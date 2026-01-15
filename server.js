const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
const bcrypt = require("bcrypt");
const axios = require("axios");
const fs = require("fs"); // Added for safe file reading
require("dotenv").config();
const admin = require("firebase-admin");

const app = express();
app.use(express.json());
app.use(cors());

// ✅ FIX 1: Safe Firebase Initialization (No JSON.parse path error)
try {
    const serviceAccount = JSON.parse(fs.readFileSync("./FIREBASE_SERVICE_ACCOUNT.json", "utf8"));
    admin.initializeApp({
        credential: admin.credential.cert(serviceAccount),
        databaseURL: process.env.FIREBASE_DB_URL
    });
    console.log("✅ Firebase initialized successfully");
} catch (error) {
    console.error("❌ Firebase Init Error:", error.message);
}

// ✅ FIX 2: Removed Git Merge Conflicts (Clean Logic)
const userSchema = new mongoose.Schema({
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true },
  fullname: { type: String, default: "" },
  phone: { type: String, default: "" },
  cnic: { type: String, default: "" },
  otp: String,
  otpExpiry: Date,
});
const User = mongoose.model("User", userSchema);

// ✅ FIX 3: Secure Email Logic (No hardcoded passwords)
// Using Brevo API via Environment Variables for high security
const sendEmail = async (to, subject, text) => {
  try {
    await axios.post("https://api.brevo.com/v3/smtp/email", {
      sender: { email: process.env.SENDER_EMAIL, name: "EcoSync Pro" },
      to: [{ email: to }],
      subject: subject,
      textContent: text
    }, {
      headers: { "api-key": process.env.BREVO_API_KEY }
    });
    return true;
  } catch (err) {
    console.error("Email Error:", err.message);
    return false;
  }
};

// ===================== ROUTES =====================

app.post("/api/auth/register", async (req, res) => {
  try {
    const { email, password, fullname, phone, cnic } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);
    
    const user = new User({ email, password: hashedPassword, fullname, phone, cnic });
    await user.save();

    // Syncing to Global Firebase Node
    await admin.database().ref("users/" + user._id).set({
      profile: { fullname, email, phone }
    });

    res.json({ success: true, message: "User Registered Globally" });
  } catch (err) {
    res.status(500).json({ success: false, error: "Database Sync Error" });
  }
});

// ✅ FIX 4: Secure MongoDB Connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => {
    const port = process.env.PORT || 3000;
    app.listen(port, () => console.log(`🚀 Stable System Online on port ${port}`));
  })
  .catch(err => console.error("❌ Node Connection Failed:", err.message));