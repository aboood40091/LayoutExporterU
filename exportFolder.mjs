// Utility script to batch export an entire folder of layouts.
//! This script supresses warnings from the main script.
//
// This script expects a folder with the following structure as input: (This is the structure provided by SwitchToolbox when extracting lyt_root)
// - <inputFolder>/
//   - anim/ (.bflan files)
//   - blyt/ (.bflyt files)
//   - timg/ (.bflim files)
//
// The output files will be placed in <inputFolder>/flyt/
// Remember to place a folder named "Fonts" in the /flyt/ folder containing the required fonts in BFFNT format.

import fs from 'fs';
import { execSync } from 'child_process';

const inputFolder = process.argv[2];
if (!inputFolder) {
    console.log('Usage: node exportFolder.mjs <inputFolder>');
    process.exit(1);
}

if (!fs.existsSync(`${inputFolder}/flyt`)) fs.mkdirSync(`${inputFolder}/flyt`);

fs.readdirSync(`${inputFolder}/blyt`).map(lyt => [`blyt/${lyt}`, `flyt/${lyt.slice(0, -6)}.flyt`]).forEach(([bflyt, flyt]) => {
    console.log(`Converting: ${inputFolder}/${bflyt} -> ${inputFolder}/${flyt}`);
    execSync(`py main.py ${inputFolder}/${bflyt} ${inputFolder}/${flyt}`);
});
