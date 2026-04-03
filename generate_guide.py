#!/usr/bin/env python3
"""Generate the Polymarket Pipeline Setup Guide PDF."""
from __future__ import annotations

from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
import sys

# --- Colors ---
BLACK = HexColor("#0A0A0A")
GREEN = HexColor("#00FF41")
CYAN = HexColor("#00E5FF")
DIM_GREEN = HexColor("#1A3A1A")
DARK_PANEL = HexColor("#111111")
PANEL_BORDER = HexColor("#1C3D1C")
WHITE = HexColor("#E0E0E0")
MUTED = HexColor("#777777")
YELLOW = HexColor("#FFD600")
RED = HexColor("#FF4444")

W, H = letter  # 612 x 792


def draw_bg(c):
    c.setFillColor(BLACK)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_panel(c, x, y, w, h, border_color=PANEL_BORDER):
    c.setFillColor(DARK_PANEL)
    c.setStrokeColor(border_color)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=1)


def text(c, x, y, txt, color=WHITE, size=10, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, txt)


def text_wrap(c, x, y, txt, color=WHITE, size=10, font="Helvetica", max_width=480, line_height=14):
    """Draw text with word wrapping. Returns new y position."""
    c.setFillColor(color)
    c.setFont(font, size)
    words = txt.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if c.stringWidth(test, font, size) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    for line in lines:
        if y < 60:
            c.showPage()
            draw_bg(c)
            y = H - 60
        c.setFillColor(color)
        c.setFont(font, size)
        c.drawString(x, y, line)
        y -= line_height
    return y


def code_block(c, x, y, lines, width=480):
    """Draw a code block with dark background."""
    line_h = 14
    padding = 10
    block_h = len(lines) * line_h + padding * 2

    if y - block_h < 50:
        c.showPage()
        draw_bg(c)
        y = H - 60

    draw_panel(c, x - 8, y - block_h + 4, width + 16, block_h, border_color=HexColor("#2A2A2A"))

    cy = y - padding
    for line in lines:
        c.setFillColor(GREEN)
        c.setFont("Courier", 9)
        c.drawString(x, cy, line)
        cy -= line_h

    return y - block_h - 8


def heading(c, x, y, txt, color=GREEN, size=18):
    if y < 100:
        c.showPage()
        draw_bg(c)
        y = H - 60
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, txt)
    # Underline
    tw = c.stringWidth(txt, "Helvetica-Bold", size)
    c.setStrokeColor(color)
    c.setLineWidth(0.5)
    c.line(x, y - 4, x + tw, y - 4)
    return y - 30


def subheading(c, x, y, txt, color=CYAN, size=13):
    if y < 80:
        c.showPage()
        draw_bg(c)
        y = H - 60
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", size)
    c.drawString(x, y, txt)
    return y - 22


def bullet(c, x, y, txt, color=WHITE, size=10, max_width=460):
    if y < 60:
        c.showPage()
        draw_bg(c)
        y = H - 60
    c.setFillColor(GREEN)
    c.setFont("Helvetica", size)
    c.drawString(x, y, ">")
    y = text_wrap(c, x + 14, y, txt, color=color, size=size, max_width=max_width)
    return y - 2


def separator(c, y):
    c.setStrokeColor(HexColor("#222222"))
    c.setLineWidth(0.5)
    c.line(50, y, W - 50, y)
    return y - 15


