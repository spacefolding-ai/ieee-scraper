#!/bin/bash

# IEEE Xplore Author Scraper - Run Script
# Usage: ./run_scraper.sh [config_file]

echo "======================================================================"
echo "IEEE Xplore Author Scraper"
echo "======================================================================"
echo ""

# Check if config file is specified
if [ "$1" != "" ]; then
    CONFIG_FILE="$1"
    echo "Using config file: $CONFIG_FILE"
    
    # Check if file exists
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "Error: Config file '$CONFIG_FILE' not found!"
        exit 1
    fi
    
    # Run with specified config
    python3 ieee_author_scraper.py --config "$CONFIG_FILE"
else
    echo "Using default config: config.json"
    echo ""
    echo "To use a different config file, run:"
    echo "  ./run_scraper.sh config_test.json"
    echo ""
    
    # Run with default config
    python3 ieee_author_scraper.py
fi

echo ""
echo "======================================================================"
echo "Scraping complete!"
echo "Check authors_output.json for results"
echo "Check ieee_scraper.log for detailed logs"
echo "======================================================================"

