"""
Example usage of the LinkedIn Job Scraper
This script demonstrates how to use the scraper programmatically
"""
from linkedin_scraper import LinkedInJobScraper
from llm_helper import LLMHelper


def example_usage():
    """Example of how to use the scraper"""
    
    # Initialize scraper
    scraper = LinkedInJobScraper(headless=False)
    
    try:
        # Start browser
        scraper.start_driver()
        
        # Login (replace with your credentials)
        scraper.login(
            email="your_email@example.com",
            password="your_password"
        )
        
        # Search for jobs
        jobs = scraper.search_jobs(
            title="Software Engineer",
            location="New York, NY",
            max_results=50
        )
        
        # Save jobs locally
        scraper.save_jobs_json()
        scraper.save_jobs_txt()
        
        # Export to CSV
        scraper.export_to_csv(max_results=50)
        
        # Initialize LLM helper
        llm_helper = LLMHelper()
        
        # User information for cover letters
        user_info = {
            'name': 'John Doe',
            'experience': '5+ years of software development experience',
            'skills': 'Python, JavaScript, React, Node.js, AWS'
        }
        
        # Current CV About Me section
        current_about_me = """I am a dedicated software engineer with 5+ years of experience 
        in full-stack development. I specialize in Python and JavaScript, with expertise in 
        building scalable web applications using React and Node.js."""
        
        # Process first 5 jobs as example
        for job in jobs[:5]:
            print(f"\nProcessing: {job.get('title')} at {job.get('company')}")
            
            # Generate cover letter
            cover_letter = llm_helper.generate_cover_letter(job, user_info)
            llm_helper.save_cover_letter(cover_letter, job)
            
            # Customize CV section
            cv_section = llm_helper.customize_cv_about_me(job, current_about_me)
            llm_helper.save_cv_section(cv_section, job)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    example_usage()

