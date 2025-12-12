# Quick Setup Guide

## Installation Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install ChromeDriver:**
   - ChromeDriver is usually managed automatically by Selenium
   - If you encounter issues, download from: https://chromedriver.chromium.org/
   - Make sure Chrome browser is installed

3. **Configure API Key:**
   - The Groq API key is already set in `config.py`
   - You can also create a `.env` file (see `.env.example`)

## Running the Scraper

### Interactive Mode (Recommended)
```bash
python main.py
```

This will prompt you for:
- LinkedIn credentials
- Job search parameters (title, location)
- Your information for cover letters
- Export options

### Programmatic Mode
See `example_usage.py` for how to use the scraper in your own scripts.

## Output Files

All output files are saved in the `output/` directory:
- `output/jobs/` - Job listings (JSON and TXT)
- `output/cover_letters/` - Generated cover letters
- `output/cv_sections/` - Customized CV sections
- `output/*.csv` - CSV exports

## Troubleshooting

### "ChromeDriver not found"
- Ensure Chrome browser is installed
- Selenium should manage ChromeDriver automatically
- If issues persist, install ChromeDriver manually

### "Login failed"
- Check your LinkedIn credentials
- LinkedIn may require manual 2FA verification
- Some accounts may be flagged for automated access

### "API Error"
- Verify your Groq API key is correct
- Check your internet connection
- Review API quota/limits on Groq console

### "No jobs found"
- Verify your search terms
- Check if LinkedIn's page structure has changed
- Try different job titles or locations

## Notes

- The scraper opens a Chrome browser window (set `headless=True` to run in background)
- Rate limiting is included for API calls
- First 50 results are exported to CSV by default
- Cover letters and CV sections are generated for all scraped jobs (up to 50)

