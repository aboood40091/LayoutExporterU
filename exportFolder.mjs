// Utility script to batch export an entire folder of layouts.
//
// This script expects a folder with the following structure as input: (This is the structure provided by SwitchToolbox when extracting lyt_root)
// - <inputFolder>/
//   - anim/ (.bflan files)
//   - blyt/ (.bflyt files)
//   - timg/ (.bflim files)
//
// The input folder must be inside a folder named Layouts in the same folder as this script.
// The output will be placed in Layouts/<inputFolder>/flyt/
// Remember to place a folder named Fonts in the /flyt/ folder containing the required fonts.

import fs from 'fs';
import { execSync } from 'child_process';

const inputFolder = process.argv[2];
if (!inputFolder) {
    console.log('Usage: node exportFolder.mjs <inputFolder>');
    process.exit(1);
}

if (!fs.existsSync(`Layouts/${inputFolder}/flyt`)) fs.mkdirSync(`Layouts/${inputFolder}/flyt`);

fs.readdirSync(`Layouts/${inputFolder}/blyt`).map(lyt => [`blyt/${lyt}`, `flyt/${lyt.slice(0, -6)}.flyt`]).forEach(([bflyt, flyt]) => {
    console.log(`Converting: ${inputFolder}/${bflyt} -> ${inputFolder}/${flyt}`);
    execSync(`py main.py Layouts/${inputFolder}/${bflyt} Layouts/${inputFolder}/${flyt}`);
});
