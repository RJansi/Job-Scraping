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

                # Filter for FAANG companies if possible
                filtered_jobs = []
                for job in jobs:
                    job['role'] = role
                    job['location'] = location

                    # Basic company filtering (if company name is in title/URL)
                    company_match = False
                    job_text = f"{job.get('title', '')} {job.get('job_url', '')}".lower()

                    for company in self.companies:
                        if company.lower() in job_text:
                            company_match = True
                            job['company'] = company
                            break

                    # Include job if it's from a FAANG company or if we can't determine (to be safe)
                    if company_match or not job.get('company'):
                        filtered_jobs.append(job)

                all_jobs.extend(filtered_jobs)
                logger.info(f"Found {len(filtered_jobs)} relevant jobs for {role} in {location}")

        self.job_data = all_jobs
        return all_jobs

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