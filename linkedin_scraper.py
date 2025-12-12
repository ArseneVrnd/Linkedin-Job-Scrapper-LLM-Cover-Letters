"""
LinkedIn Job Scraper with location and title search
"""
import os
import time
import json
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
from config import JOBS_DIR, OUTPUT_DIR


class LinkedInJobScraper:
    def __init__(self, headless=False):
        """
        Initialize the LinkedIn Job Scraper
        
        Args:
            headless (bool): Run browser in headless mode
        """
        self.options = webdriver.ChromeOptions()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.driver = None
        self.jobs = []

    def start_driver(self):
        """Initialize the Chrome driver"""
        try:
            self.driver = webdriver.Chrome(options=self.options)
            self.driver.maximize_window()
            print("Chrome driver started successfully")
        except Exception as e:
            print(f"Error starting driver: {e}")
            raise

    def login(self, email, password):
        """
        Login to LinkedIn with captcha detection
        
        Args:
            email (str): LinkedIn email
            password (str): LinkedIn password
        """
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            email_input = self.driver.find_element(By.ID, "username")
            password_input = self.driver.find_element(By.ID, "password")
            
            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Check for captcha or challenge page
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            # Check for various captcha indicators
            captcha_indicators = [
                "challenge" in current_url,
                "captcha" in page_source,
                "verify" in current_url,
                "security" in current_url,
                "unusual activity" in page_source,
                "verify your identity" in page_source
            ]
            
            # Also check for captcha elements
            captcha_selectors = [
                "iframe[title*='captcha']",
                "iframe[title*='challenge']",
                "div[id*='captcha']",
                "div[class*='captcha']",
                "form[action*='challenge']"
            ]
            
            has_captcha = any(captcha_indicators)
            
            # Check for captcha elements in DOM
            if not has_captcha:
                for selector in captcha_selectors:
                    try:
                        captcha_elem = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if captcha_elem:
                            has_captcha = True
                            break
                    except:
                        continue
            
            if has_captcha:
                print("\n" + "="*80)
                print("CAPTCHA DETECTED")
                print("="*80)
                print("LinkedIn has requested a captcha or security verification.")
                print("Please resolve the captcha in the browser window.")
                print("Once you have completed the captcha and logged in successfully,")
                print("press Enter here to continue...")
                print("="*80)
                input()
                
                # Wait a bit more and verify login
                time.sleep(3)
                current_url = self.driver.current_url.lower()
                if "feed" in current_url or "linkedin.com/in/" in current_url or "jobs" in current_url:
                    print("Login successful after captcha resolution")
                else:
                    print("Warning: Please ensure you have successfully logged in.")
                    print("Continuing anyway...")
            else:
                # Verify normal login success
                if "feed" in current_url or "linkedin.com/in/" in current_url or "jobs" in current_url:
                    print("Login successful")
                else:
                    print("Login may not have completed. Please check the browser.")
                    
        except Exception as e:
            print(f"Login error: {e}")
            raise

    def search_jobs(self, titles, location, max_results=50):
        """
        Search for jobs on LinkedIn (supports multiple job titles)
        
        Args:
            titles (str or list): Job title(s) to search for (can be a single string or list of strings)
            location (str): Location to search in
            max_results (int): Maximum number of results per title to scrape (default: 50)
        """
        # Convert single title to list
        if isinstance(titles, str):
            titles = [titles]
        
        all_jobs = []
        
        for title in titles:
            print(f"\nSearching for '{title}' jobs in '{location}'...")
            title_jobs = self._search_single_title(title, location, max_results)
            all_jobs.extend(title_jobs)
            print(f"Found {len(title_jobs)} jobs for '{title}'")
        
        # Remove duplicates based on link
        seen_links = set()
        unique_jobs = []
        for job in all_jobs:
            job_link = job.get('link', '')
            if job_link and job_link not in seen_links:
                seen_links.add(job_link)
                unique_jobs.append(job)
        
        self.jobs = unique_jobs
        print(f"\nTotal unique jobs collected: {len(self.jobs)}")
        return self.jobs
    
    def _search_single_title(self, title, location, max_results=50):
        """
        Search for a single job title on LinkedIn
        
        Args:
            title (str): Job title to search for
            location (str): Location to search in
            max_results (int): Maximum number of results to scrape
        
        Returns:
            list: List of job dictionaries
        """
        try:
            # Navigate to jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Find and fill job title search box (try multiple selectors)
            title_input = None
            title_selectors = [
                "input[aria-label*='Search jobs']",
                "input[aria-label*='Search by title']",
                "input.jobs-search-box__text-input[aria-label*='Search']",
                "input[placeholder*='Search jobs']"
            ]
            
            for selector in title_selectors:
                try:
                    title_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not title_input:
                raise Exception("Could not find job title search input")
            
            title_input.clear()
            title_input.send_keys(title)
            time.sleep(1)
            
            # Find and fill location search box (try multiple selectors)
            location_input = None
            location_selectors = [
                "input[aria-label*='City, state, or zip code']",
                "input[aria-label*='Location']",
                "input.jobs-search-box__text-input[aria-label*='Location']",
                "input[placeholder*='Location']"
            ]
            
            for selector in location_selectors:
                try:
                    location_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not location_input:
                raise Exception("Could not find location search input")
            
            location_input.clear()
            location_input.send_keys(location)
            time.sleep(1)
            location_input.send_keys(Keys.RETURN)
            
            # Wait for results to load
            time.sleep(5)
            
            # Scroll and collect jobs
            title_jobs = []
            collected_count = 0
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while collected_count < max_results:
                # Get current page jobs (try multiple selectors)
                job_cards = []
                job_selectors = [
                    "div.job-search-card",
                    "li.jobs-search-results__list-item",
                    "div[data-job-id]",
                    "article.job-card-container"
                ]
                
                for selector in job_selectors:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if job_cards:
                        break
                
                for card in job_cards:
                    if collected_count >= max_results:
                        break
                    
                    try:
                        job_data = self._extract_job_data(card)
                        if job_data:
                            # Check for duplicates by link
                            job_link = job_data.get('link', '')
                            if job_link and not any(j.get('link') == job_link for j in title_jobs):
                                title_jobs.append(job_data)
                                collected_count += 1
                                print(f"Collected job {collected_count}/{max_results}: {job_data.get('title', 'N/A')}")
                    except Exception as e:
                        print(f"Error extracting job data: {e}")
                        continue
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check if we need to click "See more jobs" or if we've reached the end
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    # Try to click "See more jobs" button if available
                    try:
                        see_more = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='See more jobs']")
                        see_more.click()
                        time.sleep(3)
                    except:
                        break
                last_height = new_height
                
                if collected_count >= max_results:
                    break
            
            return title_jobs
            
        except Exception as e:
            print(f"Error searching jobs: {e}")
            raise

    def _extract_job_data(self, card):
        """
        Extract job data from a job card element
        
        Args:
            card: Selenium WebElement representing a job card
            
        Returns:
            dict: Job data dictionary
        """
        try:
            job_data = {}
            
            # Title (try multiple selectors)
            title_selectors = [
                "h3.base-search-card__title a",
                "h3.job-card-list__title a",
                "a.job-card-list__title-link",
                "h3 a[data-control-name='job_card_title_link']"
            ]
            for selector in title_selectors:
                try:
                    title_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['title'] = title_elem.text.strip()
                    job_data['link'] = title_elem.get_attribute('href')
                    break
                except:
                    continue
            if 'title' not in job_data:
                job_data['title'] = "N/A"
                job_data['link'] = "N/A"
            
            # Company (try multiple selectors)
            company_selectors = [
                "h4.base-search-card__subtitle a",
                "h4.job-card-container__company-name a",
                "a.job-card-container__link",
                "span.job-card-container__primary-description"
            ]
            for selector in company_selectors:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['company'] = company_elem.text.strip()
                    job_data['company_link'] = company_elem.get_attribute('href') or "N/A"
                    break
                except:
                    continue
            if 'company' not in job_data:
                job_data['company'] = "N/A"
                job_data['company_link'] = "N/A"
            
            # Location (try multiple selectors)
            location_selectors = [
                "span.job-search-card__location",
                "li.job-card-container__metadata-item",
                "span.job-card-container__metadata-item"
            ]
            for selector in location_selectors:
                try:
                    location_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['location'] = location_elem.text.strip()
                    break
                except:
                    continue
            if 'location' not in job_data:
                job_data['location'] = "N/A"
            
            # Posted date (try multiple selectors)
            date_selectors = [
                "time.job-search-card__listdate",
                "time.job-card-container__listed-date",
                "time[datetime]"
            ]
            for selector in date_selectors:
                try:
                    date_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['posted_date'] = date_elem.get_attribute('datetime') or date_elem.text.strip()
                    break
                except:
                    continue
            if 'posted_date' not in job_data:
                job_data['posted_date'] = "N/A"
            
            # Description snippet (try multiple selectors)
            desc_selectors = [
                "p.base-search-card__snippet",
                "p.job-card-container__description",
                "div.job-card-container__description"
            ]
            for selector in desc_selectors:
                try:
                    desc_elem = card.find_element(By.CSS_SELECTOR, selector)
                    job_data['description_snippet'] = desc_elem.text.strip()
                    break
                except:
                    continue
            if 'description_snippet' not in job_data:
                job_data['description_snippet'] = "N/A"
            
            job_data['scraped_at'] = datetime.now().isoformat()
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None

    def save_jobs_json(self, filename=None):
        """
        Save jobs to JSON file
        
        Args:
            filename (str): Optional filename, defaults to timestamp-based name
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.json"
        
        filepath = os.path.join(JOBS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        
        print(f"Jobs saved to {filepath}")
        return filepath

    def save_jobs_txt(self, filename=None):
        """
        Save jobs to text file
        
        Args:
            filename (str): Optional filename, defaults to timestamp-based name
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.txt"
        
        filepath = os.path.join(JOBS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, job in enumerate(self.jobs, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"Job #{i}\n")
                f.write(f"{'='*80}\n")
                f.write(f"Title: {job.get('title', 'N/A')}\n")
                f.write(f"Company: {job.get('company', 'N/A')}\n")
                f.write(f"Location: {job.get('location', 'N/A')}\n")
                f.write(f"Posted: {job.get('posted_date', 'N/A')}\n")
                f.write(f"Link: {job.get('link', 'N/A')}\n")
                f.write(f"Description: {job.get('description_snippet', 'N/A')}\n")
                f.write(f"Scraped at: {job.get('scraped_at', 'N/A')}\n")
        
        print(f"Jobs saved to {filepath}")
        return filepath

    def export_to_xlsx(self, filename=None, max_results=50, cover_letters=None):
        """
        Export jobs to XLSX file with cover letters
        
        Args:
            filename (str): Optional filename, defaults to timestamp-based name
            max_results (int): Maximum number of results to export (default: 50)
            cover_letters (dict): Dictionary mapping job links to cover letters
        """
        if not self.jobs:
            print("No jobs to export")
            return None
        
        # Limit to first 50 results
        jobs_to_export = self.jobs[:max_results]
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.xlsx"
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Prepare data for XLSX
        xlsx_data = []
        for job in jobs_to_export:
            job_link = job.get('link', '')
            cover_letter = cover_letters.get(job_link, 'N/A') if cover_letters else 'N/A'
            
            xlsx_data.append({
                'Title': job.get('title', 'N/A'),
                'Company': job.get('company', 'N/A'),
                'Location': job.get('location', 'N/A'),
                'Posted Date': job.get('posted_date', 'N/A'),
                'Link': job_link,
                'Description Snippet': job.get('description_snippet', 'N/A'),
                'Recommended Cover Letter': cover_letter,
                'Scraped At': job.get('scraped_at', 'N/A')
            })
        
        df = pd.DataFrame(xlsx_data)
        
        # Create Excel writer with formatting
        from openpyxl.utils import get_column_letter
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Jobs')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Jobs']
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(col)
                )
                # Set width with some padding, but limit for very long columns
                adjusted_width = min(max_length + 2, 100)
                column_letter = get_column_letter(idx)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Exported {len(jobs_to_export)} jobs to {filepath}")
        return filepath

    def close(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")


if __name__ == "__main__":
    # Example usage
    scraper = LinkedInJobScraper(headless=False)
    try:
        scraper.start_driver()
        # Note: You'll need to provide your LinkedIn credentials
        # scraper.login("your_email@example.com", "your_password")
        # scraper.search_jobs("Software Engineer", "New York, NY", max_results=50)
        # scraper.export_to_csv(max_results=50)
        # scraper.save_jobs_json()
        # scraper.save_jobs_txt()
    finally:
        scraper.close()

