// Capture d'écran d'une page avec Chromium (Playwright).
// Usage : node shot.js <url ou fichier> <sortie.png> [largeur] [hauteur] [fullPage=0|1]
const { chromium } = require("playwright");

(async () => {
  const [target, out, w = "1440", h = "900", full = "0"] = process.argv.slice(2);
  const isLocal = /^(file:|https?:\/\/(127\.0\.0\.1|localhost))/.test(process.argv[2]) || !process.argv[2].startsWith("http");
  const proxy = isLocal ? null : (process.env.HTTPS_PROXY || process.env.https_proxy);
  const browser = await chromium.launch(proxy ? { proxy: { server: proxy } } : {});
  const context = await browser.newContext({
    viewport: { width: parseInt(w, 10), height: parseInt(h, 10) },
    deviceScaleFactor: 1,
    ignoreHTTPSErrors: true,
    locale: "fr-CH",
    reducedMotion: process.env.SHOT_MOTION || "reduce",
  });
  const page = await context.newPage();
  const url = target.startsWith("http") ? target : "file://" + require("path").resolve(target);
  await page.goto(url, { waitUntil: "load", timeout: 60000 });
  if (full === "1") {
    await page.evaluate(async () => {
      for (let y = 0; y < document.documentElement.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
      window.scrollTo(0, 0);
    });
  }
  await page.waitForTimeout(1500);
  await page.screenshot({ path: out, fullPage: full === "1" });
  await browser.close();
  console.log("écrit", out);
})().catch((e) => { console.error(e); process.exit(1); });
