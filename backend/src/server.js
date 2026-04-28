require("dotenv").config();
const mongoose = require("mongoose");
const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const morgan = require("morgan");
const path = require("path");
const fs = require("fs");

const productRoutes = require("./routes/productRoutes");

// ─────────────────────────────────────────────────────────────
// 1. CONNECT TO MONGODB ATLAS
// ─────────────────────────────────────────────────────────────
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("🌿 MongoDB Atlas Connected"))
  .catch(err => console.log("❌ MongoDB Error:", err));

// ─────────────────────────────────────────────────────────────
// 2. CREATE REQUIRED DIRECTORIES (Render Safe)
// ─────────────────────────────────────────────────────────────
const dataDir = path.join(__dirname, "..", "data");
const uploadsDir = path.join(__dirname, "..", "uploads");

[dataDir, uploadsDir].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// ─────────────────────────────────────────────────────────────
// 3. INITIALIZE APP
// ─────────────────────────────────────────────────────────────
const app = express();

// IMPORTANT: Render assigns PORT automatically → use process.env.PORT
const PORT = process.env.PORT || 5000;

// ─────────────────────────────────────────────────────────────
// 4. MIDDLEWARE
// ─────────────────────────────────────────────────────────────
app.use(
  helmet({
    crossOriginResourcePolicy: false, // Needed for loading images
  })
);
app.use(cors());
app.use(morgan("dev"));
app.use(express.json());

// Static uploads dir
app.use("/uploads", express.static(uploadsDir));

// ─────────────────────────────────────────────────────────────
// 5. ROUTES
// ─────────────────────────────────────────────────────────────
app.use("/api/products", productRoutes);

// Health check (important for Render)
app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// ─────────────────────────────────────────────────────────────
// 6. ERROR HANDLING
// ─────────────────────────────────────────────────────────────
app.use((err, req, res, next) => {
  console.error("❌ SERVER ERROR:", err.stack);
  res.status(500).json({ success: false, error: "Internal Server Error" });
});

// ─────────────────────────────────────────────────────────────
// 7. START SERVER (Render Compatible)
// ─────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 AyurChain Backend running on port ${PORT}`);
});