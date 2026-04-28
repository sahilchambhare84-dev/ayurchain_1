import os
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

# Ensure folders exist BEFORE mounting
QR_DIR = "static/qrcodes"
os.makedirs(QR_DIR, exist_ok=True)

# Mount static
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── FIREBASE SETUP ─────────────────────────

FIREBASE_KEY = "serviceAccountKey.json"
db = None

try:
    if os.path.exists(FIREBASE_KEY):
        cred = credentials.Certificate(FIREBASE_KEY)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase connected")
    else:
        print("❌ Firebase key not found")
except Exception as e:
    print("🔥 Firebase init error:", e)
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

    doc_ref = db.collection("products").document()
    product_id = doc_ref.id

    doc_ref.set(data)

    # QR LINK (IMPORTANT)
    qr_data = f"http://10.13.22.92:8000/static/index.html?id={product_id}"

    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join(QR_DIR, f"{product_id}.png")
    qr_img.save(qr_path)

    return {
        "message": "Product added successfully",
        "product_id": product_id,
        "qr_code": f"/static/qrcodes/{product_id}.png"
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
    return {"message": "API running", "docs": "/docs"}