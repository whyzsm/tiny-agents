#!/usr/bin/env node
/* Validate and screenshot a local consulting HTML report. */

const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = {
    mustContain: [],
    mustNotContain: [],
    desktop: "1440x1100",
    mobile: "390x844",
  };
  for (let i = 2; i < argv.length; i += 1) {
    const key = argv[i];
    const value = argv[i + 1];
    if (key === "--must-contain") {
      args.mustContain.push(value);
      i += 1;
    } else if (key === "--must-not-contain") {
      args.mustNotContain.push(value);
      i += 1;
    } else if (key.startsWith("--")) {
      args[key.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase())] = value;
      i += 1;
    }
  }
  if (!args.html || !args.outDir) {
    throw new Error("Usage: node render_check.cjs --html <file.html> --out-dir <dir> [--must-contain text] [--must-not-contain text] [--chrome /path/to/Chrome]");
  }
  return args;
}

function viewportFrom(value, fallback) {
  const [width, height] = String(value || fallback).split("x").map((n) => Number(n));
  if (!width || !height) throw new Error(`Invalid viewport: ${value}`);
  return { width, height };
}

function requirePlaywright() {
  try {
    return require("playwright");
  } catch (error) {
    throw new Error("Missing playwright package. Install or run from a workspace that has playwright available.");
  }
}

async function main() {
  const args = parseArgs(process.argv);
  const htmlPath = path.resolve(args.html);
  const outDir = path.resolve(args.outDir);
  if (!fs.existsSync(htmlPath)) {
    throw new Error(`HTML file not found: ${htmlPath}`);
  }
  fs.mkdirSync(outDir, { recursive: true });

  const html = fs.readFileSync(htmlPath, "utf8");
  const staticErrors = [];
  for (const text of args.mustContain) {
    if (!html.includes(text)) staticErrors.push(`Missing required text in source: ${text}`);
  }
  for (const text of args.mustNotContain) {
    if (html.includes(text)) staticErrors.push(`Forbidden text remains in source: ${text}`);
  }
  if (staticErrors.length) {
    for (const error of staticErrors) console.error(`ERROR: ${error}`);
    process.exit(1);
  }

  const { chromium } = requirePlaywright();
  const launchOptions = { headless: true };
  if (args.chrome) launchOptions.executablePath = args.chrome;
  const browser = await chromium.launch(launchOptions);
  const results = [];
  const viewports = [
    { name: "desktop", ...viewportFrom(args.desktop, "1440x1100") },
    { name: "mobile", ...viewportFrom(args.mobile, "390x844") },
  ];

  for (const vp of viewports) {
    const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
    const consoleErrors = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("pageerror", (err) => consoleErrors.push(err.message));
    await page.goto(`file://${htmlPath}`, { waitUntil: "load" });
    await page.screenshot({ path: path.join(outDir, `${vp.name}.png`), fullPage: true });
    const info = await page.evaluate((checks) => {
      const text = document.body.innerText;
      return {
        title: document.title,
        hasRequiredText: checks.mustContain.every((item) => text.includes(item)),
        hasForbiddenText: checks.mustNotContain.some((item) => text.includes(item)),
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        overflowX: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
        height: document.documentElement.scrollHeight,
      };
    }, { mustContain: args.mustContain, mustNotContain: args.mustNotContain });
    results.push({ viewport: vp, info, consoleErrors });
    await page.close();
  }
  await browser.close();

  const errors = [];
  for (const result of results) {
    if (!result.info.hasRequiredText) errors.push(`${result.viewport.name}: required text missing in rendered page.`);
    if (result.info.hasForbiddenText) errors.push(`${result.viewport.name}: forbidden text remains in rendered page.`);
    if (result.info.overflowX) errors.push(`${result.viewport.name}: page has horizontal overflow (${result.info.scrollWidth} > ${result.info.clientWidth}).`);
    if (result.consoleErrors.length) errors.push(`${result.viewport.name}: console errors: ${result.consoleErrors.join(" | ")}`);
  }

  const reportPath = path.join(outDir, "render-check.json");
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2), "utf8");
  if (errors.length) {
    for (const error of errors) console.error(`ERROR: ${error}`);
    console.error(`Details: ${reportPath}`);
    process.exit(1);
  }
  console.log(`OK: render check passed. Screenshots and details written to ${outDir}`);
}

main().catch((error) => {
  console.error(`ERROR: ${error.message}`);
  process.exit(1);
});
