"""
Optimized Naukri.com Scraper using Selenium
Faster and more reliable version with better element detection
"""

import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
import json
import csv
from typing import List, Dict
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizedNaukriScraper:
    """
    Optimized Naukri scraper with faster loading and better element detection
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
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--start-maximized')
            
            # Add preferences to load images faster
            prefs = {
                'profile.managed_default_content_settings.images': 2,  # Don't load images
                'profile.managed_default_content_settings.plugins': 2,
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(15)
            logger.info("✓ WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize WebDriver: {e}")
            raise
    
    def search_jobs(self) -> List[Dict]:
        """Search for jobs using Selenium"""
        self._initialize_driver()
        all_jobs = []
        
        try:
            for role in self.roles:
                for location in self.locations:
                    logger.info(f"\n🔍 Searching for '{role}' in '{location}'...")
                    jobs = self._search_with_selenium(role, location)
                    all_jobs.extend(jobs)
                    if jobs:
                        logger.info(f"✓ Found {len(jobs)} jobs")
                    time.sleep(1)  # Shorter delay
            
            return all_jobs
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("✓ WebDriver closed")
    
    def _search_with_selenium(self, role: str, location: str) -> List[Dict]:
        """Perform search with Selenium with optimized loading"""
        jobs = []
        try:
            search_url = f"{self.base_url}/search"
            logger.info(f"Loading: {search_url}")
            
            try:
                self.driver.get(search_url)
            except Exception as e:
                logger.warning(f"Page load timeout (partial load): {e}")
            
            # Brief wait for initial page
            time.sleep(2)
            
            # Set search parameters using direct input
            try:
                # Find and fill keyword search box
                keyword_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='keyword'], input[placeholder*='Keyword'], input[type='text']")
                if keyword_inputs:
                    keyword_inputs[0].clear()
                    keyword_inputs[0].send_keys(role)
                    logger.debug(f"Entered keyword: {role}")
                    time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Could not set keyword: {e}")
            
            try:
                # Find and fill location search box
                location_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='location'], input[placeholder*='Location']")
                if location_inputs:
                    location_inputs[0].clear()
                    location_inputs[0].send_keys(location)
                    logger.debug(f"Entered location: {location}")
                    time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Could not set location: {e}")
            
            # Wait for job cards to load
            time.sleep(3)
            
            # Scroll to trigger lazy loading
            for _ in range(2):
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(0.5)
            
            # Extract jobs from page HTML
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all job containers
            job_selectors = [
                'article.jobTuple',
                'article[data-job-id]',
                'div.jobTuple',
                'li[data-job-id]'
            ]
            
            job_elements = []
            for selector in job_selectors:
                job_elements = soup.select(selector)
                if len(job_elements) > 0:
                    logger.debug(f"Found {len(job_elements)} jobs with selector: {selector}")
                    break
            
            # Parse job information
            for idx, job_elem in enumerate(job_elements[:30]):  # Limit to 30 per search
                try:
                    job_info = self._parse_job_element(job_elem, role, location)
                    if job_info and job_info.get('title'):
                        jobs.append(job_info)
                except Exception as e:
                    logger.debug(f"Error parsing job {idx}: {e}")
            
            logger.debug(f"Extracted {len(jobs)} valid jobs from {len(job_elements)} elements")
            
        except Exception as e:
            logger.error(f"✗ Error in search: {e}")
        
        return jobs
    
    def _parse_job_element(self, element, role: str, location: str) -> Dict:
        """Parse individual job element"""
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
            # Try to extract title
            title_elem = element.select_one('a[href*="/jobs/"], .jobTitle, a.jd')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
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
                        job['job_url'] = urljoin(self.base_url, href)
                    else:
                        # Try to construct full URL
                        job['job_url'] = urljoin(self.base_url + '/', href)
                    
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
                            job['job_url'] = f"{self.base_url}/job-listings-{title_slug}"
                else:
                    job['job_url'] = None
            
            # Extract company
            company_elem = element.select_one('.companyName, .cName, a.cName')
            if company_elem:
                job['company'] = company_elem.get_text(strip=True)
            
            # Extract experience
            exp_text = element.get_text()
            if 'year' in exp_text.lower():
                import re
                exp_match = re.search(r'(\d+)\s*(?:to|-|yrs?)', exp_text.lower())
                if exp_match:
                    job['experience'] = exp_match.group(0)
            
            # Extract salary
            salary_elem = element.select_one('.salary, .salaryText, .ctc')
            if salary_elem:
                job['salary'] = salary_elem.get_text(strip=True)
            
            # Extract posted date
            date_elem = element.select_one('.postedDate, .date, .posted')
            if date_elem:
                job['posted_date'] = date_elem.get_text(strip=True)
            
            return job if job.get('title') or job.get('company') else None
        
        except Exception as e:
            logger.debug(f"Error parsing element: {e}")
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
    
    def save_results(self, jobs: List[Dict], base_filename='naukri_jobs'):
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
            logger.info(f"✓ Saved {len(jobs)} jobs to {csv_file}")
            
            # Save to JSON
            json_file = f"{base_filename}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved {len(jobs)} jobs to {json_file}")
        
        except Exception as e:
            logger.error(f"Error saving results: {e}")
    
    def display_results(self, jobs: List[Dict]):
        """Display results"""
        if not jobs:
            print("\n❌ No jobs found")
            return
        
        print("\n" + "="*100)
        print(f"✓ FOUND {len(jobs)} JOBS")
        print("="*100 + "\n")
        
        for idx, job in enumerate(jobs[:10], 1):
            print(f"#{idx}. {job.get('title', 'N/A')}")
            print(f"    Company: {job.get('company', 'N/A')}")
            print(f"    Location: {job.get('location', 'N/A')}")
            print(f"    Salary: {job.get('salary', 'N/A')}")
            print(f"    URL: {job.get('job_url', 'N/A')}")
            print()
        
        if len(jobs) > 10:
            print(f"... and {len(jobs) - 10} more jobs")


def main():
    """Run optimized scraper"""
    print("\n" + "="*100)
    print("NAUKRI.COM JOB SCRAPER - OPTIMIZED SELENIUM VERSION")
    print("="*100 + "\n")
    print("🚀 Starting scraper...")
    print("   Searching for: Data Scientist, Tableau Developer, Python Developer")
    print("   Experience: 11+ years")
    print("   Locations: Chennai, Bangalore")
    print("   Companies: Google, Amazon, Meta, Apple, Netflix\n")
    
    try:
        scraper = OptimizedNaukriScraper(headless=True)
        jobs = scraper.search_jobs()
        
        if jobs:
            logger.info(f"\n✓ Total jobs found: {len(jobs)}")
            faang_jobs = scraper.filter_by_company(jobs)
            logger.info(f"✓ FAANG jobs found: {len(faang_jobs)}")
            
            if faang_jobs:
                scraper.save_results(faang_jobs)
                scraper.display_results(faang_jobs)
            else:
                logger.warning("No FAANG company jobs found in results")
                scraper.save_results(jobs, 'naukri_jobs_all')
                scraper.display_results(jobs)
        else:
            logger.warning("\n❌ No jobs found - website structure may have changed")
            logger.warning("Try running: python debug_scraper.py")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
