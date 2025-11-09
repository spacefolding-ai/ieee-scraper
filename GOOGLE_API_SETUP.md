# Google Custom Search API Setup Guide

## Why Use the API?

The Google Custom Search API is more reliable than web scraping because:
- ✅ No blocking issues
- ✅ Faster and more accurate
- ✅ 100 free searches per day
- ✅ Can upgrade for more searches

---

## Setup Steps (5 minutes)

### Step 1: Get API Key

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create a new project (or select existing)
3. Click **"+ CREATE CREDENTIALS"** → **"API key"**
4. Copy your API key (e.g., `AIzaSyC...`)
5. Click **"Enable APIs and Services"**
6. Search for **"Custom Search API"** and enable it

### Step 2: Create Custom Search Engine

1. Go to: https://programmablesearchengine.google.com/
2. Click **"Add"** to create new search engine
3. In "Sites to search":
   - Enter `*` (search the entire web)
4. Name it: "Author Email Finder"
5. Click **"Create"**
6. Click **"Customize"** on your new search engine
7. Copy the **Search engine ID** (e.g., `a1b2c3d4e5f...`)

### Step 3: Configure Settings

In the Programmable Search Engine settings:
1. Turn **ON**: "Search the entire web"
2. Turn **OFF**: "Image search"
3. Click **"Update"**

---

## Usage

### Test with API:

```bash
python3 find_author_emails.py --test \
  --api-key "YOUR_API_KEY" \
  --cx "YOUR_SEARCH_ENGINE_ID"
```

### Process all authors:

```bash
python3 find_author_emails.py \
  --api-key "YOUR_API_KEY" \
  --cx "YOUR_SEARCH_ENGINE_ID"
```

### Process specific number:

```bash
python3 find_author_emails.py \
  --api-key "YOUR_API_KEY" \
  --cx "YOUR_SEARCH_ENGINE_ID" \
  --limit 100
```

### Resume interrupted search:

```bash
python3 find_author_emails.py \
  --api-key "YOUR_API_KEY" \
  --cx "YOUR_SEARCH_ENGINE_ID" \
  --resume
```

---

## API Limits

- **Free tier**: 100 searches/day
- **Paid tier**: $5 per 1000 searches (up to 10,000/day)

### For 2,211 authors:
- **Free**: 22 days (100 authors/day)
- **Paid**: 1-2 days (~$11 total)

---

## Save Credentials

Create a file `google_credentials.txt`:

```
API_KEY=AIzaSyC...
SEARCH_ENGINE_ID=a1b2c3d4e5f...
```

Then run:

```bash
export GOOGLE_API_KEY=$(grep API_KEY google_credentials.txt | cut -d= -f2)
export GOOGLE_CX=$(grep SEARCH_ENGINE_ID google_credentials.txt | cut -d= -f2)

python3 find_author_emails.py --api-key "$GOOGLE_API_KEY" --cx "$GOOGLE_CX"
```

---

## Troubleshooting

**"API key not valid"**
- Make sure Custom Search API is enabled in Google Cloud Console

**"Daily limit exceeded"**
- Wait 24 hours or upgrade to paid tier

**No results found**
- Check that "Search the entire web" is enabled
- Verify the search engine ID is correct

---

## Alternative: Manual Search

If you don't want to use the API, you can manually search for emails using the output file structure and update `authors_with_emails.json` manually.

