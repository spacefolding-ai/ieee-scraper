#!/bin/bash

# IEEE Xplore Scraper - POST API Method
# New method using POST response capture instead of HTML parsing

echo "======================================================================"
echo "IEEE Xplore Scraper (POST API Method)"
echo "======================================================================"
echo ""
echo "This scraper uses POST response capture for:"
echo "  ✓ Clean JSON data (no HTML parsing)"
echo "  ✓ Complete publication metadata"
echo "  ✓ Author information with affiliations"
echo "  ✓ Faster and more reliable"
echo ""
echo "======================================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

# Ask for options
echo "Options:"
echo "  1. Collect publications only"
echo "  2. Collect + filter by European countries"
echo ""
read -p "Enter choice (1-2, default=2): " choice

FILTER_ARG=""
if [ "$choice" == "1" ]; then
    echo ""
    echo "✓ Will collect all publications (no country filtering)"
else
    FILTER_ARG="--filter-countries"
    echo ""
    echo "✓ Will filter by European countries from config"
fi

echo ""
echo "Starting scraper..."
echo ""

# Run scraper
python3 ieee_scraper_post_api.py $FILTER_ARG

echo ""
echo "======================================================================"
echo "Done! Check results/ folder for output"
echo "======================================================================"

