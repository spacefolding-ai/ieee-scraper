# Perplexity API Email Finder - Setup Guide

## 🚀 Quick Start

### Step 1: Get Perplexity API Key (2 minutes)

1. Go to: https://www.perplexity.ai/settings/api
2. Sign in or create account
3. Click **"Generate API Key"**
4. Copy your key (format: `pplx-xxxxx`)

**Free Credits:** 5M tokens (~5,000 searches) 🎉

---

### Step 2: Test the Script (1 minute)

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --test
```

This tests with 10 authors to verify everything works.

---

### Step 3: Run for All Authors

Choose your method:

#### **Option A: Sequential (Slower, More Stable)** ⭐ Recommended

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE"
```

- **Time:** ~3-6 hours
- **Safe:** No rate limit issues
- **Simple:** Set and forget

#### **Option B: Parallel (Faster, May Hit Limits)**

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --parallel \
  --concurrent 5
```

- **Time:** ~30-60 minutes
- **Fast:** 5 requests at once
- **Risk:** May hit rate limits

Adjust `--concurrent` (1-10):
- `--concurrent 3` = safer, slower
- `--concurrent 5` = balanced ⭐
- `--concurrent 10` = faster, risky

---

## 📊 Expected Results

### For 2,211 Authors:

| Mode | Time | Success Rate | Cost |
|------|------|--------------|------|
| Sequential | 3-6 hrs | 60-70% | ~$1 |
| Parallel (5) | 45-90 min | 60-70% | ~$1 |
| Parallel (10) | 22-45 min | 50-60% | ~$1 |

---

## 🔧 Advanced Options

### Resume Interrupted Search

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --resume
```

### Process Specific Number

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --limit 100
```

### Custom Input/Output Files

```bash
python3 find_emails_perplexity.py \
  --api-key "pplx-YOUR_KEY_HERE" \
  --input "custom_authors.json" \
  --output "custom_emails.json"
```

---

## 📁 Output Files

### Main Output: `results/authors_with_emails_perplexity.json`

```json
{
  "summary": {
    "total_authors": 2211,
    "processed": 2211,
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
        "source_url": "https://research.manchester.ac.uk/...",
        "response": "The email address for Dr. Mahdieh S. Sadabadi...",
        "citations": ["https://research.manchester.ac.uk/..."]
      }
    }
  }
}
```

### Log File: `results/perplexity_email_search.log`

Contains detailed progress and any errors.

---

## 💡 Tips for Best Results

### 1. **Start with Sequential Mode**
Most stable and reliable. Let it run overnight.

### 2. **Monitor Progress**
```bash
tail -f results/perplexity_email_search.log
```

### 3. **Check Success Rate**
```bash
grep "✓ Found" results/perplexity_email_search.log | wc -l
```

### 4. **Resume if Interrupted**
Script auto-saves every 25-50 authors. Just add `--resume`.

### 5. **Handle Failures**
After completion, extract authors without emails:
```bash
python3 << 'EOF'
import json
with open('results/authors_with_emails_perplexity.json', 'r') as f:
    data = json.load(f)
not_found = [a for a in data['authors'].values() 
             if not a['email_search'].get('found')]
print(f"Not found: {len(not_found)}")
EOF
```

---

## ⚠️ Troubleshooting

### "Invalid API key"
- Check you copied the full key including `pplx-` prefix
- Verify at https://www.perplexity.ai/settings/api

### "Rate limit exceeded"
- Use sequential mode instead of parallel
- Reduce `--concurrent` number
- Add `time.sleep()` delays (already included)

### Low success rate (<50%)
- Normal for some institutions (no public emails)
- Try Google API for failed cases
- Manual verification for important contacts

### Script crashes
- Use `--resume` to continue
- Check log file for specific errors
- Reduce `--concurrent` if using parallel

---

## 💰 Cost Tracking

Perplexity charges per token:
- Free: 5M tokens
- After: $0.20 per 1M tokens

**Estimated usage:**
- Per author: ~1,000 tokens
- 2,211 authors: ~2.2M tokens = **$0.44**
- Well within free tier! 🎉

Check usage at: https://www.perplexity.ai/settings/api

---

## 🎯 Workflow Recommendation

**Day 1 Afternoon:**
```bash
# Start sequential run
python3 find_emails_perplexity.py --api-key "pplx-xxxx"
# Let run for 3-6 hours
```

**Day 1 Evening:**
- Review results
- ~1,500 emails found (65%)

**Day 2 (Optional):**
- Use Google API for remaining ~700 authors
- Manual verification of key contacts

**Total time:** 1-2 days
**Total cost:** ~$1
**Expected emails:** ~1,500-1,800 (65-80%)

---

## 📞 Support

Issues? Check:
1. Log file: `results/perplexity_email_search.log`
2. API status: https://status.perplexity.ai/
3. Your usage: https://www.perplexity.ai/settings/api

---

## ✅ You're Ready!

Just run:
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY" --test
```

Then when satisfied:
```bash
python3 find_emails_perplexity.py --api-key "pplx-YOUR_KEY"
```

Good luck! 🚀