def build_pdf(output_path: str):
    c = canvas.Canvas(output_path, pagesize=letter)

    # ===================== PAGE 1: Cover =====================
    draw_bg(c)

    # Top accent line
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.line(50, H - 40, W - 50, H - 40)

    # Title
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 36)
    c.drawString(50, H - 120, "POLYMARKET")
    c.drawString(50, H - 165, "PIPELINE")

    # Subtitle
    c.setFillColor(CYAN)
    c.setFont("Helvetica", 14)
    c.drawString(50, H - 200, "SETUP GUIDE")

    # Tagline
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 11)
    c.drawString(50, H - 240, "An event-driven AI pipeline that monitors breaking news in real time,")
    c.drawString(50, H - 256, "classifies market impact using Claude, and trades niche Polymarket")
    c.drawString(50, H - 272, "markets automatically when it finds edge.")

    # Pipeline diagram
    y = H - 330
    draw_panel(c, 50, y - 50, W - 100, 55)
    c.setFillColor(GREEN)
    c.setFont("Courier", 10)
    c.drawString(70, y - 20, "Twitter/Telegram/RSS  -->  Classification  -->  Niche Markets  -->  Trade")
    c.setFillColor(MUTED)
    c.setFont("Courier", 8)
    c.drawString(70, y - 38, "real-time streams       bullish/bearish/neutral   < $500K volume    dry-run default")

    # What you get
    y = H - 430
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "WHAT YOU GET")
    y -= 28

    items = [
        "Real-time news streams — Twitter API v2, Telegram, RSS fallback",
        "Claude classification: bullish / bearish / neutral + materiality score",
        "Niche market filter — only trades markets under $500K volume",
        "Edge detection + quarter-Kelly sizing (classification-based, not probability guessing)",
        "Trade execution via Polymarket CLOB API (dry-run by default)",
        "Bloomberg Terminal-style live dashboard",
        "Backtest engine + calibration tracking — measure if your edge is real",
        "Full SQLite audit trail — every trade, classification, and latency log",
    ]
    for item in items:
        y = bullet(c, 60, y, item)

    # Footer
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.line(50, 60, W - 50, 60)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 44, "github.com/brodyautomates/polymarket-pipeline")
    c.drawRightString(W - 50, 44, "@brodyautomates")

    c.showPage()

    # ===================== PAGE 2: Prerequisites =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "1. PREREQUISITES")
    y -= 5

    y = subheading(c, 50, y, "What You Need Before Starting")
    y -= 5

    y = bullet(c, 60, y, "Python 3.9 or higher installed on your machine")
    y = bullet(c, 60, y, "An Anthropic API key (get one at console.anthropic.com)")
    y = bullet(c, 60, y, "A terminal app (Terminal, iTerm2, Ghostty, Warp, etc.)")
    y = bullet(c, 60, y, "Git installed (to clone the repo)")

    y -= 10
    y = subheading(c, 50, y, "Optional (for enhanced features)")
    y -= 5

    y = bullet(c, 60, y, "Twitter Bearer Token — enables real-time filtered stream (twitter.developer.com)")
    y = bullet(c, 60, y, "Telegram Bot Token + channel IDs — enables Telegram monitoring")
    y = bullet(c, 60, y, "NewsAPI key — broader RSS coverage (newsapi.org)")
    y = bullet(c, 60, y, "Polymarket API credentials — only needed for live trading")
    y = bullet(c, 60, y, "Python 3.9.10+ — required for the Polymarket CLOB trading client")

    y -= 15
    y = separator(c, y)

    # Check Python version
    y = subheading(c, 50, y, "Check Your Python Version")
    y -= 5

    y = code_block(c, 60, y, [
        "python3 --version",
        "",
        "# If below 3.9, install via Homebrew:",
        "brew install python@3.12",
    ])

    y -= 10
    y = text_wrap(c, 50, y, "If you see Python 3.9.x or higher, you're good. The pipeline works on 3.9+. For live trading via Polymarket's API, you need 3.9.10 or higher.", color=MUTED, size=9, max_width=500)

    y -= 15
    y = separator(c, y)

    # Get Anthropic key
    y = subheading(c, 50, y, "Get Your Anthropic API Key")
    y -= 5

    steps = [
        "Go to console.anthropic.com and sign in (or create an account)",
        "Navigate to API Keys in the left sidebar",
        "Click 'Create Key' and copy the key (starts with sk-ant-...)",
        "Keep this key — you'll enter it during setup",
    ]
    for i, step in enumerate(steps):
        y = bullet(c, 60, y, f"Step {i+1}: {step}")

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 2")

    c.showPage()

    # ===================== PAGE 3: Installation =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "2. INSTALLATION")
    y -= 5

    y = subheading(c, 50, y, "Option A: One-Command Setup (Recommended)")
    y -= 5

    y = text_wrap(c, 50, y, "This script handles everything — virtual environment, dependencies, API key entry, and verification.", color=MUTED, size=9)
    y -= 8

    y = code_block(c, 60, y, [
        "git clone https://github.com/brodyautomates/polymarket-pipeline.git",
        "cd polymarket-pipeline",
        "bash setup.sh",
    ])

    y -= 5
    y = text_wrap(c, 50, y, "The setup script will walk you through entering your API keys interactively. Just paste them when prompted.", color=WHITE, size=10)

    y -= 15
    y = separator(c, y)

    y = subheading(c, 50, y, "Option B: Manual Setup")
    y -= 5

    y = code_block(c, 60, y, [
        "git clone https://github.com/brodyautomates/polymarket-pipeline.git",
        "cd polymarket-pipeline",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "cp .env.example .env",
    ])

    y -= 5
    y = text_wrap(c, 50, y, "Then open .env in any text editor and add your keys:", color=WHITE, size=10)
    y -= 8

    y = code_block(c, 60, y, [
        "# Required",
        "ANTHROPIC_API_KEY=sk-ant-your-key-here",
        "",
        "# Optional — real-time news streams (highly recommended)",
        "TWITTER_BEARER_TOKEN=your-bearer-token",
        "TELEGRAM_BOT_TOKEN=your-bot-token",
        "TELEGRAM_CHANNEL_IDS=-100123456789,-100987654321",
        "",
        "# Optional — broader RSS coverage",
        "NEWSAPI_KEY=your-newsapi-key",
        "",
        "# Optional — only for live trading",
        "POLYMARKET_API_KEY=your-key",
        "POLYMARKET_API_SECRET=your-secret",
        "POLYMARKET_API_PASSPHRASE=your-passphrase",
        "POLYMARKET_PRIVATE_KEY=your-private-key",
    ])

    y -= 15
    y = separator(c, y)

    y = subheading(c, 50, y, "Verify Your Setup")
    y -= 5

    y = text_wrap(c, 50, y, "Run the verify command to check every connection before you start:", color=WHITE, size=10)
    y -= 8

    y = code_block(c, 60, y, [
        "python cli.py verify",
    ])

    y -= 5
    y = text_wrap(c, 50, y, "This checks: Python version, dependencies, .env file, Anthropic API key, news scraper, Polymarket API, and SQLite database. Fix anything marked FAIL before continuing.", color=MUTED, size=9, max_width=500)

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 3")

    c.showPage()

    # ===================== PAGE 4: Running the Pipeline =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "3. RUNNING THE PIPELINE")
    y -= 5

    y = subheading(c, 50, y, "V2: Real-Time Event-Driven Pipeline (Recommended)")
    y -= 5

    y = text_wrap(c, 50, y, "Dry-run is the default. Connects to Twitter, Telegram, and RSS — monitors breaking news continuously, classifies events, and logs trades without placing them. Zero risk.", color=WHITE, size=10)
    y -= 8

    y = code_block(c, 60, y, [
        "source .venv/bin/activate",
        "python cli.py watch",
        "",
        "# Enable live trading",
        "python cli.py watch --live",
    ])

    y -= 5
    y = text_wrap(c, 50, y, "The watch command runs indefinitely. It connects to your news sources, matches breaking headlines to niche Polymarket markets, classifies each with Claude, and executes trades when it finds edge.", color=MUTED, size=9, max_width=500)

    y -= 15

    y = subheading(c, 50, y, "V1: Synchronous RSS Pipeline")
    y -= 5

    y = code_block(c, 60, y, [
        "# Single scan — scrape RSS, score markets, log signals",
        "python cli.py run",
        "",
        "python cli.py run --max 15 --hours 12",
    ])

    y -= 15

    y = subheading(c, 50, y, "Launch the Live Dashboard")
    y -= 5

    y = text_wrap(c, 50, y, "Full-screen terminal dashboard showing the pipeline in real-time. Market scanner, trade log, performance stats, news ticker — all updating live.", color=WHITE, size=10)
    y -= 8

    y = code_block(c, 60, y, [
        "python cli.py dashboard",
        "",
        "# Faster scan cycles (every 30 seconds)",
        "python cli.py dashboard --speed 30",
    ])

    y -= 15
    y = separator(c, y)

    y = subheading(c, 50, y, "All CLI Commands")
    y -= 5

    commands = [
        ("python cli.py watch", "V2: Real-time event-driven pipeline"),
        ("python cli.py watch --live", "V2: Enable live trading"),
        ("python cli.py run", "V1: Synchronous RSS-based pipeline"),
        ("python cli.py dashboard", "Launch live terminal dashboard"),
        ("python cli.py backtest", "Backtest against resolved markets"),
        ("python cli.py calibrate", "Classification accuracy report"),
        ("python cli.py niche", "Browse niche markets (volume-filtered)"),
        ("python cli.py verify", "Check all API keys and connections"),
        ("python cli.py scrape", "Test the news scraper"),
        ("python cli.py markets", "Browse all active markets"),
        ("python cli.py trades", "View trade log"),
        ("python cli.py stats", "Performance + latency + calibration stats"),
    ]

    for cmd, desc in commands:
        if y < 60:
            c.showPage()
            draw_bg(c)
            y = H - 60
        c.setFillColor(GREEN)
        c.setFont("Courier", 9)
        c.drawString(60, y, cmd)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(310, y, desc)
        y -= 16

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 4")

    c.showPage()

    # ===================== PAGE 5: How It Works =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "4. HOW IT WORKS")
    y -= 5

    sections = [
        ("News Detection", "news_stream.py",
         "Real-time streams from Twitter API v2 (filtered by keywords), Telegram channels (long polling), and RSS fallback (every 120s). All three run concurrently. Events are deduplicated and timestamped with receive latency. If Twitter is unconfigured, the pipeline falls back to Telegram and RSS automatically."),

        ("Market Matching", "matcher.py",
         "Each breaking headline is matched to active niche markets (under $500K volume) by keyword overlap. Only relevant markets proceed to classification. This is the core edge: niche markets are slow to reprice — the crowd is small and the information gap is real."),

        ("Classification", "classifier.py",
         "Instead of asking Claude 'what's the probability?', the system asks: 'Does this news make the market MORE likely to resolve YES, MORE likely to resolve NO, or is it NOT RELEVANT?' Claude also rates materiality (0.0-1.0) — how much should this move the price? This is a classification task, not estimation — something LLMs are genuinely good at."),

        ("Edge Detection", "edge.py",
         "A signal fires when direction is bullish or bearish AND materiality exceeds the threshold (default 0.6) AND the market price has room to move. Position sizing uses quarter-Kelly criterion based on materiality score and current market price."),

        ("Trade Execution", "executor.py",
         "In dry-run mode: logs what it would have bet. In live mode: places limit orders through Polymarket's CLOB API. Safety rails enforce max bet ($25), daily loss limit ($100), and auto-halt on breach."),

        ("Calibration Tracking", "calibrator.py",
         "Every classification is tracked. As markets resolve, the system measures whether bullish/bearish calls were correct. Accuracy is broken down by news source and market category. If strategy accuracy drops below baseline, the system flags it."),

        ("Logging", "logger.py",
         "SQLite audit trail — every trade, classification, news event, and latency measurement. Tracks news-to-trade time against the 5-second target."),
    ]

    for title, filename, desc in sections:
        if y < 120:
            c.showPage()
            draw_bg(c)
            y = H - 60

        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, title)
        c.setFillColor(MUTED)
        c.setFont("Courier", 9)
        c.drawString(250, y, filename)
        y -= 18
        y = text_wrap(c, 50, y, desc, color=WHITE, size=9.5, max_width=510, line_height=13)
        y -= 12

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 5")

    c.showPage()

    # ===================== PAGE 6: Configuration & Safety =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "5. CONFIGURATION & SAFETY")
    y -= 5

    y = subheading(c, 50, y, "Settings (.env)")
    y -= 5

    settings = [
        ("DRY_RUN", "true", "Set to false for live trading"),
        ("MAX_BET_USD", "25", "Maximum single bet size in dollars"),
        ("DAILY_LOSS_LIMIT_USD", "100", "Pipeline halts if daily losses hit this"),
        ("EDGE_THRESHOLD", "0.10", "Minimum edge to trigger trade"),
        ("MAX_VOLUME_USD", "500000", "Only trade markets below this volume"),
        ("MIN_VOLUME_USD", "1000", "Skip dead markets"),
        ("MATERIALITY_THRESHOLD", "0.6", "Minimum materiality score to act on"),
        ("SPEED_TARGET_SECONDS", "5", "Target news-to-trade latency"),
    ]

    # Table header
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(60, y, "SETTING")
    c.drawString(240, y, "DEFAULT")
    c.drawString(330, y, "DESCRIPTION")
    y -= 5
    c.setStrokeColor(HexColor("#333333"))
    c.line(60, y, W - 60, y)
    y -= 15

    for setting, default, desc in settings:
        c.setFillColor(GREEN)
        c.setFont("Courier", 9)
        c.drawString(60, y, setting)
        c.setFillColor(WHITE)
        c.setFont("Courier", 9)
        c.drawString(240, y, default)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(330, y, desc)
        y -= 18

    y -= 15
    y = subheading(c, 50, y, "Safety Rails")
    y -= 5

    safety = [
        "Dry-run mode is ON by default. Zero real trades until you explicitly enable --live.",
        "$25 max single bet. Configurable, but you have to change it intentionally.",
        "$100 daily loss limit. Pipeline stops executing if you hit this.",
        "Quarter-Kelly position sizing. Conservative sizing that survives bad streaks.",
        "API keys never leave your machine. .env is gitignored. Nothing sent anywhere except the APIs you configure.",
    ]
    for item in safety:
        y = bullet(c, 60, y, item, max_width=470)

    y -= 15
    y = separator(c, y)

    y = subheading(c, 50, y, "News Sources (config.py)")
    y -= 5

    y = text_wrap(c, 50, y, "Twitter and Telegram are the primary sources (lowest latency). RSS is the fallback. All are configured in config.py:", color=WHITE, size=10)
    y -= 8

    y = code_block(c, 60, y, [
        "# Twitter keywords for filtered stream",
        "TWITTER_KEYWORDS = ['OpenAI', 'Bitcoin', 'Fed rate', 'Trump', ...]",
        "",
        "# Telegram channels to monitor",
        "TELEGRAM_CHANNEL_IDS = ['-100123456789']",
        "",
        "# RSS fallback feeds",
        "RSS_FEEDS = [",
        '    "https://feeds.feedburner.com/TechCrunch",',
        '    "https://feeds.arstechnica.com/arstechnica/index",',
        '    "https://www.theverge.com/rss/index.xml",',
        "]",
    ])

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 6")

    c.showPage()

    # ===================== PAGE 7: What You Can Build =====================
    draw_bg(c)
    y = H - 60

    y = heading(c, 50, y, "6. WHAT YOU CAN BUILD FROM HERE")
    y -= 5

    y = text_wrap(c, 50, y, "This is a working foundation. The pipeline is modular — every component can be extended or swapped independently.", color=WHITE, size=10)
    y -= 10

    ideas = [
        ("Smarter Classification", "Feed Claude the full article text instead of just headlines. Use web scraping to pull article bodies from the URLs before classifying."),
        ("Multi-Model Consensus", "Classify with Claude + GPT-4 + Gemini. Only bet when all three agree on direction. Reduces false signals dramatically."),
        ("Portfolio Tracking", "Monitor open positions, track resolution status, auto-exit when edge disappears or market moves against you."),
        ("Deeper Niche Sourcing", "SEC EDGAR filings, earnings call transcripts, press release wires. The more obscure the source, the bigger the information gap."),
        ("Adaptive Thresholds", "Use calibration data to auto-tune materiality and edge thresholds by market category. Let the data optimize itself."),
        ("Multi-Chain Execution", "Extend executor.py to place orders on Manifold, Kalshi, or other prediction markets simultaneously."),
    ]

    for title, desc in ideas:
        if y < 80:
            c.showPage()
            draw_bg(c)
            y = H - 60
        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, title)
        y -= 16
        y = text_wrap(c, 50, y, desc, color=MUTED, size=9.5, max_width=510, line_height=13)
        y -= 12

    y -= 15
    y = separator(c, y)

    # Quick reference
    y = subheading(c, 50, y, "Quick Reference — File Map")
    y -= 5

    files = [
        ("news_stream.py", "Real-time news — Twitter API v2, Telegram, RSS fallback"),
        ("market_watcher.py", "Polymarket WebSocket — live prices, niche filter, momentum"),
        ("classifier.py", "Claude classification — bullish/bearish/neutral + materiality"),
        ("matcher.py", "Routes breaking news to relevant markets"),
        ("edge.py", "Edge detection + Kelly sizing (classification-based)"),
        ("executor.py", "Trade execution — dry-run + live CLOB orders"),
        ("pipeline.py", "Event-driven orchestrator (asyncio)"),
        ("calibrator.py", "Tracks classification accuracy over time"),
        ("backtest.py", "Historical replay for strategy validation"),
        ("scraper.py", "RSS + NewsAPI ingestion (V1 / RSS fallback)"),
        ("markets.py", "Polymarket Gamma API — market data"),
        ("scorer.py", "V1 Claude probability scoring engine"),
        ("logger.py", "SQLite — trades, news events, calibration, latency"),
        ("dashboard.py", "Bloomberg Terminal-style live dashboard"),
        ("cli.py", "CLI — watch, run, backtest, calibrate, niche, verify"),
        ("config.py", "All settings, API keys, thresholds"),
        ("setup.sh", "One-command setup script"),
    ]

    for fname, desc in files:
        if y < 50:
            c.showPage()
            draw_bg(c)
            y = H - 60
        c.setFillColor(GREEN)
        c.setFont("Courier", 9)
        c.drawString(60, y, fname)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(200, y, desc)
        y -= 15

    # Bottom CTA
    y -= 20
    c.setStrokeColor(GREEN)
    c.setLineWidth(2)
    c.line(50, y, W - 50, y)
    y -= 30
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "READY TO RUN")
    y -= 22
    c.setFillColor(WHITE)
    c.setFont("Helvetica", 11)
    c.drawString(50, y, "source .venv/bin/activate && python cli.py watch")

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawRightString(W - 50, 35, "Page 7")
    c.drawCentredString(W / 2, 35, "github.com/brodyautomates/polymarket-pipeline")

    # ===================== FINAL PAGE: Disclaimer =====================
    c.showPage()
    draw_bg(c)
    y = H - 60

    # Top accent
    c.setStrokeColor(YELLOW)
    c.setLineWidth(2)
    c.line(50, H - 40, W - 50, H - 40)

    y = H - 100
    c.setFillColor(YELLOW)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "DISCLAIMER")
    tw = c.stringWidth("DISCLAIMER", "Helvetica-Bold", 18)
    c.setStrokeColor(YELLOW)
    c.setLineWidth(0.5)
    c.line(50, y - 4, 50 + tw, y - 4)
    y -= 35

    disclaimer_sections = [
        ("For Entertainment & Educational Purposes Only",
         "This software is provided strictly for entertainment and educational purposes. It is not financial advice, investment advice, or a recommendation to buy or sell any asset."),
        ("No Financial Responsibility",
         "The authors and contributors of this project are not responsible for any financial losses, damages, or consequences arising from the use of this software. You use it entirely at your own risk."),
        ("Trading Risk",
         "Prediction market trading carries significant financial risk. You can lose some or all of the money you trade with. Never trade with funds you cannot afford to lose."),
        ("No Guarantee of Performance",
         "Past performance of any strategy, signal, or classification produced by this pipeline does not guarantee future results. The pipeline may produce incorrect signals."),
        ("Regulatory Compliance",
         "It is your responsibility to ensure that your use of this software complies with all applicable laws and regulations in your jurisdiction. Prediction markets may be restricted or prohibited in some regions."),
    ]

    for title, body in disclaimer_sections:
        if y < 100:
            c.showPage()
            draw_bg(c)
            y = H - 60
        c.setFillColor(CYAN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, title)
        y -= 16
        y = text_wrap(c, 50, y, body, color=WHITE, size=9.5, max_width=510, line_height=13)
        y -= 14

    # Bottom box
    y -= 10
    draw_panel(c, 50, y - 44, W - 100, 50, border_color=YELLOW)
    c.setFillColor(YELLOW)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, y - 22, "BY USING THIS SOFTWARE YOU ACKNOWLEDGE AND ACCEPT ALL OF THE ABOVE.")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, y - 36, "This is not financial advice. For entertainment and educational use only.")

    # Footer
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(50, 35, "Polymarket Pipeline — Setup Guide")
    c.drawCentredString(W / 2, 35, "github.com/brodyautomates/polymarket-pipeline")
    c.drawRightString(W - 50, 35, "@brodyautomates")

    c.save()


if __name__ == "__main__":
    repo_path = os.path.join(os.path.dirname(__file__), "SETUP_GUIDE.pdf")
    lead_magnet_path = os.path.expanduser(
        "~/Desktop/EXOSOFT HQ/Lead-Magnets/Polymarket_Pipeline_Setup_Guide.pdf"
    )

    build_pdf(repo_path)
    print(f"Generated: {repo_path}")

    build_pdf(lead_magnet_path)
    print(f"Generated: {lead_magnet_path}")
