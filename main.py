"""
Main script to run the LinkedIn Job Scraper with LLM integration
"""
import os
import time
from linkedin_scraper import LinkedInJobScraper
from llm_helper import LLMHelper


def main():
    """Main function to run the job scraper and generate cover letters/CV sections"""
    
    print("="*80)
    print("LinkedIn Job Scraper with AI-Powered Cover Letter & CV Customization")
    print("="*80)
    print()
    
    # Step 1: Get Groq API Key (FIRST STEP)
    print("STEP 1: Groq API Configuration")
    print("-"*80)
    groq_api_key = input("Enter your Groq API key: ").strip()
    
    if not groq_api_key:
        print("Error: Groq API key is required. Exiting...")
        return
    
    # API key will be passed directly to LLMHelper
    
    # Get user inputs
    print("\nPlease provide the following information:")
    print("-"*80)
    
    # Entire CV (moved earlier in the flow)
    print("\nCV Information:")
    print("Enter your entire CV (press Enter twice on an empty line to finish):")
    print("(Include all sections: About Me, Experience, Education, Skills, etc.)")
    entire_cv = ""
    empty_line_count = 0
    while True:
        line = input()
        if line.strip() == "":
            empty_line_count += 1
            if empty_line_count >= 2:
                break
        else:
            empty_line_count = 0
            entire_cv += line + "\n"
    
    entire_cv = entire_cv.strip()
    
    if not entire_cv:
        print("Warning: No CV provided. CV customization will be skipped.")
    
    # Extract About Me section from CV if possible (for backward compatibility)
    current_about_me = ""
    if entire_cv:
        # Try to extract About Me section (look for common headers)
        about_me_keywords = ["about me", "about", "summary", "profile", "overview"]
        lines = entire_cv.split('\n')
        in_about_section = False
        about_lines = []
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            # Check if this line is an About Me header
            if any(keyword in line_lower for keyword in about_me_keywords) and len(line.strip()) < 50:
                in_about_section = True
                continue
            # Check if we hit another major section (usually capitalized or has colons)
            if in_about_section:
                if line.strip() and (line.strip().isupper() or ':' in line or line.strip().startswith('#')):
                    # Might be a new section, but continue if it's short
                    if len(line.strip()) < 50:
                        break
                about_lines.append(line)
        
        if about_lines:
            current_about_me = '\n'.join(about_lines).strip()
        else:
            # If no About Me section found, use first paragraph or first few lines
            first_paragraph = entire_cv.split('\n\n')[0] if '\n\n' in entire_cv else '\n'.join(entire_cv.split('\n')[:5])
            current_about_me = first_paragraph.strip()
    
    # Base cover letter template
    print("\nCover Letter Template:")
    print("Enter your base cover letter template (press Enter twice on an empty line to finish):")
    print("(This will be adapted for each job)")
    base_cover_letter = ""
    empty_line_count = 0
    while True:
        line = input()
        if line.strip() == "":
            empty_line_count += 1
            if empty_line_count >= 2 and base_cover_letter:
                break
        else:
            empty_line_count = 0
            base_cover_letter += line + "\n"
    
    base_cover_letter = base_cover_letter.strip()
    
    if not base_cover_letter:
        print("Warning: No cover letter template provided. Cover letters will be generated from scratch.")
    
    # Additional context (optional)
    print("\nAdditional Context (optional, press Enter to skip):")
    achievements = input("Specific achievements or projects to highlight: ").strip()
    company_research = input("Company research you've done: ").strip()
    motivation = input("Why you're particularly interested in these roles: ").strip()
    
    additional_context = {}
    if achievements:
        additional_context['achievements'] = achievements
    if company_research:
        additional_context['company_research'] = company_research
    if motivation:
        additional_context['motivation'] = motivation
    
    # Job search parameters - Support multiple job titles
    print("\nJob Search Parameters:")
    print("You can enter multiple job titles separated by commas (e.g., 'Software Engineer, Data Scientist, Developer')")
    job_titles_input = input("Enter job title(s) to search for: ").strip()
    
    # Parse multiple job titles
    if ',' in job_titles_input:
        job_titles = [title.strip() for title in job_titles_input.split(',')]
    else:
        job_titles = [job_titles_input]
    
    location = input("Enter location (e.g., 'New York, NY'): ").strip()
    
    # Number of results per title (TOP 50 per location)
    try:
        max_results = int(input("Enter maximum number of results per job title (default 50): ").strip() or "50")
    except ValueError:
        max_results = 50
    
    # LinkedIn credentials (moved to end, before starting browser)
    print("\nLinkedIn Login:")
    email = input("Enter your LinkedIn email: ").strip()
    password = input("Enter your LinkedIn password: ").strip()
    
    # Export options
    print("\nExport Options:")
    generate_cover_letters = input("Generate adapted cover letters for all jobs? (y/n, default y): ").strip().lower() != 'n'
    customize_cv = input("Customize CV 'About Me' section for all jobs? (y/n, default n): ").strip().lower() == 'y'
    
    print("\n" + "="*80)
    print("Starting job scraping...")
    print("="*80)
    
    # Initialize scraper
    scraper = LinkedInJobScraper(headless=False)
    llm_helper = LLMHelper(api_key=groq_api_key)
    
    try:
        # Start browser and login
        scraper.start_driver()
        scraper.login(email, password)
        
        # Search for jobs (supports multiple titles, TOP 50 per location)
        print(f"\nSearching for {len(job_titles)} job title(s) in '{location}'...")
        print(f"Job titles: {', '.join(job_titles)}")
        jobs = scraper.search_jobs(job_titles, location, max_results=max_results)
        
        if not jobs:
            print("No jobs found. Exiting...")
            return
        
        # Generate cover letters
        cover_letters_dict = {}
        if generate_cover_letters:
            print("\n" + "="*80)
            print("Generating AI-powered adapted cover letters...")
            print("="*80)
            
            # Limit to first 50 for LLM processing
            jobs_to_process = jobs[:50]
            
            for i, job in enumerate(jobs_to_process, 1):
                print(f"\nProcessing job {i}/{len(jobs_to_process)}: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                
                print("  → Adapting cover letter...")
                try:
                    if base_cover_letter:
                        cover_letter = llm_helper.adapt_cover_letter(job, base_cover_letter, additional_context)
                    else:
                        # Fallback if no template provided
                        cover_letter = "Cover letter template not provided. Please provide a base cover letter template."
                    
                    job_link = job.get('link', '')
                    if job_link:
                        cover_letters_dict[job_link] = cover_letter
                    
                    # Save individual cover letter file
                    llm_helper.save_cover_letter(cover_letter, job)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"  ✗ Error generating cover letter: {e}")
                    job_link = job.get('link', '')
                    if job_link:
                        cover_letters_dict[job_link] = f"Error: {str(e)}"
        
        # Customize CV sections
        if customize_cv and entire_cv:
            print("\n" + "="*80)
            print("Customizing CV 'About Me' sections...")
            print("="*80)
            
            jobs_to_process = jobs[:50]
            
            for i, job in enumerate(jobs_to_process, 1):
                print(f"\nProcessing job {i}/{len(jobs_to_process)}: {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
                
                print("  → Customizing CV 'About Me' section...")
                try:
                    cv_section = llm_helper.customize_cv_about_me(job, current_about_me, entire_cv)
                    llm_helper.save_cv_section(cv_section, job)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"  ✗ Error customizing CV section: {e}")
        
        # Export to XLSX with cover letters
        print("\nExporting to XLSX...")
        scraper.export_to_xlsx(max_results=50, cover_letters=cover_letters_dict)
        
        print("\n" + "="*80)
        print("Process completed successfully!")
        print("="*80)
        print(f"\nSummary:")
        print(f"  - Jobs scraped: {len(jobs)}")
        print(f"  - Job titles searched: {', '.join(job_titles)}")
        print(f"  - Location: {location}")
        print(f"  - XLSX exported to: output/")
        if generate_cover_letters:
            print(f"  - Cover letters saved to: output/cover_letters/")
        if customize_cv:
            print(f"  - CV sections saved to: output/cv_sections/")
        print()
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
