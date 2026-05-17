"""
Naukri.com Job Scraper - JSON-LD Based
Extracts job data from structured JSON-LD data in the HTML
"""

import argparse
import requests
import json
import logging
from datetime import datetime
import re
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NaukriJSONLDScraper:
    def __init__(self):
        self.base_url = "https://www.naukri.com"
        self.search_url = "https://www.naukri.com/search"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
                normalized_url = href
            elif href.startswith('//'):
                normalized_url = 'https:' + href
            elif href.startswith('/'):
                normalized_url = urljoin(self.base_url, href)
            else:
                normalized_url = urljoin(self.base_url + '/', href)

            if normalized_url and 'naukri.com' in normalized_url:
                normalized_url = re.sub(r'(?<!:)//+', '/', normalized_url)
                return normalized_url
            else:
                if title:
                    title_slug = title.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')
                    return f"{self.base_url}/job-listings-{title_slug}"
                return None
        except Exception as e:
            logger.debug(f"Error normalizing URL '{href}': {e}")
            return None

    def _create_selenium_driver(self):
        """Create a Selenium WebDriver for detail page scraping."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

        return webdriver.Chrome(options=options)

    def _clean_html_text(self, html_text):
        if not html_text:
            return None

        from bs4 import BeautifulSoup
        return BeautifulSoup(html_text, 'html.parser').get_text(separator=' ', strip=True)

    def _extract_job_from_detail_page(self, driver, url):
        """Fetch the job detail page in Selenium and extract structured fields."""
        result = {}
        try:
            driver.get(url)
            driver.implicitly_wait(8)

            page_source = driver.page_source
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page_source, 'html.parser')
            jsonld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

            for script in jsonld_scripts:
                try:
                    jsonld_data = json.loads(script.string.strip())
                except Exception:
                    continue

                if isinstance(jsonld_data, dict) and jsonld_data.get('@type') == 'JobPosting':
                    result['company'] = None
                    hiring_org = jsonld_data.get('hiringOrganization') or {}
                    if isinstance(hiring_org, dict):
                        result['company'] = hiring_org.get('name') or hiring_org.get('identifier')

                    result['job_description'] = self._clean_html_text(jsonld_data.get('description'))
                    result['posted_date'] = jsonld_data.get('datePosted')
                    result['salary'] = None
                    base_salary = jsonld_data.get('baseSalary')
                    if isinstance(base_salary, dict):
                        salary_value = base_salary.get('value') or {}
                        if isinstance(salary_value, dict):
                            min_sal = salary_value.get('minValue')
                            max_sal = salary_value.get('maxValue')
                            currency = salary_value.get('currency')
                            if min_sal or max_sal:
                                salary_parts = []
                                if min_sal:
                                    salary_parts.append(str(min_sal))
                                if max_sal:
                                    salary_parts.append(str(max_sal))
                                salary_text = ' - '.join(salary_parts)
                                if currency:
                                    salary_text = f"{salary_text} {currency}"
                                result['salary'] = salary_text
                        elif isinstance(salary_value, str):
                            result['salary'] = salary_value
                    elif isinstance(base_salary, str):
                        result['salary'] = base_salary

                    result['skills'] = None
                    if 'skills' in jsonld_data:
                        if isinstance(jsonld_data['skills'], list):
                            result['skills'] = ', '.join(jsonld_data['skills'])
                        else:
                            result['skills'] = jsonld_data['skills']

                    result['experience'] = jsonld_data.get('experienceRequirements')
                    return result

        except Exception as e:
            logger.warning(f"Could not extract detail fields from {url}: {e}")

        return result

    def _populate_detail_fields(self, jobs):
        if not jobs:
            return jobs

        driver = None
        try:
            driver = self._create_selenium_driver()
            for job in jobs:
                if job.get('job_url'):
                    details = self._extract_job_from_detail_page(driver, job['job_url'])
                    if details:
                        for key, value in details.items():
                            if value and not job.get(key):
                                job[key] = value
        except Exception as e:
            logger.warning(f"Selenium detail scraping failed: {e}")
        finally:
            if driver:
                driver.quit()

        return jobs

    def _extract_job_from_jsonld(self, jsonld_data):
        """
        Extract job information from JSON-LD structured data
        """
        jobs = []

        if not jsonld_data or not isinstance(jsonld_data, dict):
            return jobs

        # Check if this is an ItemList with job listings
        if jsonld_data.get('@type') == 'ItemList' and 'itemListElement' in jsonld_data:
            for item in jsonld_data['itemListElement']:
                if isinstance(item, dict) and 'url' in item:
                    job_url = item['url']

                    # Create a basic job entry with the URL
                    job = {
                        'timestamp': datetime.now().isoformat(),
                        'title': None,  # Will be extracted from URL or page title
                        'company': None,
                        'experience': None,
                        'salary': None,
                        'job_description': None,
                        'job_url': self._normalize_job_url(job_url),
                        'company_type': None,
                        'skills': None,
                        'posted_date': None,
                        'location': None,
                        'role': None
                    }

                    # Try to extract title from URL
                    if job_url:
                        # URL format: https://www.naukri.com/job-listings-{title}-{company}-{location}-{exp}-{id}
                        url_parts = job_url.split('-')
                        if len(url_parts) > 3:
                            # Extract title (everything between job-listings- and the last few parts)
                            title_parts = url_parts[2:-3]  # Skip 'job' 'listings' and last 3 parts (location/exp/id)
                            job['title'] = ' '.join(title_parts).title()

                    jobs.append(job)

        return jobs

    def _scrape_search_page(self, role, location):
        """
        Scrape a single search page and extract jobs from JSON-LD
        """
        jobs = []

        # Build search parameters
        params = {
            'keyword': role,
            'location': location,
            'experience': self.experience,
        }

        logger.info(f"Fetching: {self.search_url} with params: {params}")

        try:
            response = self.session.get(self.search_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse HTML to find JSON-LD scripts
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all JSON-LD script tags
            jsonld_scripts = soup.find_all('script', {'type': 'application/ld+json'})

            for script in jsonld_scripts:
                try:
                    jsonld_data = json.loads(script.string.strip())
                    page_jobs = self._extract_job_from_jsonld(jsonld_data)
                    jobs.extend(page_jobs)
                except json.JSONDecodeError as e:
                    logger.debug(f"Failed to parse JSON-LD: {e}")
                    continue

            logger.info(f"Found {len(jobs)} jobs from JSON-LD data")

        except Exception as e:
            logger.error(f"Error scraping {role} in {location}: {e}")

        return jobs

    def scrape_all_jobs(self):
        """
        Scrape jobs for all role-location combinations
        """
        all_jobs = []

        for role in self.roles:
            for location in self.locations:
                logger.info(f"\nSearching for '{role}' in '{location}'...")

                jobs = self._scrape_search_page(role, location)
                for job in jobs:
                    job['role'] = role
                    job['location'] = location
                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs for {role} in {location}")

        # Populate additional fields from the detail pages when available
        all_jobs = self._populate_detail_fields(all_jobs)

        # Filter for FAANG companies if possible
        filtered_jobs = []
        for job in all_jobs:
            company_match = False
            job_text = f"{job.get('title', '')} {job.get('job_url', '')} {job.get('company', '')}".lower()

            for company in self.companies:
                if company.lower() in job_text:
                    company_match = True
                    if not job.get('company'):
                        job['company'] = company
                    break

            if company_match or not job.get('company'):
                filtered_jobs.append(job)

        self.job_data = filtered_jobs
        return filtered_jobs

    def save_to_json(self, filename=None):
        """
        Save job data to JSON file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_jsonld_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.job_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.job_data)} jobs to {filename}")
        return filename

    def save_to_csv(self, filename=None):
        """
        Save job data to CSV file
        """
        import csv

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"naukri_jobs_jsonld_{timestamp}.csv"

        if not self.job_data:
            logger.warning("No job data to save")
            return None

        # Get all unique keys
        fieldnames = set()
        for job in self.job_data:
            fieldnames.update(job.keys())

        fieldnames = sorted(fieldnames)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.job_data)

        logger.info(f"Saved {len(self.job_data)} jobs to {filename}")
        return filename


