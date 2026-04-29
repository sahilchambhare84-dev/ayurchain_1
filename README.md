# AyurChain 🌿

A secure, transparent herbal supply chain platform. Now unified into a single, easy-to-run application.

## 🚀 One-Click Start
1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the application**:
    ```bash
    python backend/src/app.py
    ```
3.  **Access the Portal**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## ✨ Features
- **Unified Backend**: FastAPI now serves both the API and the Frontend.
- **Smart Verification**: Real-time QR scanning with cryptographic validation.
- **Persistent Inventory**: Products are stored in Firestore and automatically re-synced.
- **Auto-QR**: QR codes are dynamically generated and re-generated as needed.

## 📸 QR Camera Scanning
AyurChain supports real-time verification using your device's camera.
- **Local**: Works automatically on `localhost`.
- **Production**: Requires **HTTPS** for camera access due to browser security policies.

## 🛠️ Configuration
- **Firebase**: The app uses `serviceAccountKey.json` in the root for Firestore.
- **Environment**: Use a `.env` file for `FIREBASE_KEY` if deploying to the cloud (e.g., Render/Heroku).

---
© 2026 AyurChain - Transparency for the Herbal World.