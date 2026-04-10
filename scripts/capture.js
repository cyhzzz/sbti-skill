#!/usr/bin/env node

const path = require('path');

async function main() {
  const args = process.argv.slice(2);
  const htmlPath = args[0];
  const outputPath = args[1];
  const width = parseInt(args[2]) || 1200;
  const height = parseInt(args[3]) || 1600;
  const fullpage = args[4] === 'fullpage';

  if (!htmlPath || !outputPath) {
    console.error('Usage: node capture.js <html> <png> [width] [height] [fullpage]');
    process.exit(1);
  }

  let chromium;
  try {
    chromium = require('playwright').chromium;
  } catch {
    console.error('Playwright not found. Run: npx playwright install chromium');
    process.exit(1);
  }

  const browser = await chromium.launch();
  const page = await browser.newPage();

  // Collect image loading errors
  const imgErrors = [];
  page.on('pageerror', err => {
    // Ignore non-image errors
  });
  page.on('requestfailed', req => {
    const url = req.url();
    if (/\.(png|jpg|jpeg|gif|svg|ico)$/i.test(url)) {
      imgErrors.push(url);
    }
  });

  await page.setViewportSize({ width, height: fullpage ? 800 : height });

  const fileUrl = 'file://' + path.resolve(htmlPath);
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);

  // Verify critical images (logo) loaded
  const logoResult = await page.evaluate(() => {
    const imgs = document.querySelectorAll('img');
    const results = [];
    for (const img of imgs) {
      if (!img.complete || img.naturalWidth === 0) {
        results.push({ src: img.src, failed: true });
      }
    }
    return results;
  });

  const allImgErrors = [...imgErrors, ...logoResult];
  if (allImgErrors.length > 0) {
    console.warn('WARN: Some images failed to load:');
    allImgErrors.forEach(e => console.warn('  - ' + (e.src || e)));
    // Continue anyway — non-fatal
  } else {
    console.log('INFO: All images loaded successfully');
  }

  if (fullpage) {
    const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
    await page.setViewportSize({ width, height: bodyHeight });
    await page.waitForTimeout(300);
    await page.screenshot({
      path: path.resolve(outputPath),
      type: 'png',
      clip: { x: 0, y: 0, width, height: bodyHeight }
    });
  } else {
    await page.screenshot({
      path: path.resolve(outputPath),
      type: 'png',
      clip: { x: 0, y: 0, width, height }
    });
  }

  await browser.close();
  console.log('OK: ' + path.resolve(outputPath));
}

main().catch(err => {
  console.error(err.message);
  process.exit(1);
});