def parse_arguments():
    parser = argparse.ArgumentParser(description='Naukri JSON-LD scraper with prompt-based input')
    parser.add_argument('--profile', '-p', type=str, help='Job profile or role (comma-separated for multiple)')
    parser.add_argument('--location', '-l', type=str, help='Location or locations (comma-separated)')
    parser.add_argument('--experience', '-e', type=int, help='Years of experience')
    return parser.parse_args()


def prompt_if_missing(args):
    if not args.profile:
        args.profile = input('Enter job profile(s) (comma-separated, e.g. Data Scientist, Python Developer): ').strip()
    if not args.location:
        args.location = input('Enter location(s) (comma-separated, e.g. Chennai, Bangalore): ').strip()
    if not args.experience:
        experience_value = input('Enter years of experience (e.g. 11): ').strip()
        while experience_value and not experience_value.isdigit():
            experience_value = input('Please enter a valid number for years of experience: ').strip()
        args.experience = int(experience_value) if experience_value else None
    return args


def normalize_list(value):
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def main():
    args = parse_arguments()
    args = prompt_if_missing(args)

    if not args.profile or not args.location or not args.experience:
        print('Error: profile, location, and experience are required.')
        return

    scraper = NaukriJSONLDScraper()
    scraper.roles = normalize_list(args.profile)
    scraper.locations = normalize_list(args.location)
    scraper.experience = args.experience

    print("="*80)
    print("NAUKRI.COM JOB SCRAPER - JSON-LD BASED")
    print("="*80)
    print("\nSearching for:")
    print(f"   Roles: {', '.join(scraper.roles)}")
    print(f"   Experience: {scraper.experience}+ years")
    print(f"   Locations: {', '.join(scraper.locations)}")
    print(f"   Companies: {', '.join(scraper.companies)}")
    print("="*80)

    # Scrape jobs
    jobs = scraper.scrape_all_jobs()

    print(f"\n✅ Found {len(jobs)} total jobs")

    if jobs:
        # Save results
        json_file = scraper.save_to_json()
        csv_file = scraper.save_to_csv()

        print(f"\n📁 Results saved to:")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")

        # Show sample
        print("\n📋 Sample job:")
        sample = jobs[0]
        for key, value in sample.items():
            if value:
                print(f"   {key}: {value}")

    else:
        print("\n❌ No jobs found")

if __name__ == "__main__":
    main()