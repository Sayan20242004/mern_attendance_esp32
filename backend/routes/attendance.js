const express = require("express");
const router = express.Router();
const Attendance = require("../models/Attendance");
const axios = require("axios");

router.post("/", async (req, res) => {
  const imageBuffer = req.body;

  try {
    const response = await axios.post(
      "http://localhost:8000/recognize",
      imageBuffer,
      {
        headers: {
          "Content-Type": "image/jpeg"
        }
      }
    );

    const userId = response.data.userId;

    if (userId) {
      await Attendance.create({ userId });
      return res.json({ message: "Attendance marked" });
    }

    res.json({ message: "No match" });

  } catch (err) {
    console.error(err.message);
    res.status(500).json({ error: err.message });
  }
});

router.get("/", async (req, res) => {
  const data = await Attendance.find().sort({ timestamp: -1 });
  res.json(data);
});

module.exports = router;
