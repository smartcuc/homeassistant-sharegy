#!/usr/bin/env node
/*
# frontend/scripts/cap-sync-flavor.js
# Synchronisiert Capacitor mit dem gewählten Flavor (home vs pro)
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

console.log(`[Capacitor-Flavor] Selecting flavor: '${flavor}' (Source: ${configFile})...`);

const srcPath = path.join(rootDir, configFile);
const destPath = path.join(rootDir, "capacitor.config.json");

if (!fs.existsSync(srcPath)) {
    console.error(`[Capacitor-Flavor] Error: Config file '${srcPath}' not found!`);
    process.exit(1);
}

// Copy selected config to capacitor.config.json
fs.copyFileSync(srcPath, destPath);
console.log(`[Capacitor-Flavor] Updated capacitor.config.json for flavor '${flavor}'.`);

// Execute cap sync android
try {
    console.log(`[Capacitor-Flavor] Running 'npx cap sync android'...`);
    execSync("npx cap sync android", { cwd: rootDir, stdio: "inherit" });
    console.log(`[Capacitor-Flavor] Successfully synchronized '${flavor}' target!`);
} catch (err) {
    console.error(`[Capacitor-Flavor] Sync failed:`, err.message);
    process.exit(1);
}
