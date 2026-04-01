# I Built an AI That Detects Breaking News and Front-Runs Prediction Markets

## HOOK (0-3s)

**SCREEN:** Dashboard running. Trades flowing. Green on black.

"I built an AI that detects breaking news and front-runs prediction markets in under 5 seconds."

---

## THE PROBLEM (3-12s)

**SCREEN:** Show a slow RSS feed refresh. Then show a Polymarket chart that already moved.

"Most trading bots scrape RSS feeds. By the time a headline hits RSS, the market has already moved. You're trading 30 minutes behind."

"And they ask Claude 'what's the probability?' — that's the wrong question. LLMs aren't calibrated probability estimators. Not against efficient markets."

---

## THE FIX (12-25s)

**SCREEN:** Show the V2 pipeline flow. Twitter stream → classifier → niche market → trade.

"So I rebuilt it from scratch. Three changes."

"One — real-time Twitter stream instead of stale RSS. News hits us in seconds, not minutes."

"Two — I stopped asking Claude for probabilities. Instead I ask: does this headline make the market more likely to resolve yes or no? That's a classification task. LLMs are actually good at that."

"Three — I only trade niche markets under $500K volume. Small crowds. Slow to reprice. That's where the edge is."

---

## THE CLASSIFIER (25-35s)

**SCREEN:** Close-up on a signal. Show the headline, the market question, direction: BULLISH, materiality: 0.82.

"Here's what it looks like. Breaking headline comes in from Twitter. Claude reads it and says — bullish, materiality 0.82. That means this news is highly material to the market outcome."

"The market is priced at 0.45. Claude says bullish with high conviction. That's the signal."

"News to trade in under 5 seconds."

---

## THE NICHE FILTER (35-42s)

**SCREEN:** Show `python cli.py niche` output — the 24 niche markets.

"I'm not competing on 'Will Trump win?' — that market has $12 million in volume and a hundred bots. Zero edge."

"I'm trading this." *Point at a niche market.* "$98K volume. Small crowd. When news drops that moves this market — I'm first."

---

## THE BACKTEST (42-50s)

**SCREEN:** Show `python cli.py backtest` output with results.

"But I don't just trust it. There's a built-in backtest engine. It replays resolved markets through the classifier and tells you if the strategy actually works before you risk a dollar."

"And a calibration tracker that measures accuracy over time. If it drops below 55% — it auto-pauses."

---

## THE STACK (50-58s)

**SCREEN:** Quick flash of the file structure.

"The whole thing is Python. Event-driven with asyncio. Twitter WebSocket for news. Polymarket WebSocket for prices. Claude Haiku for classification — fast and cheap."

"16 files. One command to set up."

---

## CTA (58-65s)

**SCREEN:** Dashboard running. Or face cam.

"I'm giving away the full pipeline. Every file. Setup guide. Backtest engine. One command to install."

"DM me the word PIPELINE and I'll send you the repo."
