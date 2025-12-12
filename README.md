# LinkedIn Job Scraper with AI-Powered Cover Letter Adaptation

An enhanced LinkedIn job scraper that searches for jobs by multiple titles and location, exports results to XLSX, and automatically generates personalized adapted cover letters using Groq's GPT-OSS-120B model.

## Features

- 🔍 **Multiple Job Titles Search**: Search for multiple job titles simultaneously (e.g., "Software Engineer, Data Scientist, Developer")
- 📍 **Location-Based Search**: Search for jobs in specific locations
- 📊 **XLSX Export**: Export the first 50 results to an XLSX file with a "Recommended Cover Letter" column
- ✍️ **AI Cover Letter Adaptation**: Automatically adapt your base cover letter template to match each job description using GPT-OSS-120B
- 📝 **CV Customization**: Optionally customize your CV's "About Me" section based on each job description
- 🤖 **Groq API Integration**: Fast LLM processing using Groq's GPT-OSS-120B model
- 🎯 **TOP 50 Results**: Scrapes the top 50 jobs per location for each job title

## Requirements

- Python 3.8+
- Chrome browser
- ChromeDriver (automatically managed by Selenium)
- Groq API key

## Installation

1. Clone or download this repository:
```bash
cd Linkedin-Job-Scrapper
```

2. Install required packages:
```bash
py -m pip install -r requirements.txt
```

3. **Groq API Key**: You will be prompted to enter your Groq API key when running the script (first step).

## Usage

### Interactive Mode (Recommended)

Run the main script:
```bash
py main.py
```

The script will prompt you for:
1. **Groq API Key** (first step - required)
2. LinkedIn email and password
3. Job title(s) - can enter multiple separated by commas (e.g., "Software Engineer, Data Scientist")
4. Location (e.g., "New York, NY")
5. Maximum results per title (default: 50)
6. Your base cover letter template (will be adapted for each job)
7. Optional: Additional context (achievements, company research, motivation)
8. Optional: Current CV "About Me" section
9. Export options

### Programmatic Usage

See `example_usage.py` for how to use the scraper in your own scripts.

## Cover Letter Adaptation

The scraper uses a sophisticated prompt to adapt your base cover letter template to each job:

- Analyzes job requirements, skills, and qualifications
- Matches them with your experience from the cover letter
- Reorganizes and rewrites to emphasize relevant points
- Uses keywords from the job description naturally
- Maintains professional tone matching company culture
- Keeps it concise (3-4 paragraphs, max 1 page)
- Includes strong opening showing genuine interest
- Provides concrete examples demonstrating you meet requirements
- Ends with compelling call to action

## Output Structure

The script creates the following directory structure:

```
output/
├── jobs/              # Job listings in JSON and TXT format (legacy)
├── cover_letters/     # Generated adapted cover letters (individual files)
├── cv_sections/      # Customized CV "About Me" sections (if enabled)
└── *.xlsx            # Main export file with jobs and cover letters
```

### XLSX File Columns

The exported XLSX file contains:
- **Title**: Job title
- **Company**: Company name
- **Location**: Job location
- **Posted Date**: When the job was posted
- **Link**: Direct link to the job posting
- **Description Snippet**: Brief job description
- **Recommended Cover Letter**: AI-adapted cover letter for this specific job
- **Scraped At**: Timestamp when the job was scraped

## Configuration

Edit `config.py` to customize:
- Output directories
- Model selection (default: `openai/gpt-oss-120b`)

## Important Notes

⚠️ **LinkedIn Terms of Service**: Please ensure your use of this scraper complies with LinkedIn's Terms of Service. Use responsibly and ethically.

⚠️ **Rate Limiting**: The script includes rate limiting for API calls. Be mindful of Groq API rate limits.

⚠️ **Credentials**: Never commit your LinkedIn credentials or API keys to version control. The API key is now prompted at runtime for security.

⚠️ **Cover Letter Template**: You must provide a base cover letter template. The AI will adapt this template for each job, so make sure it contains your relevant experience and skills.

## Troubleshooting

### ChromeDriver Issues
If you encounter ChromeDriver issues:
- Ensure Chrome browser is installed
- ChromeDriver should be automatically managed by Selenium
- If issues persist, download ChromeDriver manually and add to PATH

### Login Issues
- Make sure your LinkedIn credentials are correct
- LinkedIn may require 2FA - you may need to handle this manually
- Some accounts may be flagged for automated access

### API Issues
- Verify your Groq API key is correct
- Check your API quota/limits on Groq console
- Ensure you have internet connectivity
- The model used is `openai/gpt-oss-120b` - verify it's available on your Groq account

### No Jobs Found
- Verify your search terms
- Check if LinkedIn's page structure has changed
- Try different job titles or locations
- Ensure you're logged in correctly

### XLSX Export Issues
- Ensure `openpyxl` is installed: `py -m pip install openpyxl`
- Check that you have write permissions in the output directory

## Model Information

This scraper uses **GPT-OSS-120B** model via Groq API:
- Model identifier: `openai/gpt-oss-120b`
- Fast inference speeds
- High-quality cover letter adaptation
- Optimized for professional writing tasks

## License

This project is for educational purposes. Please respect LinkedIn's Terms of Service and use responsibly.

## Contributing

Feel free to fork this project and submit pull requests for improvements.

## Disclaimer

This tool is provided as-is. The authors are not responsible for any misuse or violations of LinkedIn's Terms of Service. Use at your own risk.
