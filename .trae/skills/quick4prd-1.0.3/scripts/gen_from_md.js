#!/usr/bin/env node
'use strict';

const path = require('path');
const {
  generateBundle,
  loadManifestEntries,
  loadProfile,
  parseCliArgs,
  resolveEntry,
} = require('./lib/common');

function printHelp() {
  console.log(`
智能体需求文档生成skill / gen_from_md.js

用法：
  /usr/local/bin/node gen_from_md.js --source /absolute/path/to/doc.md --output-dir /absolute/path/to/out
  /usr/local/bin/node gen_from_md.js --profile /absolute/path/to/profile.json
  /usr/local/bin/node gen_from_md.js --manifest /absolute/path/to/manifest.json

支持参数：
  --source        单个源 Markdown 文件路径
  --output-dir    输出目录；不传时默认使用源文件所在目录
  --basename      生成快照时使用的基础文件名；不传时默认取源文件名
  --profile       单文档 profile JSON
  --manifest      批量任务 manifest JSON（数组，或 { documents: [] }）
  --help          查看帮助
`);
}

function mergeDefined(...sources) {
  const merged = {};
  sources.forEach((source) => {
    if (!source) return;
    Object.entries(source).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        merged[key] = value;
      }
    });
  });
  return merged;
}

function buildSingleEntry(args) {
  let profile = null;
  if (args.profile) {
    profile = loadProfile(args.profile);
  }

  const merged = mergeDefined(profile ? profile.data : null, args);
  if (!merged.source) {
    throw new Error('单文档模式下必须提供 --source 或在 profile 中提供 source');
  }

  return [resolveEntry(merged, profile ? profile.dir : process.cwd())];
}

function buildManifestEntries(args) {
  const manifest = loadManifestEntries(args.manifest);
  let profile = null;
  if (args.profile) {
    profile = loadProfile(args.profile);
  }

  return manifest.documents.map((doc, index) => {
    const merged = mergeDefined(profile ? profile.data : null, doc);
    try {
      return resolveEntry(merged, manifest.dir);
    } catch (error) {
      throw new Error(`manifest 第 ${index + 1} 项无效：${error.message}`);
    }
  });
}

async function main() {
  const args = parseCliArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  const entries = args.manifest ? buildManifestEntries(args) : buildSingleEntry(args);

  console.log(`\n📄 共 ${entries.length} 个文档任务待生成：`);
  entries.forEach((entry) => {
    console.log(`   - ${path.basename(entry.sourcePath)} -> ${entry.outputDir}`);
  });
  console.log('');

  for (const entry of entries) {
    const result = await generateBundle(entry);
    console.log(`✓ ${path.basename(result.mdSnapshotPath)}`);
    console.log(`  → 版本号：${result.version}`);
    if (result.archived.length > 0) {
      result.archived.forEach((file) => console.log(`  → 已归档旧版本：${file}`));
    }
    console.log('');
  }

  console.log('✅ 完成');
}

main().catch((error) => {
  console.error(`✗ ${error.message}`);
  process.exit(1);
});
