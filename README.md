# Polymarket Pipeline V2

An AI-powered breaking news detector that classifies events against prediction markets and trades automatically when it finds edge.

```text
Breaking News (Twitter / Telegram / RSS)
        -> (< 5 seconds)
Match to niche markets (< $500K volume)
        ->
Gemini Classification: bullish / bearish / neutral + materiality
        ->
Edge detection + quarter-Kelly sizing
        ->
Instant execution -> SQLite log -> calibration tracking
```

## What Changed From V1

V1 scraped RSS feeds, asked the model for a probability estimate, and competed on high-volume markets where every bot already operates.

V2 inverts all three:
- **Speed**: Real-time Twitter and Telegram streams instead of stale RSS.
- **Classification**: Gemini classifies "bullish or bearish?" instead of trying to be a direct probability estimator.
- **Niche markets**: Only trades markets under $500K volume where the crowd is smaller and slower.

## Setup

### One-command setup

```bash
git clone https://github.com/brodyautomates/polymarket-pipeline.git
cd polymarket-pipeline
bash setup.sh
```

### Manual setup

```bash
git clone https://github.com/brodyautomates/polymarket-pipeline.git
cd polymarket-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your keys to `.env`:

```env
GEMINI_API_KEY=your-gemini-api-key
CLASSIFICATION_MODEL=gemini-3-flash-preview
SCORING_MODEL=gemini-3.1-pro-preview
TWITTER_BEARER_TOKEN=
TELEGRAM_BOT_TOKEN=
POLYMARKET_API_KEY=
```

Verify the setup:

```bash
python cli.py verify
```

## How To Use

### V2: event-driven pipeline

```bash
python cli.py watch
python cli.py watch --live
```

The `watch` command runs indefinitely. It connects to the configured news sources, matches headlines to niche Polymarket markets, classifies each event with Gemini, and executes trades when it finds edge.

### V1: synchronous pipeline

```bash
python cli.py run
python cli.py run --max 15 --hours 12
```

### Other commands

| Command | What it does |
|---|---|
| `python cli.py dashboard` | Live terminal dashboard |
| `python cli.py backtest` | Backtest against resolved markets |
| `python cli.py calibrate` | Classification accuracy report |
| `python cli.py niche` | Browse niche markets |
| `python cli.py verify` | Check API keys and connections |
| `python cli.py scrape` | Test the news scraper |
| `python cli.py markets` | Browse all active markets |
| `python cli.py trades` | View trade log |
| `python cli.py stats` | Performance, latency, and calibration stats |

## Architecture

```text
news_stream.py      Real-time news: Twitter API v2, Telegram, RSS fallback
market_watcher.py   Polymarket WebSocket: live prices, niche filter, momentum
classifier.py       Gemini classification: bullish / bearish / neutral + materiality
matcher.py          Routes breaking news to relevant markets
edge.py             Edge detection + Kelly sizing
executor.py         Trade execution: dry-run + live CLOB orders
pipeline.py         Event-driven orchestrator
calibrator.py       Tracks classification accuracy over time
backtest.py         Historical replay for strategy validation
logger.py           SQLite logging and calibration tracking
config.py           API keys, thresholds, and model settings
dashboard.py        Live terminal dashboard
cli.py              Command-line interface
```

## How It Works

1. News detection: Real-time streams from Twitter, Telegram, and RSS fallback feed the pipeline.
2. Market matching: Each headline is matched to active niche markets by keyword overlap.
3. Classification: Gemini is asked whether the news is bullish, bearish, or irrelevant to the market question, plus how material it is.
4. Edge detection: Signals are generated only when direction, materiality, and price room all line up.
5. Execution: Dry-run by default. Live mode places orders via the Polymarket CLOB API.
6. Calibration: As markets resolve, the system tracks whether classifications were correct.

## Configuration

| Setting | Default | What it does |
|---|---|---|
| `DRY_RUN` | `true` | Set to `false` for live trading |
| `MAX_BET_USD` | `25` | Maximum single bet |
| `DAILY_LOSS_LIMIT_USD` | `100` | Pipeline halts if breached |
| `EDGE_THRESHOLD` | `0.10` | Minimum edge to trigger trade |
| `MAX_VOLUME_USD` | `500000` | Only trade markets below this volume |
| `MIN_VOLUME_USD` | `1000` | Skip dead markets |
| `MATERIALITY_THRESHOLD` | `0.6` | Minimum materiality to act on |
| `SPEED_TARGET_SECONDS` | `5` | Target news-to-trade latency |
| `CLASSIFICATION_MODEL` | `gemini-3-flash-preview` | Model used for headline classification |
| `SCORING_MODEL` | `gemini-3.1-pro-preview` | Model used for V1 scoring |

## Safety

- Dry-run mode is on by default.
- Single-bet size is capped at $25.
- Daily exposure is capped at $100 by default.
- Quarter-Kelly sizing is used for position sizing.
- Niche market filtering avoids the most competitive markets.
- Calibration tracking helps catch model drift over time.

## Disclaimer

This project is for entertainment and educational purposes only. It is not financial advice. Prediction market trading carries significant risk, and you can lose money.
