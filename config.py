import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Configuration - will be set by user input
GROQ_API_KEY = None

# Output directories
OUTPUT_DIR = "output"
JOBS_DIR = os.path.join(OUTPUT_DIR, "jobs")
COVER_LETTERS_DIR = os.path.join(OUTPUT_DIR, "cover_letters")
CV_SECTIONS_DIR = os.path.join(OUTPUT_DIR, "cv_sections")

# Create directories if they don't exist
for directory in [OUTPUT_DIR, JOBS_DIR, COVER_LETTERS_DIR, CV_SECTIONS_DIR]:
    os.makedirs(directory, exist_ok=True)

