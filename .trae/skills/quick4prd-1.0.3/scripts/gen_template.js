#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const {
  ensureDir,
  generateBundle,
  loadProfile,
  normalizePath,
  parseCliArgs,
  replaceTokens,
  sanitizeFileStem,
  todayIso,
} = require('./lib/common');

function printHelp() {
  console.log(`
智能体需求文档生成skill / gen_template.js

用法：
  /usr/local/bin/node gen_template.js --output-dir /absolute/path/to/doc --basename 示例项目-用户管理功能设计 --title 用户管理功能设计
  /usr/local/bin/node gen_template.js --profile /absolute/path/to/profile.json

支持参数：
  --output-dir     输出目录（必填，除非 profile 内已提供）
  --basename       源文件基础名，例如：示例项目-用户管理功能设计
  --title          文档标题，例如：用户管理功能设计
  --system         所属系统
  --project        所属项目
  --document-code  文档编号
  --owner          编制人
  --created-date   编制日期，默认今天
  --doc-version    文档版本，默认 v0.1
  --template       自定义模板 Markdown 路径
  --profile        profile JSON 路径
  --force          若源文件已存在则覆盖
  --help           查看帮助
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

function buildValues(config) {
  const createdDate = config.createdDate || todayIso();
  const title = config.title || config.documentTitle || '示例功能设计';
  const baseName = sanitizeFileStem(config.basename || config.baseName || title);

  return {
    documentTitle: title,
    projectName: config.project || config.projectName || '示例项目',
    systemName: config.system || config.systemName || '示例管理平台',
    documentCode: config.documentCode || 'PRD-XXX-2026-001',
    docVersion: config.docVersion || 'v0.1',
    createdDate,
    owner: config.owner || '待补充',
    moduleName: config.moduleName || '待补充模块',
    menuPath: config.menuPath || '一级菜单 → 二级菜单 → 功能页面',
    baseName,
  };
}

async function main() {
  const args = parseCliArgs(process.argv.slice(2));
  if (args.help) {
    printHelp();
    return;
  }

  let profile = null;
  if (args.profile) {
    profile = loadProfile(args.profile);
  }

  const config = mergeDefined(profile ? profile.data : null, args);
  const values = buildValues(config);
  const outputDir = normalizePath(config.outputDir, profile ? profile.dir : process.cwd());
  if (!outputDir) {
    throw new Error('缺少 outputDir，请通过 --output-dir 或 profile 提供');
  }

  const templatePath = normalizePath(
    config.template || path.join(__dirname, '..', 'references', '通用需求文档模板.md'),
    profile ? profile.dir : process.cwd(),
  );

  if (!fs.existsSync(templatePath)) {
    throw new Error(`找不到模板文件：${templatePath}`);
  }

  ensureDir(outputDir);
  const sourcePath = path.join(outputDir, `${values.baseName}.md`);

  if (fs.existsSync(sourcePath) && !config.force) {
    throw new Error(`源文件已存在：${sourcePath}。如需覆盖，请追加 --force`);
  }

  const template = fs.readFileSync(templatePath, 'utf8');
  const content = replaceTokens(template, values);
  fs.writeFileSync(sourcePath, content, 'utf8');

  console.log(`✓ 已创建源文件：${sourcePath}`);

  const result = await generateBundle({
    sourcePath,
    outputDir,
    baseName: values.baseName,
    backupDirName: config.backupDirName || 'backup',
  });

  console.log(`✓ ${path.basename(result.mdSnapshotPath)}`);
  console.log(`  → 版本号：${result.version}`);
  console.log('✅ 完成');
}

main().catch((error) => {
  console.error(`✗ ${error.message}`);
  process.exit(1);
});
