const express = require("express");
const router = express.Router();
const User = require("../models/User");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
//const mongoose = require("mongoose");

const SECRET = "secret123";


router.post("/register", async (req, res) => {
  try {
    const { name, email, password, imagePath, vector } = req.body;

    if (!name || !email || !password) {
      return res.status(400).json({ message: "Missing fields" });
    }

    const hash = await bcrypt.hash(password, 10);

    const user = await User.create({
      name,
      email,
      password: hash,
      imagePath: imagePath || "",  
      vector: vector || []         
    });

    res.json({ userId: user._id });

  } catch (err) {
    console.error("REGISTER ERROR FULL:", err);
    res.status(500).json({ message: err.message });
  }
});
// LOGIN
router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  const user = await User.findOne({ email });

  if (!user) return res.status(400).json({ message: "User not found" });

  const valid = await bcrypt.compare(password, user.password);

  if (!valid) return res.status(400).json({ message: "Wrong password" });

  const token = jwt.sign({ id: user._id }, SECRET);

  res.json({ token, user });
});
router.post("/update-vector", async (req, res) => {
  const { userId, vector } = req.body;

  if (!userId || !vector) {
    return res.status(400).json({ message: "Missing fields" });
  }

  try {
    await User.findByIdAndUpdate(userId, { vector });
    res.json({ message: "Vector saved" });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

module.exports = router;
