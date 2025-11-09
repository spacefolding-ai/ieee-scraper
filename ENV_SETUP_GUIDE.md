# .env File Setup Guide

## 🔐 Secure API Key Storage

Instead of typing your API key every time, store it in a `.env` file.

---

## ⚡ Quick Setup (1 minute)

### Step 1: Copy the example file
```bash
cp .env.example .env
```

### Step 2: Edit .env file
Open `.env` in your editor and replace the placeholder:

```bash
# .env file
PERPLEXITY_API_KEY=pplx-YOUR-ACTUAL-API-KEY-HERE
```

### Step 3: Install python-dotenv (optional but recommended)
```bash
pip3 install python-dotenv
```

### Step 4: Run without --api-key flag
```bash
# Before (with API key in command)
python3 find_emails_perplexity.py --api-key "pplx-xxx" --test

# After (reads from .env automatically)
python3 find_emails_perplexity.py --test
```

Done! ✅

---

## 🔑 Three Ways to Provide API Key

The script supports three methods (in priority order):

### 1. Command Line (Highest Priority)
```bash
python3 find_emails_perplexity.py --api-key "pplx-xxx"
```

### 2. Environment Variable
```bash
export PERPLEXITY_API_KEY="pplx-xxx"
python3 find_emails_perplexity.py
```

### 3. .env File (Recommended ⭐)
```bash
# Create .env file with:
PERPLEXITY_API_KEY=pplx-xxx

# Then just run:
python3 find_emails_perplexity.py
```

---

## 📝 .env File Format

Your `.env` file should look like this:

```bash
# Perplexity API Configuration
PERPLEXITY_API_KEY=pplx-1a2b3c4d5e6f7g8h9i0j

# Google Custom Search API (optional)
GOOGLE_API_KEY=AIzaSyC...
GOOGLE_SEARCH_ENGINE_ID=a1b2c3d4e5f...
```

---

## 🛡️ Security

✅ **Safe:** `.env` is in `.gitignore` (won't be committed to git)  
✅ **Private:** Only on your local machine  
✅ **Convenient:** No need to type API key every time  

**Never commit `.env` to git!** Always use `.env.example` as a template.

---

## 🔧 Troubleshooting

### "API key not found" error

**If you see this error:**
```
Perplexity API key not found!
Please provide it via:
  1. Command line: --api-key 'pplx-xxx'
  2. Environment variable: export PERPLEXITY_API_KEY='pplx-xxx'
  3. .env file: PERPLEXITY_API_KEY=pplx-xxx
```

**Check:**
1. `.env` file exists in project root
2. `.env` contains: `PERPLEXITY_API_KEY=pplx-xxx` (no spaces around `=`)
3. API key starts with `pplx-`
4. No quotes needed in .env file

### python-dotenv not installed

If you don't have `python-dotenv`, the script will still work with:
- Command line: `--api-key` flag
- Environment variable: `export PERPLEXITY_API_KEY=...`

To install:
```bash
pip3 install python-dotenv
```

---

## 📋 Complete Example

```bash
# 1. Copy template
cp .env.example .env

# 2. Edit .env and add your key
# PERPLEXITY_API_KEY=pplx-your-key-here

# 3. (Optional) Install dotenv
pip3 install python-dotenv

# 4. Run without typing key
python3 find_emails_perplexity.py --test

# 5. Full run
python3 find_emails_perplexity.py
```

---

## ✅ Verification

Check if your .env is working:

```bash
# Should run without asking for API key
python3 find_emails_perplexity.py --test

# Should see "Loading authors from..." not "API key not found!"
```

---

## 🎯 Benefits

✅ **Secure** - API key not in command history  
✅ **Convenient** - No need to type it every time  
✅ **Safe** - .gitignore prevents accidental commits  
✅ **Flexible** - Can still override with --api-key if needed  

Perfect for daily use! 🚀
