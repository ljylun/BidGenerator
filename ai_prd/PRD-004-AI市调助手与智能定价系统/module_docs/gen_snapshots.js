'use strict';

const fs = require('fs');
const path = require('path');

const docsDir = __dirname;
const manifestPath = path.join(docsDir, 'prd004.manifest.json');
const profilePath = path.join(docsDir, 'prd004-batch.profile.json');

// Load manifest
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));
// Load profile
const profile = JSON.parse(fs.readFileSync(profilePath, 'utf-8'));

const outputDir = profile.outputDir || docsDir;
const backupDirName = profile.backupDirName || 'backup';

// Ensure output dir exists
if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
// Ensure backup dir exists
const backupDir = path.join(outputDir, backupDirName);
if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

function extractVersion(content) {
  // Try to find version from doc info table: | 文档版本 | v0.1 |
  const match = content.match(/\|\s*文档版本\s*\|\s*(v[\d.]+)\s*\|/);
  return match ? match[1] : 'v0.1';
}

function archiveOldSnapshot(baseName, version) {
  const oldFile = path.join(outputDir, `${baseName}_${version}.md`);
  if (fs.existsSync(oldFile)) {
    const backupFile = path.join(backupDir, `${baseName}_${version}.md`);
    fs.copyFileSync(oldFile, backupFile);
    fs.unlinkSync(oldFile);
    console.log(`  Archived: ${baseName}_${version}.md -> ${backupDirName}/`);
  }
}

let success = 0;
let failed = 0;

for (const doc of manifest.documents) {
  const sourceFile = path.join(docsDir, doc.sourceFile);
  
  if (!fs.existsSync(sourceFile)) {
    console.error(`  SKIP (not found): ${doc.sourceFile}`);
    failed++;
    continue;
  }

  const content = fs.readFileSync(sourceFile, 'utf-8');
  const version = extractVersion(content);
  const baseName = doc.baseName;
  const snapshotName = `${baseName}_${version}.md`;
  const snapshotPath = path.join(outputDir, snapshotName);

  try {
    // Archive old snapshot if exists
    archiveOldSnapshot(baseName, version);
    
    // Write new snapshot
    fs.copyFileSync(sourceFile, snapshotPath);
    console.log(`  OK: ${doc.docCode} -> ${snapshotName}`);
    success++;
  } catch (err) {
    console.error(`  FAIL: ${doc.docCode} - ${err.message}`);
    failed++;
  }
}

console.log(`\nDone. Success: ${success}, Failed: ${failed}`);
console.log(`Output: ${outputDir}`);
console.log(`Backup: ${backupDir}`);
