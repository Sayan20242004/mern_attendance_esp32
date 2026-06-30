const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
  name: String,
  email: String,
  password: String,
  role: { type: String, default: "user" },
  imagePath: String,     // optional: path/URL to stored profile image
  vector: [Number]       // store Python-generated vector
});

module.exports = mongoose.model("User", UserSchema);