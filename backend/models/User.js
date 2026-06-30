const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
  name: String,
  email: String,
  password: String,
  role: { type: String, default: "user" },
  imagePath: String,     
  vector: [Number]       
});

module.exports = mongoose.model("User", UserSchema);
