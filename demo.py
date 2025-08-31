#!/usr/bin/env python3
"""
Quick Demo Script for USAJobs Cybersecurity Scraper

This script demonstrates the basic usage of the job scraper
for students and educators.
"""

import os
from scheduled_scraper import main as run_scraper
from analyze_jobs import main as analyze_data


def main():
    """Run a quick demo of the job scraper system."""
    print("🔐 USAJobs Cybersecurity Scraper Demo")
    print("=" * 50)

    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\n❌ ERROR: .env file not found!")
        print("Please create a .env file with your USAJobs API credentials:")
        print("USAJOBS_API_KEY=your_api_key_here")
        print("USAJOBS_EMAIL=your_email_here")
        return

    print("\n1. Running job scraper (this may take a few minutes)...")
    print("   Fetching cybersecurity jobs from USAJobs.gov...")

    try:
        # Run the scraper once
        run_scraper()

        print("\n2. Analyzing collected job data...")
        # Analyze the data
        analyze_data()

        print("\n✅ Demo complete!")
        print("\nNext steps:")
        print("- Check the job_data/ directory for exported CSV files")
        print("- Review entry_level_cybersecurity_jobs.csv for student opportunities")
        print("- Use 'python scheduled_scraper.py' to run automated collection")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Make sure your .env file has valid API credentials.")


if __name__ == "__main__":
    main()