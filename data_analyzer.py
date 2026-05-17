"""
Data Analysis and Utilities for Naukri Job Scraping Results
"""

import json
import csv
import pandas as pd
from datetime import datetime
import logging
from typing import List, Dict
from collections import Counter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NaukriDataAnalyzer:
    """Analyze and process scraped job data"""
    
    def __init__(self, json_file=None, csv_file=None):
        self.jobs = []
        self.df = None
        
        if json_file:
            self.load_from_json(json_file)
        elif csv_file:
            self.load_from_csv(csv_file)
    
    def load_from_json(self, filepath):
        """Load job data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.jobs = json.load(f)
            self.df = pd.DataFrame(self.jobs)
            logger.info(f"Loaded {len(self.jobs)} jobs from {filepath}")
        except Exception as e:
            logger.error(f"Error loading JSON: {e}")
    
    def load_from_csv(self, filepath):
        """Load job data from CSV file"""
        try:
            self.df = pd.read_csv(filepath)
            self.jobs = self.df.to_dict('records')
            logger.info(f"Loaded {len(self.jobs)} jobs from {filepath}")
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
    
    def get_company_statistics(self) -> Dict:
        """Get statistics by company"""
        if not self.df is None:
            company_counts = self.df['company'].value_counts().to_dict()
            return company_counts
        return {}
    
    def get_location_statistics(self) -> Dict:
        """Get statistics by location"""
        if self.df is not None:
            location_counts = self.df['location'].value_counts().to_dict()
            return location_counts
        return {}
    
    def get_role_statistics(self) -> Dict:
        """Get statistics by role"""
        if self.df is not None:
            role_counts = self.df['role'].value_counts().to_dict()
            return role_counts
        return {}
    
    def get_salary_statistics(self) -> Dict:
        """Get salary-related statistics"""
        if self.df is not None:
            salary_data = self.df[self.df['salary'].notna()]
            stats = {
                'total_with_salary': len(salary_data),
                'percentage': f"{(len(salary_data) / len(self.df) * 100):.2f}%"
            }
            return stats
        return {}
    
    def get_summary_report(self) -> str:
        """Generate a summary report"""
        if not self.jobs:
            return "No data loaded"
        
        report = []
        report.append("\n" + "="*80)
        report.append("NAUKRI JOB SCRAPING SUMMARY REPORT")
        report.append("="*80 + "\n")
        
        report.append(f"Total Jobs Found: {len(self.jobs)}")
        report.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Company statistics
        report.append("Top Companies:")
        company_stats = self.get_company_statistics()
        for company, count in list(company_stats.items())[:10]:
            report.append(f"  - {company}: {count} jobs")
        report.append("")
        
        # Location statistics
        report.append("Jobs by Location:")
        location_stats = self.get_location_statistics()
        for location, count in location_stats.items():
            report.append(f"  - {location}: {count} jobs")
        report.append("")
        
        # Role statistics
        report.append("Jobs by Role:")
        role_stats = self.get_role_statistics()
        for role, count in role_stats.items():
            report.append(f"  - {role}: {count} jobs")
        report.append("")
        
        # Salary statistics
        report.append("Salary Information:")
        salary_stats = self.get_salary_statistics()
        for key, value in salary_stats.items():
            report.append(f"  - {key}: {value}")
        report.append("")
        
        report.append("="*80 + "\n")
        
        return "\n".join(report)
    
    def export_filtered_results(self, filters: Dict, output_file: str):
        """
        Export filtered results to a new file
        
        Example filters:
        {
            'company': 'Google',
            'location': 'Chennai',
            'role': 'Data Scientist'
        }
        """
        if self.df is None:
            logger.error("No data loaded")
            return
        
        filtered_df = self.df.copy()
        
        for column, value in filters.items():
            if column in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[column] == value]
        
        if len(filtered_df) > 0:
            if output_file.endswith('.csv'):
                filtered_df.to_csv(output_file, index=False, encoding='utf-8')
            elif output_file.endswith('.json'):
                filtered_df.to_json(output_file, orient='records', indent=2)
            logger.info(f"Exported {len(filtered_df)} filtered jobs to {output_file}")
        else:
            logger.warning("No jobs match the filter criteria")
    
    def get_jobs_by_company(self, company: str) -> List[Dict]:
        """Get all jobs from a specific company"""
        if self.df is not None:
            return self.df[self.df['company'] == company].to_dict('records')
        return []
    
    def display_top_jobs(self, limit=10):
        """Display top jobs"""
        if not self.jobs:
            print("No data loaded")
            return
        
        print("\n" + "="*100)
        print(f"TOP {min(limit, len(self.jobs))} JOBS")
        print("="*100 + "\n")
        
        for idx, job in enumerate(self.jobs[:limit], 1):
            print(f"#{idx}")
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Company: {job.get('company', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Salary: {job.get('salary', 'N/A')}")
            print(f"  URL: {job.get('job_url', 'N/A')}")
            print()
    
    def save_report(self, filepath: str):
        """Save summary report to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.get_summary_report())
            logger.info(f"Report saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")


def main():
    """Example usage"""
    # Load and analyze results
    analyzer = NaukriDataAnalyzer(json_file='naukri_jobs.json')
    
    # Print summary report
    print(analyzer.get_summary_report())
    
    # Display top jobs
    analyzer.display_top_jobs(limit=5)
    
    # Save report
    analyzer.save_report('job_analysis_report.txt')
    
    # Export jobs by specific company
    # analyzer.export_filtered_results({'company': 'Google'}, 'google_jobs.csv')


if __name__ == "__main__":
    main()
