#!/bin/bash
# Polymarket Pipeline V2 setup

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${GREEN}${BOLD}  POLYMARKET PIPELINE V2 - SETUP${NC}"
echo -e "${GREEN}  Breaking News Detector + AI Classifier + Niche Market Trader${NC}"
echo ""

PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" --version 2>&1 | awk '{print $2}')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
            PYTHON=$cmd
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}ERROR: Python 3.9+ is required.${NC}"
    exit 1
fi

echo -e "${GREEN}OK${NC} Found $("$PYTHON" --version)"

if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    "$PYTHON" -m venv .venv
    echo -e "${GREEN}OK${NC} Virtual environment created"
else
    echo -e "${GREEN}OK${NC} Virtual environment exists"
fi

source .venv/bin/activate

echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip -q 2>/dev/null
pip install -r requirements.txt -q 2>/dev/null
echo -e "${GREEN}OK${NC} Dependencies installed"

if [ -f ".env" ]; then
    echo -e "${GREEN}OK${NC} .env file exists"
else
    echo ""
    echo -e "${BOLD}Let's configure your API keys.${NC}"
    echo ""

    echo -e "${YELLOW}1. Gemini API Key${NC} (required)"
    read -p "   Enter your Gemini API key: " GEMINI_KEY
    echo ""

    echo -e "${YELLOW}2. Twitter API v2 Bearer Token${NC} (optional)"
    read -p "   Enter Twitter bearer token (or press Enter to skip): " TWITTER_KEY
    echo ""

    echo -e "${YELLOW}3. Telegram Bot Token${NC} (optional)"
    read -p "   Enter Telegram bot token (or press Enter to skip): " TELEGRAM_KEY
    TELEGRAM_CHANNELS=""
    if [ -n "$TELEGRAM_KEY" ]; then
        read -p "   Enter channel IDs (comma-separated, or Enter to skip): " TELEGRAM_CHANNELS
    fi
    echo ""

    echo -e "${YELLOW}4. Polymarket API Credentials${NC} (optional, live trading only)"
    read -p "   Enter Polymarket API key (or press Enter to skip): " POLY_KEY
    POLY_SECRET=""
    POLY_PASS=""
    POLY_PRIV=""
    if [ -n "$POLY_KEY" ]; then
        read -p "   Enter Polymarket API secret: " POLY_SECRET
        read -p "   Enter Polymarket API passphrase: " POLY_PASS
        read -p "   Enter Polymarket private key: " POLY_PRIV
    fi
    echo ""

    echo -e "${YELLOW}5. NewsAPI Key${NC} (optional)"
    read -p "   Enter NewsAPI key (or press Enter to skip): " NEWSAPI
    echo ""

    cat > .env << ENVEOF
# Gemini (required)
GEMINI_API_KEY=${GEMINI_KEY}

# Optional model overrides
CLASSIFICATION_MODEL=gemini-3-flash-preview
SCORING_MODEL=gemini-3.1-pro-preview

# Twitter API v2 (optional)
TWITTER_BEARER_TOKEN=${TWITTER_KEY}

# Telegram (optional)
TELEGRAM_BOT_TOKEN=${TELEGRAM_KEY}
TELEGRAM_CHANNEL_IDS=${TELEGRAM_CHANNELS}

# Polymarket CLOB API (optional)
POLYMARKET_API_KEY=${POLY_KEY}
POLYMARKET_API_SECRET=${POLY_SECRET}
POLYMARKET_API_PASSPHRASE=${POLY_PASS}
POLYMARKET_PRIVATE_KEY=${POLY_PRIV}

# NewsAPI.org (optional)
NEWSAPI_KEY=${NEWSAPI}

# Pipeline Settings
DRY_RUN=true
MAX_BET_USD=25
DAILY_LOSS_LIMIT_USD=100
EDGE_THRESHOLD=0.10

# V2 Settings
MAX_VOLUME_USD=500000
MIN_VOLUME_USD=1000
MATERIALITY_THRESHOLD=0.6
SPEED_TARGET_SECONDS=5
ENVEOF

    echo -e "${GREEN}OK${NC} .env file created"
fi

echo ""
echo -e "${YELLOW}Running verification...${NC}"
echo ""
"$PYTHON" cli.py verify

echo ""
echo -e "${GREEN}${BOLD}  SETUP COMPLETE${NC}"
echo ""
echo "  Next steps:"
echo "    source .venv/bin/activate"
echo "    python cli.py watch"
echo "    python cli.py run"
echo "    python cli.py dashboard"
echo "    python cli.py backtest"
echo ""
