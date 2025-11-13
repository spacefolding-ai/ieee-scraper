#!/usr/bin/env python3
"""
Real-time progress monitor for author type enrichment.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from collections import Counter

PROGRESS_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment_progress.json")
LOG_FILE = Path("/Users/miroslavjugovic/Projects/ieee-scraper/enrichment.log")

def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")

def format_time_elapsed(start_time_str):
    """Format elapsed time."""
    start = datetime.fromisoformat(start_time_str)
    elapsed = datetime.now() - start
    
    hours = int(elapsed.total_seconds() // 3600)
    minutes = int((elapsed.total_seconds() % 3600) // 60)
    seconds = int(elapsed.total_seconds() % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def estimate_time_remaining(total, processed, elapsed_seconds):
    """Estimate time remaining."""
    if processed == 0:
        return "Calculating..."
    
    rate = processed / elapsed_seconds
    remaining = total - processed
    remaining_seconds = remaining / rate
    
    hours = int(remaining_seconds // 3600)
    minutes = int((remaining_seconds % 3600) // 60)
    
    return f"{hours:02d}:{minutes:02d}"

def load_progress():
    """Load progress data."""
    if not PROGRESS_FILE.exists():
        return None
    
    try:
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    except:
        return None

def get_last_log_lines(n=10):
    """Get last n lines from log file."""
    if not LOG_FILE.exists():
        return []
    
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return lines[-n:]
    except:
        return []

def display_progress():
    """Display real-time progress."""
    progress = load_progress()
    
    if not progress:
        print("No progress data available yet. Waiting for enrichment to start...")
        return
    
    total = 3019  # Total authors to process
    processed = progress.get('total_processed', 0)
    successful = progress.get('successful', 0)
    failed = progress.get('failed', 0)
    
    # Calculate metrics
    percent_complete = (processed / total * 100) if total > 0 else 0
    success_rate = (successful / processed * 100) if processed > 0 else 0
    
    # Time calculations
    start_time = progress.get('started_at')
    if start_time:
        elapsed = format_time_elapsed(start_time)
        start_dt = datetime.fromisoformat(start_time)
        elapsed_seconds = (datetime.now() - start_dt).total_seconds()
        eta = estimate_time_remaining(total, processed, elapsed_seconds)
    else:
        elapsed = "00:00:00"
        eta = "Calculating..."
    
    # Progress bar
    bar_length = 50
    filled = int(bar_length * processed / total)
    bar = '█' * filled + '░' * (bar_length - filled)
    
    # Clear and display
    clear_screen()
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " AUTHOR TYPE ENRICHMENT - LIVE PROGRESS ".center(78) + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Progress bar
    print(f"  Progress: [{bar}] {percent_complete:.1f}%")
    print()
    
    # Statistics
    print("  " + "─" * 76)
    print(f"  │ Processed:     {processed:>6,} / {total:>6,} authors")
    print(f"  │ Successful:    {successful:>6,}   ({success_rate:>5.1f}%)")
    print(f"  │ Not Found:     {failed:>6,}   ({(failed/processed*100) if processed > 0 else 0:>5.1f}%)")
    print("  " + "─" * 76)
    print(f"  │ Time Elapsed:  {elapsed}")
    print(f"  │ ETA:           {eta}")
    print("  " + "─" * 76)
    print()
    
    # Author types found
    if progress.get('results'):
        type_counts = Counter(r['author_type'] for r in progress['results'] if r['author_type'])
        
        if type_counts:
            print("  Author Types Found:")
            print("  " + "─" * 76)
            
            # Show top 10
            for author_type, count in type_counts.most_common(10):
                pct = (count / successful * 100) if successful > 0 else 0
                print(f"    {author_type:<35s} {count:>5,}  ({pct:>4.1f}%)")
            
            if len(type_counts) > 10:
                print(f"    ... and {len(type_counts) - 10} more types")
            print()
    
    # Recent activity
    print("  Recent Activity:")
    print("  " + "─" * 76)
    recent_logs = get_last_log_lines(8)
    for line in recent_logs:
        line = line.strip()
        if line:
            # Color code messages
            if '✅' in line or 'SUCCESS' in line:
                prefix = "  🟢 "
            elif '❌' in line or 'WARNING' in line:
                prefix = "  🟡 "
            elif 'ERROR' in line:
                prefix = "  🔴 "
            else:
                prefix = "     "
            
            # Truncate if too long
            display_line = line[-68:] if len(line) > 68 else line
            print(f"{prefix}{display_line}")
    
    print()
    print("  " + "─" * 76)
    print("  Press Ctrl+C to stop monitoring (enrichment will continue)")
    print("  " + "─" * 76)

def main():
    """Main monitoring loop."""
    print("Starting progress monitor...")
    print("Monitoring enrichment progress in real-time...")
    print()
    
    try:
        while True:
            display_progress()
            time.sleep(2)  # Update every 2 seconds
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
        print("Enrichment process is still running in the background.")
        print("\nTo check final results:")
        print("  - Progress: enrichment_progress.json")
        print("  - Results:  enrichment_results.json")
        print("  - Log:      enrichment.log")

if __name__ == "__main__":
    main()

