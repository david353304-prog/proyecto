"use strict";

const path = require("node:path");

module.exports = path.resolve(
    __dirname,
    "../.venv",
    process.platform === "win32" ? "Scripts/python.exe" : "bin/python"
);
