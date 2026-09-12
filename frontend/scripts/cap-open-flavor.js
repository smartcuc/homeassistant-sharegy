#!/usr/bin/env node
/*
# frontend/scripts/cap-open-flavor.js
# Öffnet Android Studio für den gewählten Flavor (home vs pro)
*/

import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, "..");

const flavor = (process.argv[2] || "home").toLowerCase();
const configFile = flavor === "pro" ? "capacitor.pro.json" : "capacitor.home.json";

console.log(`[Capacitor-Flavor] Opening Android Studio for '${flavor}'...`);

const srcPath = path.join(rootDir, configFile);
const destPath = path.join(rootDir, "capacitor.config.json");

if (fs.existsSync(srcPath)) {
    fs.copyFileSync(srcPath, destPath);
}

try {
    execSync("npx cap open android", { cwd: rootDir, stdio: "inherit" });
} catch (err) {
    console.error(`[Capacitor-Flavor] Open failed:`, err.message);
    process.exit(1);
}
