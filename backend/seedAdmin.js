require("dotenv").config();
const mongoose = require("mongoose");
const bcrypt = require("bcryptjs");
const User = require("./models/User");

const MONGO_URI = process.env.MONGO_URI;

async function seedAdmin() {
  try {
    await mongoose.connect(MONGO_URI);
    console.log("MongoDB Connected");

    const existing = await User.findOne({ email: "admin@mail.com" });

    if (existing) {
      console.log("Admin already exists");
      process.exit();
    }

    const hash = await bcrypt.hash("123456", 10);

    await User.create({
      name: "Admin",
      email: "admin@mail.com",
      password: hash,
      role: "admin"
    });

    console.log("Admin created successfully");
    process.exit();

  } catch (err) {
    console.error(err);
    process.exit(1);
  }
}

seedAdmin();