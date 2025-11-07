#!/bin/bash

# IEEE Xplore Scraper - macOS Launch Script
# Double-click to run with live log viewing

# Change to script directory
cd "$(dirname "$0")"

# Display banner
echo "======================================================================"
echo "       IEEE Xplore Scraper (POST API Method)"
echo "======================================================================"
echo ""
echo "This scraper will:"
echo "  • Capture IEEE publications via POST API"
echo "  • Filter by European countries"
echo "  • Show live progress logs"
echo "  • Save results to results/ folder"
echo ""
echo "======================================================================"
echo ""

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed."
    echo "   Please install Python 3 from https://www.python.org/"
    echo ""
    read -p "Press Enter to exit..."
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
python3 -c "import selenium, webdriver_manager" 2>/dev/null
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

# Ask for filtering option
echo "======================================================================"
echo "Filtering Options:"
echo "======================================================================"
echo ""
echo "  1) Filter by European countries (recommended)"
echo "     - Checks author affiliations"
echo "     - Keeps only European authors"
echo ""
echo "  2) No filtering"
echo "     - Collects all publications"
echo "     - You can filter later"
echo ""
read -p "Enter choice (1-2, default=1): " filter_choice

FILTER_ARG=""
if [ "$filter_choice" == "2" ]; then
    echo ""
    echo "✅ No filtering - will collect all publications"
else
    FILTER_ARG="--filter-countries"
    echo ""
    echo "✅ Country filtering enabled"
fi

# Ask for browser mode
echo ""
echo "======================================================================"
echo "Browser Mode:"
echo "======================================================================"
echo ""
echo "  1) Headless mode (default, runs in background)"
echo "  2) Visible mode (for debugging)"
echo ""
read -p "Enter choice (1-2, default=1): " browser_choice

if [ "$browser_choice" == "2" ]; then
    FILTER_ARG="$FILTER_ARG --visible"
    echo ""
    echo "✅ Visible browser mode (you'll see Chrome window)"
else
    echo ""
    echo "✅ Headless mode (background)"
fi

echo ""
echo "======================================================================"
echo "Starting scraper with live logs..."
echo "======================================================================"
echo ""

# Run scraper with live output
python3 -u ieee_scraper_post_api.py $FILTER_ARG 2>&1 | while IFS= read -r line; do
    echo "$line"
    
    # Also save to log file
    echo "$line" >> results/scraper_live.log
done

# Check exit status
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "======================================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Scraping completed successfully!"
    echo ""
    echo "Results saved to:"
    echo "  📄 results/publications_post_api.json (processed data)"
    echo "  📄 results/raw_post_responses.json (all responses combined)"
    echo "  📁 results/raw_responses/ (individual page responses)"
    echo "  📋 results/scraper_live.log"
    echo ""
    
    # Show summary if results exist
    if [ -f "results/publications_post_api.json" ]; then
        echo "Summary:"
        python3 -c "
import json
import os
try:
    with open('results/publications_post_api.json') as f:
        data = json.load(f)
        print(f\"  Total publications: {data['metadata']['totalPublications']}\")
        print(f\"  Collection date: {data['metadata']['collectionDate']}\")
        print(f\"  Method: {data['metadata']['method']}\")
    
    # Count individual response files
    raw_responses_dir = 'results/raw_responses'
    if os.path.exists(raw_responses_dir):
        page_files = [f for f in os.listdir(raw_responses_dir) if f.endswith('.json')]
        print(f\"  Individual response files: {len(page_files)}\")
    
    # Also show raw responses count
    with open('results/raw_post_responses.json') as f:
        raw = json.load(f)
        print(f\"  Raw API pages captured: {raw['metadata']['totalPages']}\")
except:
    pass
" 2>/dev/null
    fi
else
    echo "⚠️  Scraping ended with errors (exit code: $EXIT_CODE)"
    echo ""
    echo "Check the logs above or:"
    echo "  📋 results/scraper_live.log"
fi

echo "======================================================================"
echo ""
read -p "Press Enter to close this window..."

