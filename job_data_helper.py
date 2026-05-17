"""
Manual Job Entry Helper & Data Processor
Allows you to manually add jobs or process data from browser extensions
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobDataHelper:
    """Helper for manual job data entry and processing"""
    
    def __init__(self):
        self.template_file = 'jobs_template.csv'
        self.import_file = 'jobs_imported.csv'
        self.output_file = 'naukri_jobs_manual.csv'
        self.output_json = 'naukri_jobs_manual.json'
    
    def create_template(self):
        """Create a template CSV for manual data entry"""
        template_data = [
            {
                'timestamp': datetime.now().isoformat(),
                'role': 'Data Scientist',
                'location': 'Bangalore',
                'title': 'Data Scientist - ML/AI',
                'company': 'Google',
                'experience': '8-12 years',
                'salary': '₹30,00,000 - ₹45,00,000',
                'job_url': 'https://www.naukri.com/jobs/...',
                'posted_date': '2 days ago',
                'skills': 'Python, ML, SQL'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'role': 'Tableau Developer',
                'location': 'Chennai',
                'title': 'Senior Tableau Developer',
                'company': 'Amazon',
                'experience': '10+ years',
                'salary': '₹25,00,000 - ₹40,00,000',
                'job_url': 'https://www.naukri.com/jobs/...',
                'posted_date': '3 days ago',
                'skills': 'Tableau, Power BI, SQL'
            },
            {
                'timestamp': datetime.now().isoformat(),
                'role': 'Python Developer',
                'location': 'Bangalore',
                'title': 'Senior Python Backend Engineer',
                'company': 'Meta',
                'experience': '11 years',
                'salary': '₹28,00,000 - ₹50,00,000',
                'job_url': 'https://www.naukri.com/jobs/...',
                'posted_date': '1 day ago',
                'skills': 'Python, Django, FastAPI, AWS'
            }
        ]
        
        try:
            with open(self.template_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=template_data[0].keys())
                writer.writeheader()
                writer.writerows(template_data)
            logger.info(f"✓ Template created: {self.template_file}")
            print(f"\n✓ Created template file: {self.template_file}")
            print("  Edit this file and add more jobs, then run the import function")
        except Exception as e:
            logger.error(f"Error creating template: {e}")
    
    def import_from_csv(self, csv_file):
        """Import jobs from a CSV file (from browser extension export)"""
        try:
            jobs = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    job = self._normalize_job_data(row)
                    if job:
                        jobs.append(job)
            
            logger.info(f"✓ Imported {len(jobs)} jobs from {csv_file}")
            return jobs
        except Exception as e:
            logger.error(f"Error importing: {e}")
            return []
    
    def _normalize_job_data(self, row: Dict) -> Dict:
        """Normalize job data from various sources"""
        normalized = {
            'timestamp': datetime.now().isoformat(),
            'role': row.get('role', row.get('Role', 'Not specified')),
            'location': row.get('location', row.get('Location', '')),
            'title': row.get('title', row.get('Title', row.get('Job Title', ''))),
            'company': row.get('company', row.get('Company', row.get('Employer', ''))),
            'experience': row.get('experience', row.get('Experience', row.get('Exp', ''))),
            'salary': row.get('salary', row.get('Salary', row.get('CTC', ''))),
            'job_url': row.get('job_url', row.get('URL', row.get('Job URL', ''))),
            'posted_date': row.get('posted_date', row.get('Posted', row.get('Posted Date', ''))),
            'skills': row.get('skills', row.get('Skills', '')),
        }
        
        # Only return if has title or company
        return normalized if (normalized['title'] or normalized['company']) else None
    
    def interactive_entry(self):
        """Interactively enter job data"""
        jobs = []
        
        print("\n" + "="*80)
        print("MANUAL JOB ENTRY - Enter 'done' when finished")
        print("="*80 + "\n")
        
        while True:
            job = {}
            print(f"\n--- Job #{len(jobs) + 1} ---")
            
            job['timestamp'] = datetime.now().isoformat()
            
            job['title'] = input("Job Title (or 'done'): ").strip()
            if job['title'].lower() == 'done':
                break
            
            job['company'] = input("Company: ").strip()
            job['role'] = input("Role (Data Scientist/Tableau Dev/Python Dev): ").strip()
            job['location'] = input("Location: ").strip()
            job['experience'] = input("Experience Required: ").strip()
            job['salary'] = input("Salary: ").strip()
            job['job_url'] = input("Job URL: ").strip()
            job['posted_date'] = input("Posted Date: ").strip()
            job['skills'] = input("Skills (comma separated): ").strip()
            
            jobs.append(job)
            print("✓ Job added")
        
        return jobs
    
    def save_jobs(self, jobs: List[Dict], filename: str = None):
        """Save jobs to CSV and JSON"""
        if not filename:
            filename = self.output_file
        
        if not jobs:
            logger.warning("No jobs to save")
            return
        
        try:
            # Save CSV
            csv_file = filename if filename.endswith('.csv') else filename + '.csv'
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
                writer.writeheader()
                writer.writerows(jobs)
            logger.info(f"✓ Saved {len(jobs)} jobs to {csv_file}")
            print(f"✓ Saved to {csv_file}")
            
            # Save JSON
            json_file = filename.replace('.csv', '.json') if '.csv' in filename else filename + '.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved {len(jobs)} jobs to {json_file}")
            print(f"✓ Saved to {json_file}")
        
        except Exception as e:
            logger.error(f"Error saving: {e}")
    
    def merge_jobs(self, *csv_files) -> List[Dict]:
        """Merge multiple CSV files"""
        all_jobs = []
        
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                jobs = self.import_from_csv(csv_file)
                all_jobs.extend(jobs)
                print(f"✓ Merged {len(jobs)} jobs from {csv_file}")
        
        logger.info(f"✓ Total jobs after merge: {len(all_jobs)}")
        return all_jobs
    
    def display_summary(self, jobs: List[Dict]):
        """Display summary of imported jobs"""
        if not jobs:
            print("\nNo jobs to display")
            return
        
        print("\n" + "="*100)
        print(f"IMPORTED JOBS SUMMARY - Total: {len(jobs)}")
        print("="*100 + "\n")
        
        # Group by company
        companies = {}
        for job in jobs:
            company = job.get('company', 'Unknown')
            if company not in companies:
                companies[company] = []
            companies[company].append(job)
        
        for company, comp_jobs in sorted(companies.items()):
            print(f"\n{company} ({len(comp_jobs)} jobs)")
            print("-" * 80)
            for job in comp_jobs:
                print(f"  • {job.get('title', 'N/A')}")
                print(f"    Exp: {job.get('experience', 'N/A')} | Loc: {job.get('location', 'N/A')}")
                print(f"    Salary: {job.get('salary', 'N/A')}")


def main():
    """Main menu"""
    helper = JobDataHelper()
    
    while True:
        print("\n" + "="*60)
        print("JOB DATA HELPER - MANUAL ENTRY & IMPORT")
        print("="*60)
        print("1. Create Template CSV (for manual entry)")
        print("2. Import from CSV (from browser extension export)")
        print("3. Manually Enter Jobs")
        print("4. Merge Multiple CSV Files")
        print("5. View Last Imported Jobs")
        print("6. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            helper.create_template()
            print("\n📋 Edit the template file with your job data, then use option 2 to import")
        
        elif choice == '2':
            csv_file = input("\nEnter CSV filename to import (default: jobs_imported.csv): ").strip()
            if not csv_file:
                csv_file = 'jobs_imported.csv'
            
            if os.path.exists(csv_file):
                jobs = helper.import_from_csv(csv_file)
                if jobs:
                    helper.save_jobs(jobs)
                    helper.display_summary(jobs)
            else:
                print(f"❌ File not found: {csv_file}")
                print("   Options:")
                print(f"   1. Create template with option 1")
                print(f"   2. Export data from Naukri.com using browser extension")
                print(f"   3. Place exported file as: {csv_file}")
        
        elif choice == '3':
            jobs = helper.interactive_entry()
            if jobs:
                helper.save_jobs(jobs)
                helper.display_summary(jobs)
        
        elif choice == '4':
            print("\nEnter CSV filenames to merge (comma-separated):")
            files_input = input("Files: ").strip()
            if files_input:
                files = [f.strip() for f in files_input.split(',')]
                jobs = helper.merge_jobs(*files)
                if jobs:
                    helper.save_jobs(jobs, 'naukri_jobs_merged')
                    helper.display_summary(jobs)
        
        elif choice == '5':
            if os.path.exists(helper.output_file):
                jobs = helper.import_from_csv(helper.output_file)
                helper.display_summary(jobs)
            else:
                print(f"No data file found: {helper.output_file}")
        
        elif choice == '6':
            print("\nGoodbye!")
            break
        
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
