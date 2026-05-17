"""
Alternative Naukri Scraper using Selenium for JavaScript-rendered content
This version handles dynamic content loading on Naukri.com
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import json
import csv
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaukriSeleniumScraper:
    """
    Advanced Naukri scraper using Selenium for JavaScript-rendered content
    """
    
    def __init__(self, headless=True):
        self.base_url = "https://www.naukri.com"
        self.roles = ['Data Scientist', 'Tableau Developer', 'Python Developer']
        self.experience = 11
        self.locations = ['Chennai', 'Bangalore']
        self.companies = ['Google', 'Amazon', 'Meta', 'Apple', 'Netflix']
        self.driver = None
        self.headless = headless
        self.job_data = []
        
    def _initialize_driver(self):
        """Initialize Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def search_jobs(self) -> List[Dict]:
        """
        Search for jobs using Selenium
        """
        self._initialize_driver()
        all_jobs = []
        
        try:
            for role in self.roles:
                for location in self.locations:
                    logger.info(f"Searching for '{role}' in '{location}' using Selenium...")
                    jobs = self._search_with_selenium(role, location)
                    all_jobs.extend(jobs)
                    time.sleep(2)
            
            return all_jobs
        finally:
            if self.driver:
                self.driver.quit()
    
    def _search_with_selenium(self, role: str, location: str) -> List[Dict]:
        """
        Perform search with Selenium
        """
        jobs = []
        try:
            # Build search URL with parameters
            search_url = f"{self.base_url}/search?keyword={role}&location={location}&experience={self.experience}"
            logger.info(f"Navigating to: {search_url}")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Scroll down to trigger lazy loading
            logger.info("Scrolling to load job listings...")
            for _ in range(3):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(1)
            
            wait = WebDriverWait(self.driver, 15)
            
            try:
                # Wait for job listings to appear - try multiple selectors
                job_selectors = [
                    "article.jobTuple",
                    "article[data-job-id]",
                    "div[data-job-id]",
                    "a[href*='/jobs/']"
                ]
                
                job_cards = []
                for selector in job_selectors:
                    try:
                        job_cards = wait.until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                        )
                        if len(job_cards) > 0:
                            logger.info(f"Found {len(job_cards)} job cards using selector: {selector}")
                            break
                    except:
                        continue
                
                if not job_cards:
                    logger.warning(f"No job cards found. Page may need different selectors.")
                    # Try to get all article elements
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, "article")
                    logger.info(f"Found {len(job_cards)} article elements")
                
                logger.info(f"Total job cards to process: {len(job_cards)}")
                
                # Extract data from each card
                for idx, card in enumerate(job_cards[:50]):  # Limit to first 50
                    try:
                        job_info = self._extract_job_info_selenium(card, role, location)
                        if job_info:
                            jobs.append(job_info)
                    except Exception as e:
                        logger.debug(f"Error extracting job {idx}: {e}")
                
            except Exception as e:
                logger.warning(f"Timeout waiting for job cards: {e}")
                logger.info("Trying alternative approach...")
        
        except Exception as e:
            logger.error(f"Error searching for {role} in {location}: {e}")
        
        logger.info(f"Extracted {len(jobs)} jobs successfully")
        return jobs
    
    def _extract_job_info_selenium(self, element, role: str, location: str) -> Dict:
        """
        Extract job information from Selenium element
        """
        job = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'location': location,
            'title': None,
            'company': None,
            'experience': None,
            'salary': None,
            'skills': None,
            'job_url': None,
            'posted_date': None,
        }
        
        try:
            # Extract title - try multiple selectors
            title_elem = None
            title_selectors = ['a.jobTitle', '.jobTitle', 'a[href*="/jobs/"]', 'h2', 'h3']
            
            for selector in title_selectors:
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if title_elem and title_elem.text.strip():
                        break
                except:
                    continue
            
            if title_elem:
                job['title'] = title_elem.text.strip()
                try:
                    href = title_elem.get_attribute('href')
                    if href:
                        # Handle different URL formats
                        if href.startswith('http'):
                            # Already a full URL
                            job['job_url'] = href
                        elif href.startswith('//'):
                            # Protocol-relative URL
                            job['job_url'] = 'https:' + href
                        elif href.startswith('/'):
                            # Relative URL from root
                            job['job_url'] = 'https://www.naukri.com' + href
                        else:
                            # Try to construct full URL
                            job['job_url'] = 'https://www.naukri.com/' + href
                        
                        # Additional validation - ensure it's a valid Naukri job URL
                        if job['job_url'] and 'naukri.com' in job['job_url']:
                            # Clean up any double slashes (except after protocol)
                            import re
                            job['job_url'] = re.sub(r'(?<!:)//+', '/', job['job_url'])
                        else:
                            # If not a valid Naukri URL, try to construct one
                            if job['title']:
                                # Create a search-based URL as fallback
                                title_slug = job['title'].lower().replace(' ', '-').replace('/', '-')
                                job['job_url'] = f"https://www.naukri.com/job-listings-{title_slug}"
                    else:
                        job['job_url'] = None
                except:
                    job['job_url'] = None
            
            # Extract company - try multiple selectors
            company_elem = None
            company_selectors = ['.companyName', '.company', 'a.companyName', '[data-company-name]']
            
            for selector in company_selectors:
                try:
                    company_elem = element.find_element(By.CSS_SELECTOR, selector)
                    if company_elem and company_elem.text.strip():
                        break
                except:
                    continue
            
            if company_elem:
                company_text = company_elem.text.strip()
                job['company'] = company_text
            
            # Extract experience
            try:
                exp_elem = element.find_element(By.CSS_SELECTOR, ".expWrapper, .experience, [data-experience]")
                job['experience'] = exp_elem.text.strip()
            except:
                pass
            
            # Extract salary
            try:
                salary_elem = element.find_element(By.CSS_SELECTOR, ".salary, .salaryText, [data-salary]")
                job['salary'] = salary_elem.text.strip()
            except:
                pass
            
            # Extract posted date
            try:
                date_elem = element.find_element(By.CSS_SELECTOR, ".postedDate, .posted, [data-posted]")
                job['posted_date'] = date_elem.text.strip()
            except:
                pass
            
            # Extract skills
            try:
                skills_elems = element.find_elements(By.CSS_SELECTOR, ".skills, .skill, .tags, [data-skill]")
                if skills_elems:
                    skills = [s.text.strip() for s in skills_elems if s.text.strip()]
                    job['skills'] = ', '.join(skills)
            except:
                pass
            
            # Return only if we have at least title or company
            return job if (job.get('title') and job['title']) or (job.get('company') and job['company']) else None
        
        except Exception as e:
            logger.debug(f"Error extracting job info: {e}")
            return None
    
    def filter_by_company(self, jobs: List[Dict]) -> List[Dict]:
        """Filter jobs by FAANG companies"""
        filtered = []
        for job in jobs:
            if job.get('company'):
                for company in self.companies:
                    if company.lower() in job['company'].lower():
                        filtered.append(job)
                        break
        return filtered
    
    def save_results(self, jobs: List[Dict], base_filename='naukri_jobs_selenium'):
        """Save results to CSV and JSON"""
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        try:
            # Save to CSV
            csv_file = f"{base_filename}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
            logger.info(f"Saved {len(jobs)} jobs to {csv_file}")
            
            # Save to JSON
            json_file = f"{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {json_file}")
        
        except Exception as e:
            logger.error(f"Error saving results: {e}")


def main():
    """Run Selenium-based scraper"""
    try:
        scraper = NaukriSeleniumScraper(headless=True)
        jobs = scraper.search_jobs()
        
        if jobs:
            logger.info(f"Total jobs found: {len(jobs)}")
            faang_jobs = scraper.filter_by_company(jobs)
            logger.info(f"FAANG jobs found: {len(faang_jobs)}")
            scraper.save_results(faang_jobs)
        else:
            logger.warning("No jobs found")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
