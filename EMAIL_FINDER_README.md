# 📧 Email Finder - Quick Start

## 🎯 Goal
Find institutional email addresses for 2,211 European first authors.

---

## ⚡ Fastest Method (Recommended)

### **Perplexity API - $1, 30min-6hrs, 65-70% success**

**1. Get API Key (2 minutes):**
- Go to: https://www.perplexity.ai/settings/api
- Click "Generate API Key"
- Copy key (starts with `pplx-`)

**2. Test (1 minute):**
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY" --test
```

**3. Run (choose speed):**

**Fast (30-60 minutes):**
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY" --parallel --concurrent 5
```

**Stable (3-6 hours):**
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY"
```

**Expected Result:** ~1,500 emails found (65-70%)

---

## 📊 All Methods Comparison

| Method | Cost | Time | Success | Setup |
|--------|------|------|---------|-------|
| **Perplexity API** ⭐ | **$1** | **30min-6hr** | **65-70%** | **2min** |
| Google API | $11 | 2-4hr | 50-60% | 5min |
| Manual (ChatGPT/Perplexity Pro) | $20 | 7-18hr | 70-75% | 0min |

---

## 📁 Files Created

- ✅ `find_emails_perplexity.py` - Main script (Perplexity API)
- ✅ `find_author_emails.py` - Alternative script (Google API)
- ✅ `PERPLEXITY_SETUP.md` - Detailed Perplexity guide
- ✅ `GOOGLE_API_SETUP.md` - Detailed Google guide
- ✅ `EMAIL_FINDER_COMPARISON.md` - Complete comparison

---

## 🎯 Output

**File:** `results/authors_with_emails_perplexity.json`

**Format:**
```json
{
  "summary": {
    "emails_found": 1450,
    "success_rate": "65.6%"
  },
  "authors": {
    "37085461083": {
      "name": "Mahdieh S. Sadabadi",
      "affiliation": "University of Manchester",
      "email_search": {
        "found": true,
        "email": "m.sadabadi@manchester.ac.uk",
        "source_url": "https://..."
      }
    }
  }
}
```

---

## ⚙️ Advanced Options

**Resume interrupted search:**
```bash
python3 find_emails_perplexity.py --api-key "pplx-xxx" --resume
```

**Limit to first 100:**
```bash
python3 find_emails_perplexity.py --api-key "pplx-xxx" --limit 100
```

**Monitor progress:**
```bash
tail -f results/perplexity_email_search.log
```

---

## 💡 Tips

1. **Start with test mode** to verify it works
2. **Use sequential mode** for first run (most stable)
3. **Run overnight** if you don't want to wait
4. **Check results** in `results/authors_with_emails_perplexity.json`

---

## ✅ You're Ready!

Just run:
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY" --test
```

Then:
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY"
```

Done! 🚀

For detailed info, see:
- `PERPLEXITY_SETUP.md` - Complete setup guide
- `EMAIL_FINDER_COMPARISON.md` - Method comparison
