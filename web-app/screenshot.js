const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
  const client = await page.context().newCDPSession(page);

  try {
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
    // Wait for React + socket connect
    await page.waitForTimeout(2000);

    // Draw a few strokes on the canvas so it visibly renders.
    const canvas = await page.locator('canvas');
    const box = await canvas.boundingBox();
    const draws = [
      [0.25, 0.35, 0.55, 0.45],
      [0.55, 0.45, 0.4, 0.7],
      [0.4, 0.7, 0.7, 0.8],
      [0.3, 0.3, 0.5, 0.55],
    ];
    for (const [x0, y0, x1, y1] of draws) {
      await page.mouse.move(box.x + box.width * x0, box.y + box.height * y0);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width * x1, box.y + box.height * y1, { steps: 20 });
      await page.mouse.up();
    }

    const out = path.join(__dirname, 'screenshots');
    // 1) Main canvas (dark theme)
    await page.screenshot({ path: path.join(out, '01-main-canvas.png') });

    // 2) Metrics dashboard (bottom-right panel)
    const metrics = await page.locator('.metrics-dashboard').boundingBox();
    await page.screenshot({
      path: path.join(out, '02-metrics-dashboard.png'),
      clip: { x: metrics.x, y: metrics.y, width: metrics.width, height: metrics.height },
    });

    // 3) Theme: switch to "Light"
    const buttons = page.locator('.action-btn');
    const themeBtn = buttons.filter({ hasText: 'Theme:' });
    await themeBtn.click();
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(out, '03-theme-light.png') });

    // 4) Switch canvas background to Plain White so it's clearly visible, show full app in light theme
    const canvasBtn = buttons.filter({ hasText: 'Canvas:' });
    await canvasBtn.click(); // work till Plain White (next->Plain Black->Plain White)
    await canvasBtn.click();
    await page.waitForTimeout(400);
    await page.screenshot({ path: path.join(out, '04-themes-settings.png') });

    console.log('SCREENSHOTS DONE');
    console.log(JSON.stringify({ box, metrics }, null, 2));
  } finally {
    await browser.close();
  }
})().catch((e) => { console.error(e); process.exit(1); });
