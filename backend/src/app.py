import os
import json
import tempfile
import qrcode
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# ── INITIALIZATION ─────────────────────────

app = FastAPI(title="AyurChain Producer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── STATIC + QR DIRECTORY (FIXED FOR RENDER) ─────────────────────────

# Use temp folder (safe on Render)
QR_DIR = os.path.join(tempfile.gettempdir(), "qrcodes")
os.makedirs(QR_DIR, exist_ok=True)

# Serve frontend files
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ── FIREBASE SETUP ─────────────────────────

SERVICE_ACCOUNT_PATH = "serviceAccountKey.json"

if os.path.exists(SERVICE_ACCOUNT_PATH):
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized from file")
elif os.getenv("FIREBASE_KEY"):
    firebase_data = json.loads(os.getenv("FIREBASE_KEY"))
    cred = credentials.Certificate(firebase_data)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase initialized from environment variable")
else:
    print("Firebase not configured")
    db = None

# ── MODEL ─────────────────────────

class Product(BaseModel):
    name: str
    description: Optional[str] = ""
    producer_name: str
    producer_id: str
    farmer_name: Optional[str] = ""
    location: Optional[str] = ""
    harvest_date: Optional[str] = ""
    status: Optional[str] = "Verified"

# ── ADD PRODUCT ─────────────────────────

@app.post("/add-product")
def add_product(product: Product):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    data = product.model_dump()

    # Create Firestore document
    doc_ref = db.collection("products").document()
    product_id = doc_ref.id
    doc_ref.set(data)

    # Create QR link
    BASE_URL = "https://ayurchain-1.onrender.com"
    qr_data = f"{BASE_URL}/static/index.html?id={product_id}"

    # Generate QR
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join(QR_DIR, f"{product_id}.png")
    qr_img.save(qr_path)

    print("QR saved at:", qr_path)

    return {
        "message": "Product added successfully",
        "product_id": product_id,
        "qr_code": f"/qr/{product_id}"
    }

# ── GET PRODUCT ─────────────────────────

@app.get("/product/{product_id}")
def get_product(product_id: str):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    doc = db.collection("products").document(product_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")

    return doc.to_dict()

# ── UPDATE PRODUCT ─────────────────────────

@app.put("/product/{product_id}")
def update_product(product_id: str, product: Product):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    doc_ref = db.collection("products").document(product_id)

    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Product not found")

    doc_ref.update(product.model_dump())

    return {"message": "Product updated successfully"}

# ── DELETE PRODUCT ─────────────────────────

@app.delete("/product/{product_id}")
def delete_product(product_id: str):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    db.collection("products").document(product_id).delete()

    qr_path = os.path.join(QR_DIR, f"{product_id}.png")
    if os.path.exists(qr_path):
        os.remove(qr_path)

    return {"message": "Product deleted successfully"}

# ── GET QR ─────────────────────────

@app.get("/qr/{product_id}")
def get_qr(product_id: str):
    qr_path = os.path.join(QR_DIR, f"{product_id}.png")

    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="QR not found")

    return FileResponse(qr_path)

# ── ROOT ─────────────────────────

@app.get("/")
def root():
    return FileResponse("static/index.html")