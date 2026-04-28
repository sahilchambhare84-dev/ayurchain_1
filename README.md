# AyurChain 2.0 🌿

A secure, transparent herbal supply chain platform built with **Python**, **HTML**, and **C**.

## 🚀 Quick Preview
The project is currently running on localhost.
- **Link**: [http://localhost:8000](http://localhost:8000)

## 📸 QR Camera Scanning
AyurChain now supports real-time verification using your device's camera.
- **How to use**: Click "Scan Product QR" on the homepage and grant camera permissions.
- **Security Note**: Browser security requires **HTTPS** or **localhost** for camera access. If you are deploying this, ensure you use an SSL certificate.

## 🏗️ Architecture
- **Frontend SPA (`index.html`)**: A complete, high-fidelity experience using Tailwind CSS, Lucide Icons, and jsQR. Handles all logic, storage (localStorage), and real-time scanning.
- **Backend API (`app.py`)**: A FastAPI implementation for server-side persistence and integration.
- **Native Logic (`validator.c`)**: A C utility for high-performance product ID validation.

## 🛠️ How to Run
1. **Frontend (Recommended)**: Open `index.html` or run the provided preview server: `npx serve`.
2. **Python Backend**: `pip install -r requirements.txt` and then `python app.py`.
3. **C Utility**: `gcc validator.c -o validator`.

---
© 2026 AyurChain - Transparency for the Herbal World.