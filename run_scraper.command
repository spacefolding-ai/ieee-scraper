#!/bin/bash

# IEEE Xplore Author Scraper - macOS Launch Script
# Double-click this file to run the scraper with user confirmation

# Change to the script's directory
cd "$(dirname "$0")"

# Display banner
echo "=============================================================="
echo "       IEEE Xplore Author Scraper"
echo "=============================================================="
echo ""
echo "This script will:"
echo "  1. Collect all publications from IEEE Xplore"
echo "  2. Show you the total count"
echo "  3. Ask for confirmation before scraping"
echo ""
echo "=============================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed."
    echo "   Please install Python 3 from https://www.python.org/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if requirements are installed
echo "Checking dependencies..."
python3 -c "import selenium, bs4, pycountry" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Some dependencies are missing. Installing..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install dependencies."
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

echo "✅ Dependencies OK"
echo ""

# Ask which config to use
echo "Which configuration would you like to use?"
echo "  1) config_test.json (3 queries, ~5 minutes)"
echo "  2) config.json (50 queries, ~2-3 hours)"
echo "  3) config_hil_test.json (Hardware-in-Loop test, 4 queries, ~20 publications)"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        CONFIG="config_test.json"
        ;;
    2)
        CONFIG="config.json"
        ;;
    3)
        CONFIG="config_hil_test.json"
        echo ""
        echo "🔬 Running Hardware-in-the-Loop (HIL) Keyword Test"
        echo "   This will search for HIL-related publications to verify"
        echo "   that institutions like Typhoon HIL are correctly detected."
        echo ""
        ;;
    *)
        echo "❌ Invalid choice. Exiting."
        read -p "Press Enter to exit..."
        exit 1
        ;;
esac

echo ""
echo "Starting scraper with $CONFIG..."
echo ""
echo "=============================================================="
echo ""

# Run the scraper (WITHOUT --no-confirm, so it will ask for confirmation)
python3 ieee_author_scraper.py --config "$CONFIG"

# Wait for user before closing
echo ""
echo "=============================================================="
read -p "Press Enter to close this window..."

