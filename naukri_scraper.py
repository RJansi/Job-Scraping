"""
Naukri.com Job Scraper
Extracts job listings for Data Scientist, Tableau Developer, and Python Developer
with 11+ years experience in Chennai/Bangalore from FAANG companies
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import csv
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaukriScraper:
    def __init__(self):
        self.base_url = "https://www.naukri.com"
        self.search_url = "https://www.naukri.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.naukri.com/',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.job_data = []
        
        # Configuration
        self.roles = ['Data Scientist', 'Tableau Developer', 'Python Developer']
        self.experience = 11
        self.locations = ['Chennai', 'Bangalore']
        self.companies = ['Google', 'Amazon', 'Meta', 'Apple', 'Netflix']  # FAANG companies
    
    def _normalize_job_url(self, href, title=None):
        """
        Normalize job URL to ensure it's a complete, valid Naukri.com URL
        """
        if not href:
            return None
        
        try:
            # Handle different URL formats
            if href.startswith('http'):
                # Already a full URL
                normalized_url = href
            elif href.startswith('//'):
                # Protocol-relative URL
                normalized_url = 'https:' + href
            elif href.startswith('/'):
                # Relative URL from root
                normalized_url = urljoin(self.base_url, href)
            else:
                # Try to construct full URL
                normalized_url = urljoin(self.base_url + '/', href)
            
            # Additional validation - ensure it's a valid Naukri job URL
            if normalized_url and 'naukri.com' in normalized_url:
                # Clean up any double slashes (except after protocol)
                import re
                normalized_url = re.sub(r'(?<!:)//+', '/', normalized_url)
                return normalized_url
            else:
                # If not a valid Naukri URL, try to construct one from title
                if title:
                    title_slug = title.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')
                    return f"{self.base_url}/job-listings-{title_slug}"
                return None
        except Exception as e:
            logger.debug(f"Error normalizing URL '{href}': {e}")
            return None
        
    def search_jobs(self):
        """
        Search for jobs on Naukri.com with specified parameters
        """
        logger.info("Starting job search...")
        logger.info(f"Roles: {self.roles}")
        logger.info(f"Experience: {self.experience}+ years")
        logger.info(f"Locations: {self.locations}")
        logger.info(f"Companies: {self.companies}")
        
        all_jobs = []
        
        for role in self.roles:
            for location in self.locations:
                logger.info(f"\nSearching for '{role}' in '{location}'...")
                jobs = self._search_with_filters(role, location)
                all_jobs.extend(jobs)
                time.sleep(2)  # Respectful delay between requests
        
        return all_jobs
    
    def _search_with_filters(self, role, location):
        """
        Search with specific filters
        Note: Naukri.com uses dynamic JavaScript rendering, so this may need Selenium
        """
        try:
            # Build search parameters
            params = {
                'keyword': role,
                'location': location,
                'experience': self.experience,
            }
            
            logger.info(f"Fetching: {self.search_url}?keyword={role}&location={location}")
            response = self.session.get(self.search_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = self._parse_job_listings(soup, role, location)
            
            # If no jobs found, provide helpful message
            if len(jobs) == 0:
                logger.warning(f"No jobs parsed for {role} in {location}. Naukri uses JavaScript rendering.")
                logger.warning("Recommendation: Use naukri_selenium_scraper.py for better results")
            
            logger.info(f"Found {len(jobs)} jobs for {role} in {location}")
            return jobs
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data for {role} in {location}: {e}")
            return []
    
    def _parse_job_listings(self, soup, role, location):
        """
        Parse job listings from the HTML
        Naukri.com uses JavaScript rendering, so results may be limited here
        """
        jobs = []
        
        # Try multiple selectors for job cards (includes newer structures)
        job_selectors = [
            'article.jobTuple',
            'article[data-jobid]',
            'article[data-job-id]',
            'div.jobTuple',
            'div.jobCard',
            '.jobItem',
            'div[data-job-id]',
            'li[data-job-id]',
            'a[href*="/jobs/"]'  # Fallback to job links
        ]
        
        job_elements = []
        for selector in job_selectors:
            job_elements = soup.select(selector)
            if job_elements:
                logger.debug(f"Found {len(job_elements)} elements using selector: {selector}")
                if len(job_elements) > 5:  # Only use if we found reasonable number
                    logger.info(f"Using selector: {selector}")
                    break
        
        for job_element in job_elements[:50]:  # Limit to first 50
            try:
                job_info = self._extract_job_info(job_element, role, location)
                if job_info:
                    jobs.append(job_info)
            except Exception as e:
                logger.debug(f"Error parsing job element: {e}")
                continue
        
        return jobs
    
    def _extract_job_info(self, element, role, location):
        """
        Extract individual job information
        """
        job = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'location': location,
            'title': None,
            'company': None,
            'experience': None,
            'salary': None,
            'job_description': None,
            'job_url': None,
            'company_type': None,
            'skills': None,
            'posted_date': None,
        }
        
        try:
            # Extract job title
            title_elem = element.select_one('a.jobTitle, .jobTitle, a[href*="/jobs/"]')
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
                href = title_elem.get('href', '')
                job['job_url'] = self._normalize_job_url(href, job['title'])
                
                # Debug logging for URL issues
                if job['job_url']:
                    logger.debug(f"Extracted URL: {job['job_url']} for job: {job['title'][:50]}")
                else:
                    job['job_url'] = None
            
            # Extract company name
            company_elem = element.select_one('.companyName, .company, a.companyName')
            if company_elem:
                company_name = company_elem.get_text(strip=True)
                job['company'] = company_name
                
                # Check if company is FAANG
                for faang_company in self.companies:
                    if faang_company.lower() in company_name.lower():
                        break
            
            # Extract experience
            exp_elem = element.select_one('.expWrapper, .experience, .exp')
            if exp_elem:
                job['experience'] = exp_elem.get_text(strip=True)
            
            # Extract salary
            salary_elem = element.select_one('.salary, .salaryText, .sal')
            if salary_elem:
                job['salary'] = salary_elem.get_text(strip=True)
            
            # Extract job description snippet
            desc_elem = element.select_one('.jobDescription, .description, p')
            if desc_elem:
                job['job_description'] = desc_elem.get_text(strip=True)[:200]
            
            # Extract posted date
            date_elem = element.select_one('.postedDate, .posted, .date')
            if date_elem:
                job['posted_date'] = date_elem.get_text(strip=True)
            
            # Extract skills
            skills_elem = element.select('.skills, .skill, .tags')
            if skills_elem:
                skills = [skill.get_text(strip=True) for skill in skills_elem]
                job['skills'] = ', '.join(skills)
            
            return job if job.get('title') or job.get('company') else None
            
        except Exception as e:
            logger.error(f"Error extracting job info: {e}")
            return None
    
    def filter_by_company(self, jobs):
        """
        Filter jobs to only include FAANG companies
        """
        filtered_jobs = []
        
        for job in jobs:
            if job.get('company'):
                for company in self.companies:
                    if company.lower() in job['company'].lower():
                        filtered_jobs.append(job)
                        break
        
        return filtered_jobs
    
    def save_to_csv(self, jobs, filename='naukri_jobs.csv'):
        """
        Save jobs to CSV file
        """
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        try:
            keys = jobs[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(jobs)
            logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def save_to_json(self, jobs, filename='naukri_jobs.json'):
        """
        Save jobs to JSON file
        """
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
    
    def display_results(self, jobs):
        """
        Display results in a formatted manner
        """
        if not jobs:
            logger.warning("No jobs found")
            return
        
        print("\n" + "="*100)
        print(f"TOTAL JOBS FOUND: {len(jobs)}")
        print("="*100 + "\n")
        
        for idx, job in enumerate(jobs, 1):
            print(f"Job #{idx}")
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Company: {job.get('company', 'N/A')}")
            print(f"  Experience: {job.get('experience', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Salary: {job.get('salary', 'N/A')}")
            print(f"  Posted: {job.get('posted_date', 'N/A')}")
            print(f"  URL: {job.get('job_url', 'N/A')}")
            print(f"  Skills: {job.get('skills', 'N/A')}")
            print(f"  Description: {job.get('job_description', 'N/A')}")
            print("-"*100 + "\n")


def main():
    """
    Main execution function
    """
    print("\n" + "="*80)
    print("NAUKRI.COM JOB SCRAPER - BASIC VERSION")
    print("="*80)
    print("\n⚠️  NOTE: Naukri.com uses JavaScript for job listings.")
    print("   This basic scraper may not find results.")
    print("   RECOMMENDED: Use Selenium scraper instead")
    print("   Run: python naukri_selenium_scraper.py")
    print("   Or: python run.py (and select option 2)")
    print("\n" + "="*80 + "\n")
    
    scraper = NaukriScraper()
    
    try:
        # Search for jobs
        jobs = scraper.search_jobs()
        
        if jobs:
            logger.info(f"\nTotal jobs found: {len(jobs)}")
            
            # Filter by FAANG companies
            faang_jobs = scraper.filter_by_company(jobs)
            logger.info(f"FAANG company jobs: {len(faang_jobs)}")
            
            # Save results
            scraper.save_to_csv(faang_jobs)
            scraper.save_to_json(faang_jobs)
            
            # Display results
            scraper.display_results(faang_jobs)
        else:
            logger.warning("\n" + "="*80)
            logger.warning("❌ NO JOBS FOUND")
            logger.warning("="*80)
            logger.warning("This is expected for the basic scraper on Naukri.com")
            logger.warning("\nPLEASE USE THE SELENIUM SCRAPER INSTEAD:")
            logger.warning("  Option 1: python naukri_selenium_scraper.py")
            logger.warning("  Option 2: python run.py  (then select option 2)")
            logger.warning("="*80 + "\n")
    
    except Exception as e:
        logger.error(f"Error in main execution: {e}")


if __name__ == "__main__":
    main()
