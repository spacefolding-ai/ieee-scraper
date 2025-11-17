# CRITICAL ISSUE: Machine Learning Domain False Positives

## The Problem

**66.5% of authors (3,299/4,959) have "Machine Learning" in their domain**, but this is largely **INACCURATE**.

## Root Cause

The keyword "ai" is matched as a **substring**, not a whole word. This causes it to match inside common words:

### Examples of False Matches:

| Common Word | Contains "ai" | In Publications |
|-------------|---------------|-----------------|
| **m**ai**n** | ✓ | Very common |
| **g**ai**n** | ✓ | Very common |
| **cert**ai**n** | ✓ | Very common |
| **obt**ai**n** | ✓ | Very common |
| **tr**ai**n** | ✓ | Very common (but means training) |
| photovolt**ai**c | ✓ | Common in EV research |
| uncert**ai**n | ✓ | Common in research papers |
| **av**ai**lable** | ✓ | Very common |

## Data Analysis

Out of 100 authors with "Machine Learning" domain:

### Keyword Contribution Breakdown:
```
Keyword                    Mentions    % of Total ML Score
─────────────────────────────────────────────────────────
"ai"                         440         89.2%  ← PROBLEM!
"neural network"              33          6.7%
"deep learning"                8          1.6%
"artificial intelligence"      8          1.6%
"machine learning"             4          0.8%
```

### Legitimacy Check:
- **24%** have explicit ML terms (machine learning, deep learning, neural network)
- **76%** rely ONLY on the "ai" keyword (likely false positives)

## Real-World Examples

**Example 1: Patrizio Manganiello**
- **Assigned domain:** "Electric Vehicles, Power Electronics, Machine Learning"
- **Actual research:** Power electronics for EVs
- **Why ML was assigned:** Words like "**ai**ming", "photovolt**ai**c" in abstracts
- **Legitimate ML?** ❌ NO

**Example 2: J. Nuyts**  
- **Assigned domain:** "Electric Vehicles, Machine Learning, Energy Storage"
- **Actual research:** Medical PET imaging
- **Why ML was assigned:** Words like "m**ai**n", "g**ai**n", "obt**ai**n" in abstracts
- **Legitimate ML?** ❌ NO (also wrong about EV!)

## The Code Problem

```python
# Current implementation in extract_additional_properties.py (line 207)
count = combined_text.count(keyword.lower())  # ← PROBLEM: substring match!

# What happens:
text = "the main gain in this domain is obtained..."
text.count('ai')  # Returns 4! (main, gain, domain, obtained)
```

## Impact

1. **Inflated ML coverage:** 66.5% shown vs. ~15-20% actual
2. **Misleading for targeting:** Many "ML researchers" don't do ML
3. **Reduces domain accuracy:** Pushes out more accurate domains from top 3

## Solution

### Option 1: Use Word Boundaries (Regex)
```python
import re

# Instead of:
count = combined_text.count('ai')

# Use:
count = len(re.findall(r'\bai\b', combined_text, re.IGNORECASE))
```

### Option 2: Remove "AI" Keyword Entirely
```python
# Change to:
'machine_learning': ['machine learning', 'deep learning', 'neural network', 'artificial intelligence']
# Remove: 'ai', 'AI'
```

### Option 3: Use Only Explicit ML Terms
```python
'machine_learning': ['machine learning', 'deep learning', 'neural network']
# Remove short ambiguous terms
```

## Recommendation

**Immediate fix:** Remove "AI" from the keyword list and re-run domain extraction.

This would:
- ✅ Reduce ML domain from 66.5% to ~15-20% (more accurate)
- ✅ Eliminate false positives
- ✅ Make domain more reliable for targeting

**Expected new distribution:**
- Only authors who explicitly mention "machine learning", "deep learning", "neural network", or "artificial intelligence"
- More accurate representation of actual research domains

## Files to Update

1. `extract_additional_properties.py` (line 70)
2. Re-run on all `*_simple.json` files
3. Update merged CSV files

