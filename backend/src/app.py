import os
import json
import tempfile
import qrcode
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AyurChain Producer API")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────── QR STORAGE (Render safe) ─────────
QR_DIR = os.path.join(tempfile.gettempdir(), "qrcodes")
os.makedirs(QR_DIR, exist_ok=True)

# ───────── FIREBASE ─────────
db = None
firebase_key = os.getenv("FIREBASE_KEY")

try:
    if firebase_key:
        cred = credentials.Certificate(json.loads(firebase_key))
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase connected")
    else:
        print("❌ FIREBASE_KEY not set")
except Exception as e:
    print("❌ Firebase error:", e)

# ───────── MODEL ─────────
class Product(BaseModel):
    name: str
    description: Optional[str] = ""
    producer_name: str
    producer_id: str
    farmer_name: Optional[str] = ""
    location: Optional[str] = ""
    harvest_date: Optional[str] = ""
    status: Optional[str] = "Verified"

# ───────── ROOT ─────────
@app.get("/")
def root():
    return {"message": "AyurChain API running"}

# ───────── ADD PRODUCT ─────────
@app.post("/add-product")
def add_product(product: Product):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    try:
        data = product.model_dump() if hasattr(product, "model_dump") else product.dict()

        doc_ref = db.collection("products").document()
        product_id = doc_ref.id
        doc_ref.set(data)

        # QR content → link to product API
        BASE_URL = "https://ayurchain-1.onrender.com"
        qr_data = f"{BASE_URL}/static/index.html?id={product_id}"

        qr_path = os.path.join(QR_DIR, f"{product_id}.png")
        qrcode.make(qr_data).save(qr_path)

        return {
            "message": "Product added successfully",
            "product_id": product_id,
            "qr_code": f"/qr/{product_id}"
        }

    except Exception as e:
        print("❌ ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

# ───────── GET PRODUCT ─────────
@app.get("/product/{product_id}")
def get_product(product_id: str):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    doc = db.collection("products").document(product_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Product not found")

    return doc.to_dict()

# ───────── GET QR ─────────
@app.get("/qr/{product_id}")
def get_qr(product_id: str):
    qr_path = os.path.join(QR_DIR, f"{product_id}.png")

    if not os.path.exists(qr_path):
        raise HTTPException(status_code=404, detail="QR not found")

    return FileResponse(qr_path)