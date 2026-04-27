# Quick Setup Guide: PawPal AI with Google Gemini

## Step 1: Get Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"**
3. Copy the key (looks like: `AIza...`)

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `google-generativeai>=0.3.0` (Gemini SDK)
- `streamlit>=1.30` (UI framework)
- `pytest>=7.0` (Testing)
- `python-dotenv>=1.0` (Environment variables)

## Step 3: Set API Key

Choose one method:

### Method A: Environment Variable
```bash
# Linux/macOS
export GEMINI_API_KEY="AIza..."

# Windows (Command Prompt)
set GEMINI_API_KEY=AIza...

# Windows (PowerShell)
$env:GEMINI_API_KEY="AIza..."
```

### Method B: .env File (Recommended)
Create `.env` file in project root:
```
GEMINI_API_KEY=AIza...
```

Then in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Step 4: Run Application

```bash
streamlit run pawpal/app.py
```

## Step 5: Test It Works

Try in the Streamlit UI:
1. Add a pet
2. Add some tasks
3. Click "Generate schedule"
4. See AI explanation powered by Gemini!

---

## Troubleshooting

### "GEMINI_API_KEY environment variable not set"
- ✅ Verify you set the environment variable correctly
- ✅ Check no typos in key
- ✅ Try restarting your terminal/IDE

### "Unable to generate AI explanation"
- ✅ Check internet connection
- ✅ Verify API key is valid
- ✅ Check API quota at: https://makersuite.google.com/app/apikey
- ✅ Ensure Gemini API is enabled in Google Cloud

### Response is generic/short
- ✅ This is normal! Gemini may generate shorter responses
- ✅ Check knowledge base has species info in `pawpal/knowledge_base.json`
- ✅ Try adding more detail to pet names/task descriptions

---

## Key Changes from OpenAI

| Feature | Before (OpenAI) | After (Gemini) |
|---------|---|---|
| **API Key** | OPENAI_API_KEY | GEMINI_API_KEY |
| **Library** | openai | google-generativeai |
| **Model** | gpt-3.5-turbo | gemini-pro |
| **Call** | ChatCompletion.create() | model.generate_content() |

---

## Support Resources

- **Gemini Docs**: https://ai.google.dev/
- **API Key**: https://makersuite.google.com/app/apikey
- **Pricing**: Free tier available + pay-as-you-go
- **Status**: https://status.cloud.google.com/

---

**Ready to go!** 🚀
