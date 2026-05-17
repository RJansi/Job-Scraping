"""
Naukri API-based Job Scraper
Uses Naukri's internal API for more reliable data extraction
"""

import requests
import json
import logging
from datetime import datetime
import csv
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaukriAPIClient:
    """
    Client for Naukri API - more reliable than HTML scraping
    """
    
    def __init__(self):
        self.base_api_url = "https://www.naukri.com/jobapi/v4"
        self.search_endpoint = f"{self.base_api_url}/search"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.naukri.com/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.roles = ['Data Scientist', 'Tableau Developer', 'Python Developer']
        self.experience = 11
        self.locations = ['Chennai', 'Bangalore']
        self.companies = ['Google', 'Amazon', 'Meta', 'Apple', 'Netflix']
    
    def search_jobs(self) -> List[Dict]:
        """Search for jobs via API"""
        logger.info("Starting API-based job search...")
        all_jobs = []
        
        for role in self.roles:
            for location in self.locations:
                logger.info(f"\n🔍 Searching for '{role}' in '{location}'...")
                jobs = self._api_search(role, location)
                all_jobs.extend(jobs)
                if jobs:
                    logger.info(f"✓ Found {len(jobs)} jobs via API")
        
        return all_jobs
    
    def _api_search(self, keyword: str, location: str) -> List[Dict]:
        """Perform API search"""
        jobs = []
        
        try:
            # Try multiple API endpoints
            endpoints = [
                f"{self.base_api_url}/search",
                "https://www.naukri.com/api/v1/search",
                "https://api.naukri.com/search",
            ]
            
            params = {
                'keyword': keyword,
                'location': location,
                'expn': self.experience,
                'pageNo': 1,
                'pageSize': 50,
            }
            
            for endpoint in endpoints:
                try:
                    logger.debug(f"Trying endpoint: {endpoint}")
                    response = self.session.get(endpoint, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        jobs = self._parse_api_response(data, keyword, location)
                        if jobs:
                            logger.info(f"✓ Successfully fetched from API")
                            return jobs
                except Exception as e:
                    logger.debug(f"  Endpoint failed: {e}")
                    continue
            
            # If no API works, try direct HTTP fetch
            logger.debug("API endpoints failed, trying HTTP search...")
            jobs = self._http_search_fallback(keyword, location)
            
        except Exception as e:
            logger.error(f"Error in API search: {e}")
        
        return jobs
    
    def _parse_api_response(self, data: Dict, keyword: str, location: str) -> List[Dict]:
        """Parse API response"""
        jobs = []
        
        try:
            # Handle different API response formats
            job_list = None
            
            if isinstance(data, dict):
                # Try multiple possible keys
                for key in ['jobs', 'jobPostings', 'results', 'data', 'jobList']:
                    if key in data:
                        job_list = data[key]
                        break
            
            if not job_list:
                return []
            
            for job_data in job_list[:50]:
                try:
                    job = self._extract_job_from_api(job_data, keyword, location)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.debug(f"Error parsing job: {e}")
        
        except Exception as e:
            logger.error(f"Error parsing API response: {e}")
        
        return jobs
    
    def _extract_job_from_api(self, job_data: Dict, keyword: str, location: str) -> Dict:
        """Extract job info from API data"""
        job = {
            'timestamp': datetime.now().isoformat(),
            'role': keyword,
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
            # Map common API field names
            title_keys = ['jobTitle', 'title', 'position', 'name']
            company_keys = ['companyName', 'company', 'organizationName']
            exp_keys = ['experience', 'experienceRequired', 'requiredExperience']
            salary_keys = ['salary', 'salaryRange', 'ctc', 'compensation']
            url_keys = ['jobUrl', 'url', 'jobLink', 'href']
            
            for key in title_keys:
                if key in job_data and job_data[key]:
                    job['title'] = str(job_data[key])
                    break
            
            for key in company_keys:
                if key in job_data and job_data[key]:
                    job['company'] = str(job_data[key])
                    break
            
            for key in exp_keys:
                if key in job_data and job_data[key]:
                    job['experience'] = str(job_data[key])
                    break
            
            for key in salary_keys:
                if key in job_data and job_data[key]:
                    job['salary'] = str(job_data[key])
                    break
            
            for key in url_keys:
                if key in job_data and job_data[key]:
                    job['job_url'] = str(job_data[key])
                    break
            
            if 'skills' in job_data:
                if isinstance(job_data['skills'], list):
                    job['skills'] = ', '.join(job_data['skills'])
                else:
                    job['skills'] = str(job_data['skills'])
            
            return job if job.get('title') or job.get('company') else None
        
        except Exception as e:
            logger.debug(f"Error extracting job: {e}")
            return None
    
    def _http_search_fallback(self, keyword: str, location: str) -> List[Dict]:
        """Fallback HTTP search"""
        jobs = []
        
        try:
            url = "https://www.naukri.com/search"
            params = {
                'keyword': keyword,
                'location': location,
                'experience': self.experience,
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Try to extract JSON data embedded in HTML
            text = response.text
            
            # Look for JSON data in script tags or API responses
            import re
            json_matches = re.findall(r'<script[^>]*>.*?"jobs".*?</script>', text, re.DOTALL)
            
            for match in json_matches:
                try:
                    json_str = re.search(r'\{.*\}', match)
                    if json_str:
                        data = json.loads(json_str.group())
                        jobs = self._parse_api_response(data, keyword, location)
                        if jobs:
                            break
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"HTTP fallback failed: {e}")
        
        return jobs
    
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
    
    def save_results(self, jobs: List[Dict]):
        """Save results"""
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        try:
            csv_file = 'naukri_jobs_api.csv'
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
            logger.info(f"✓ Saved to {csv_file}")
            
            json_file = 'naukri_jobs_api.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved to {json_file}")
        
        except Exception as e:
            logger.error(f"Error saving: {e}")


def main():
    """Run API-based scraper"""
    print("\n" + "="*100)
    print("NAUKRI.COM JOB SCRAPER - API VERSION")
    print("="*100 + "\n")
    print("🚀 Using Naukri API for more reliable data extraction...")
    
    try:
        client = NaukriAPIClient()
        jobs = client.search_jobs()
        
        if jobs:
            logger.info(f"\n✓ Total jobs found: {len(jobs)}")
            faang_jobs = client.filter_by_company(jobs)
            logger.info(f"✓ FAANG jobs: {len(faang_jobs)}")
            
            jobs_to_save = faang_jobs if faang_jobs else jobs
            client.save_results(jobs_to_save)
            
            print("\n" + "="*100)
            print(f"✓ Found {len(jobs_to_save)} jobs")
            print("="*100 + "\n")
            
            for idx, job in enumerate(jobs_to_save[:10], 1):
                print(f"#{idx}. {job.get('title', 'N/A')}")
                print(f"    Company: {job.get('company', 'N/A')}")
                print(f"    Location: {job.get('location', 'N/A')}\n")
        else:
            logger.warning("❌ No jobs found via API")
    
    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
