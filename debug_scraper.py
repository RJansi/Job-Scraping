"""
Debug script to inspect Naukri.com HTML structure
This helps identify the correct CSS selectors for job listings
"""

import requests
from bs4 import BeautifulSoup
import json

def debug_naukri():
    """Fetch and analyze the HTML structure of Naukri.com"""
    
    url = "https://www.naukri.com/search"
    params = {
        'keyword': 'Data Scientist',
        'location': 'Chennai',
        'experience': 11,
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    print("Fetching Naukri.com...")
    print(f"URL: {url}")
    print(f"Parameters: {params}\n")
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.content)} bytes\n")
        
        # Save raw HTML for inspection
        with open('debug_response.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("✓ Raw HTML saved to: debug_response.html\n")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all potential job card containers
        print("="*80)
        print("SEARCHING FOR JOB CONTAINERS")
        print("="*80)
        
        selectors_to_try = [
            'article.jobTuple',
            'article',
            '.jobTuple',
            '.jobCard',
            '.job-card',
            '[data-job-id]',
            'div.job',
            'div[class*="job"]',
            'li[class*="job"]',
        ]
        
        results = {}
        for selector in selectors_to_try:
            elements = soup.select(selector)
            results[selector] = len(elements)
            if elements:
                print(f"✓ {selector}: Found {len(elements)} elements")
        
        print("\n" + "="*80)
        print("ANALYZING PAGE STRUCTURE")
        print("="*80)
        
        # Get the title to verify page loaded
        title = soup.find('title')
        print(f"Page Title: {title.string if title else 'Not found'}")
        
        # Look for main content areas
        main_content = soup.find('main') or soup.find('div', {'id': 'main'})
        print(f"Main Content Found: {bool(main_content)}")
        
        # Search for any div with job-related keywords
        print("\nSearching for elements with job-related class names...")
        job_related = soup.find_all(class_=lambda x: x and 'job' in x.lower())
        print(f"Elements with 'job' in class name: {len(job_related)}")
        
        if job_related:
            print("\nFirst 5 job-related elements:")
            for idx, elem in enumerate(job_related[:5], 1):
                print(f"  {idx}. {elem.name} - class: {elem.get('class', [])}")
        
        # Look for common job listing patterns
        print("\n" + "="*80)
        print("CHECKING FOR COMMON PATTERNS")
        print("="*80)
        
        # Check for job links
        job_links = soup.find_all('a', {'href': lambda x: x and '/jobs/' in x.lower()})
        print(f"Job links found: {len(job_links)}")
        
        if job_links:
            print("First 5 job links:")
            for idx, link in enumerate(job_links[:5], 1):
                print(f"  {idx}. {link.text[:50]}")
                print(f"     URL: {link.get('href')}")
        
        # Check for company names
        companies = soup.find_all(class_=lambda x: x and 'company' in x.lower())
        print(f"\nCompany-related elements: {len(companies)}")
        
        # Check page structure
        print("\n" + "="*80)
        print("PAGE STRUCTURE")
        print("="*80)
        
        # Count major elements
        print(f"Total <a> tags: {len(soup.find_all('a'))}")
        print(f"Total <article> tags: {len(soup.find_all('article'))}")
        print(f"Total <span> tags: {len(soup.find_all('span'))}")
        print(f"Total <div> tags: {len(soup.find_all('div'))}")
        
        # Get all unique classes containing 'job'
        job_classes = set()
        for elem in soup.find_all(class_=True):
            for cls in elem.get('class', []):
                if 'job' in cls.lower():
                    job_classes.add(cls)
        
        if job_classes:
            print("\nUnique classes with 'job':")
            for cls in sorted(job_classes):
                print(f"  - {cls}")
        
        # Save analysis results
        analysis = {
            'url': url,
            'status_code': response.status_code,
            'content_length': len(response.content),
            'title': title.string if title else None,
            'job_links_found': len(job_links),
            'job_container_results': results,
            'page_loaded': response.status_code == 200 and len(response.content) > 1000,
        }
        
        with open('debug_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        print("\n✓ Analysis saved to: debug_analysis.json")
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        
        if response.status_code == 200:
            if len(job_links) > 0:
                print("✓ Website returned results - try using job links as selectors")
            else:
                print("⚠ Website may be returning dynamic content - try Selenium scraper")
                print("  Run: python naukri_selenium_scraper.py")
        else:
            print("✗ Website returned error status code")
            print("  The website might be blocking requests")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("  Check your internet connection and try again")

if __name__ == "__main__":
    debug_naukri()
