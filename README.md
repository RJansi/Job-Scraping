# Job Hunt Agent

A Python-based project for scraping Naukri.com job listings, with support for both HTML and structured data scraping.

## Project Overview

This repository includes multiple scraper implementations for Naukri.com:

- `naukri_jsonld_scraper.py` - Preferred scraper that extracts complete job URLs from embedded JSON-LD structured data.
- `naukri_scraper.py` - Basic HTML scraper using BeautifulSoup.
- `naukri_selenium_scraper.py` - Selenium-based scraper for JavaScript-rendered job listings.
- `naukri_optimized_scraper.py` - Optimized Selenium implementation with faster page handling.
- `run.py` - Runnable command-line launcher to run the JSON-LD scraper with user prompts.
- `debug_scraper.py` - Debug helper for inspecting the current Naukri.com page structure.
- `job_data_helper.py` - Helper utilities for creating templates and importing job data.

## Features

- Prompt-based command line input for job profile, location, and experience.
- Complete URL extraction through JSON-LD data.
- Supports multiple roles and locations with comma-separated input.
- Saves job data to JSON and CSV output files.
- Includes a runnable launcher script for easy execution.

## Requirements

- Python 3.8+
- `requests`
- `beautifulsoup4`
- `lxml`
- `selenium` (optional for Selenium-based scrapers)
- `webdriver-manager` (optional for Selenium scraper automation)

Install requirements using:

```bash
pip install -r requirements.txt
```

## Usage

### Run the project interactively

```bash
cd "e:\Job hunt Agent"
python run.py
```

The script will prompt for:
- Job profile(s) (e.g. `Data Scientist, Python Developer`)
- Location(s) (e.g. `Chennai, Bangalore`)
- Years of experience (e.g. `11`)

### Run with command-line arguments

```bash
python run.py --profile "Data Scientist" --location "Chennai" --experience 11
```

### Directly run the JSON-LD scraper

```bash
python naukri_jsonld_scraper.py --profile "Data Scientist" --location "Chennai" --experience 11
```

### Run the basic scraper

```bash
python naukri_scraper.py
```

### Run the Selenium scraper

```bash
python naukri_selenium_scraper.py
```

## Output

The scraper saves results to:

- `naukri_jobs_jsonld_<timestamp>.json`
- `naukri_jobs_jsonld_<timestamp>.csv`

## Notes

- JSON-LD scraping is the most reliable method for extracting complete Naukri job URLs.
- Selenium-based scrapers require a compatible browser driver (ChromeDriver) and may need additional setup.
- The project uses a `.gitignore` to avoid committing environment and output files.

## Repository Structure

- `README.md` - Project documentation.
- `run.py` - Main launcher script.
- `naukri_jsonld_scraper.py` - JSON-LD based scraper.
- `naukri_scraper.py` - Basic BeautifulSoup scraper.
- `naukri_selenium_scraper.py` - Selenium scraper.
- `naukri_optimized_scraper.py` - Optimized Selenium scraper.
- `debug_scraper.py` - Debug helper for page inspection.
- `job_data_helper.py` - Data helper utilities.
- `requirements.txt` - Dependency list.

## Legal and Ethical Use

Please use this scraper responsibly and comply with Naukri.com's Terms of Service and any applicable website policies. Avoid excessive scraping and respect rate limits.
