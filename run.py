#!/usr/bin/env python3
"""
Run the Naukri JSON-LD scraper with interactive prompt support.
"""

import argparse
import subprocess
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Run the Naukri JSON-LD scraper with profile, location, and experience input.'
    )
    parser.add_argument(
        '--profile', '-p', type=str,
        help='Job profile or role(s). Comma-separated for multiple values.'
    )
    parser.add_argument(
        '--location', '-l', type=str,
        help='Location(s). Comma-separated for multiple values.'
    )
    parser.add_argument(
        '--experience', '-e', type=int,
        help='Years of experience.'
    )
    return parser.parse_args()


def prompt_for_missing(args):
    if not args.profile:
        args.profile = input(
            'Enter job profile(s) (comma-separated, e.g. Data Scientist, Python Developer): '
        ).strip()
    if not args.location:
        args.location = input(
            'Enter location(s) (comma-separated, e.g. Chennai, Bangalore): '
        ).strip()
    if not args.experience:
        experience_value = input('Enter years of experience (e.g. 11): ').strip()
        while experience_value and not experience_value.isdigit():
            experience_value = input('Please enter a valid number for years of experience: ').strip()
        args.experience = int(experience_value) if experience_value else None
    return args


def main():
    args = parse_arguments()
    args = prompt_for_missing(args)

    if not args.profile or not args.location or args.experience is None:
        print('Error: profile, location, and experience are required.')
        return

    command = [
        sys.executable,
        'naukri_jsonld_scraper.py',
        '--profile', args.profile,
        '--location', args.location,
        '--experience', str(args.experience),
    ]

    print('\nRunning Naukri scraper...')
    result = subprocess.run(command)
    if result.returncode == 0:
        print('\n✓ Scraper finished successfully.')
    else:
        print(f'\n✗ Scraper exited with code {result.returncode}.')


if __name__ == '__main__':
    main()
