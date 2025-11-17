# DACH Affiliation Cleaning Guide

## 🎯 Goal
Clean DACH affiliations to **official German names** with email validation.

---

## 🚀 Quick Start

### Step 1: Test Run (2 minutes)
```bash
python3 clean_dach_affiliations.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --test
```

This processes only 5 affiliations to verify everything works.

---

### Step 2: Full Run (~5 minutes)
```bash
python3 clean_dach_affiliations.py \
  --api-key "pplx-YOUR_KEY_HERE"
```

---

## 📊 What It Does

1. **Extracts** unique (affiliation, email) pairs from `final_dach.csv`
2. **Cleans** each affiliation using Perplexity API with email validation
3. **Validates** against email domain (e.g., @tum.de → Technische Universität München)
4. **Adds** new column `official_german_name` to CSV
5. **Generates** review report for flagged items

---

## 📁 Output Files

### 1. `final_dach_cleaned.csv`
Your updated CSV with new column:
```csv
author_id,name,email,primary_affiliation,official_german_name
37086015611,Wei Tian,wei.tian@tum.de,"Technical University of Munich, Germany",Technische Universität München
```

### 2. `affiliation_review.txt`
Review report showing:
- ✅ High confidence cleanings (most affiliations)
- ⚠️ Flagged for manual review (~5-10%)

### 3. `affiliation_cache.json`
Cached results (prevents re-processing if you run again)

### 4. `affiliation_cleaning.log`
Detailed processing log

---

## 🔍 Review Process

After running, check `affiliation_review.txt`:

```
⚠️  FLAGGED FOR REVIEW
────────────────────────────────────────
Authors affected: 15
Original: Some unclear affiliation...
Cleaned:  Best guess from email domain
Email:    user@organization.de
Status:   ⚠️ Email suggests different org
```

**Action:** Only review the flagged items (typically 10-20 affiliations)

---

## ✨ Example Transformations

| Original | → | Official German Name |
|----------|---|---------------------|
| `Corporate Research, Robert Bosch GmbH, Renningen, Germany` | → | `Robert Bosch GmbH` |
| `Technical University of Munich, Germany` | → | `Technische Universität München` |
| `Institute for..., TU Braunschweig, Brunswick, Germany` | → | `Technische Universität Braunschweig` |
| `ETH Zurich, Switzerland` | → | `ETH Zürich` |
| `Fraunhofer Institute for Solar Energy Systems ISE` | → | `Fraunhofer ISE` |

---

## ⚙️ Advanced Options

### Custom Delay (if hitting rate limits)
```bash
python3 clean_dach_affiliations.py \
  --api-key "pplx-xxxx" \
  --delay 3.0
```

### Custom Input/Output Files
```bash
python3 clean_dach_affiliations.py \
  --api-key "pplx-xxxx" \
  --input "path/to/input.csv" \
  --output "path/to/output.csv"
```

---

## ⏱️ Time Estimate

| Task | Time |
|------|------|
| Extract unique affiliations | 30 sec |
| Process ~200 unique affiliations | 3-5 min |
| Generate outputs | 10 sec |
| **Review flagged items** | 10-15 min |
| **TOTAL** | **~20 minutes** |

---

## 💰 Cost

- ~200 affiliations × 500 tokens = **100,000 tokens**
- Cost: **~$0.02** (well within 5M free tier)

---

## 🔄 Resume/Re-run

The script caches results in `affiliation_cache.json`.

If interrupted or you want to re-run:
- Cached affiliations are **skipped automatically**
- Only new/changed affiliations are processed
- Safe to run multiple times!

---

## ✅ Validation Features

### Email Domain Matching
- `@tum.de` → Validates to "Technische Universität München"
- `@bosch.com` → Validates to "Robert Bosch GmbH"
- `@ethz.ch` → Validates to "ETH Zürich"

### Confidence Levels
- **High:** Official name found, matches email ✅
- **Medium:** Name found but minor uncertainty ⚠️
- **Low:** Unclear, needs review ❌

---

## 📝 Manual Corrections

If you need to correct any names:

1. Edit `affiliation_cache.json`
2. Find the entry
3. Change `official_german_name` to correct value
4. Re-run script (it will use your correction)

---

## 🆘 Troubleshooting

### "Invalid API key"
- Check your Perplexity API key: https://www.perplexity.ai/settings/api
- Include the `pplx-` prefix

### "Rate limit exceeded"
- Increase `--delay` to 3.0 or higher
- Script already includes 2-second delays by default

### Low confidence results
- Check `affiliation_review.txt`
- Review flagged items manually
- Edit cache file with corrections if needed

---

## 🎉 Expected Results

For 521 DACH authors:
- **~200 unique affiliations**
- **~95% high confidence** (automatic)
- **~5% flagged for review** (10-20 items)
- **Total time: 20 minutes** including review

---

## 📞 Next Steps

After cleaning:
1. Review `affiliation_review.txt` (focus on flagged items)
2. Make any manual corrections needed
3. Use `final_dach_cleaned.csv` for your reports
4. Repeat process for non-DACH if needed

---

**You're ready to go! 🚀**

```bash
python3 clean_dach_affiliations.py --api-key "pplx-YOUR_KEY" --test
```

