import os
import json
import tempfile
import qrcode
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="AyurChain Producer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ───────── QR STORAGE (works on Render) ─────────
QR_DIR = os.path.join(tempfile.gettempdir(), "qrcodes")
os.makedirs(QR_DIR, exist_ok=True)

# ───────── FIREBASE ─────────
db = None
firebase_key = os.getenv("FIREBASE_KEY")
service_account_path = os.path.join(os.path.dirname(__file__), "..", "..", "serviceAccountKey.json")

try:
    if firebase_key:
        cred = credentials.Certificate(json.loads(firebase_key))
    elif os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
    else:
        cred = None
        print("FIREBASE_KEY not set and serviceAccountKey.json not found")

    if cred:
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase connected")
except Exception as e:
    print("Firebase error:", e)

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

# ───────── API STATUS ─────────
@app.get("/")
def read_root():
    return {"message": "AyurChain API is running", "status": "operational"}

# ───────── ADD PRODUCT ─────────
@app.post("/add-product")
def add_product(product: Product):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized. Check your terminal for Firebase errors.")

    try:
        # Save product (Compatibility for Pydantic v1 and v2)
        data = product.model_dump() if hasattr(product, "model_dump") else product.dict()
        
        doc_ref = db.collection("products").document()
        product_id = doc_ref.id
        doc_ref.set(data)

        # Create QR
        qr_data = product_id 
        qr_path = os.path.join(QR_DIR, f"{product_id}.png")
        qrcode.make(qr_data).save(qr_path)

        return {
            "message": "Product added successfully",
            "product_id": product_id,
            "qr_code": f"/qr/{product_id}"
        }
    except Exception as e:
        print(f"❌ ERROR SAVING PRODUCT: {e}")
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

# ───────── LIST PRODUCTS ─────────
@app.get("/products")
def list_products(producer_id: Optional[str] = None):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    try:
        query = db.collection("products")
        if producer_id:
            query = query.where("producer_id", "==", producer_id)
        
        docs = query.stream()
        return [{"id": doc.id, **doc.to_dict()} for doc in docs]
    except Exception as e:
        print(f"❌ ERROR LISTING PRODUCTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ───────── GET QR ─────────
@app.get("/qr/{product_id}")
def get_qr(product_id: str):
    if not db:
        raise HTTPException(status_code=500, detail="Firestore not initialized")

    qr_path = os.path.join(QR_DIR, f"{product_id}.png")

    if not os.path.exists(qr_path):
        # Re-generate if product exists in DB
        doc = db.collection("products").document(product_id).get()
        if doc.exists:
            qrcode.make(product_id).save(qr_path)
        else:
            raise HTTPException(status_code=404, detail="Product not found")

    return FileResponse(qr_path)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)