"""
Scheduled Job Scraper

This script runs the cybersecurity job scraper on a schedule and maintains
a persistent database of job postings for NCAE students.

Author: USAJobs Cybersecurity Scraper Project
License: MIT
"""

import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import pandas as pd
import schedule

from config import DATA_CONFIG, SCHEDULE_CONFIG
from cybersecurity_scraper import CybersecurityJobScraper


class ScheduledJobScraper:
    """Manages scheduled job scraping and data persistence."""

    def __init__(self, data_dir: str = None, log_level: str = "INFO"):
        """Initialize the scheduled scraper.
        
        Args:
            data_dir: Directory to store job data (defaults to config value)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.data_dir = Path(data_dir or DATA_CONFIG['data_directory'])
        self.data_dir.mkdir(exist_ok=True)

        self.scraper = CybersecurityJobScraper(log_level)
        
        # Configure logger
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, log_level.upper()))

        # File paths from config
        self.master_jobs_file = self.data_dir / DATA_CONFIG['master_database_file']
        self.active_jobs_file = self.data_dir / DATA_CONFIG['active_jobs_file']
        self.csv_file = self.data_dir / DATA_CONFIG['csv_file']
        self.stats_file = self.data_dir / DATA_CONFIG['stats_file']

        # Load existing data
        self.master_jobs = self._load_existing_jobs()
        self.stats = self._load_stats()

    def _load_existing_jobs(self):
        """Load existing jobs from the master database."""
        if self.master_jobs_file.exists():
            try:
                with open(self.master_jobs_file, "r", encoding="utf-8") as f:
                    jobs = json.load(f)
                self.logger.info(
                    f"Loaded {len(jobs)} existing jobs from master database"
                )
                return jobs
            except Exception as e:
                self.logger.error(f"Error loading existing jobs: {e}")
        return []

    def _load_stats(self):
        """Load scraping statistics."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading stats: {e}")

        return {
            "total_runs": 0,
            "total_jobs_found": 0,
            "last_run": None,
            "agencies_tracked": {},
            "daily_stats": {},
        }

    def _save_master_jobs(self):
        """Save the master jobs database."""
        try:
            with open(self.master_jobs_file, "w", encoding="utf-8") as f:
                json.dump(self.master_jobs, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.master_jobs)} jobs to master database")
        except Exception as e:
            self.logger.error(f"Error saving master jobs: {e}")

    def _save_stats(self):
        """Save scraping statistics."""
        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving stats: {e}")

    def _is_job_expired(self, job):
        """Check if a job posting has expired."""
        try:
            close_date_str = job.get("application_close_date", "")
            if close_date_str:
                # Handle the USAJobs date format
                close_date = datetime.fromisoformat(
                    close_date_str.replace("Z", "+00:00").split(".")[0]
                )
                return close_date < datetime.now()
        except Exception as e:
            self.logger.warning(
                f"Error parsing date for job {job.get('announcement_number', 'unknown')}: {e}"
            )
        return False

    def _merge_new_jobs(self, new_jobs):
        """Merge new jobs with existing jobs, avoiding duplicates."""
        existing_announcements = {
            job.get("announcement_number") for job in self.master_jobs
        }

        new_count = 0
        for job in new_jobs:
            announcement_num = job.get("announcement_number")
            if announcement_num and announcement_num not in existing_announcements:
                self.master_jobs.append(job)
                existing_announcements.add(announcement_num)
                new_count += 1

        self.logger.info(f"Added {new_count} new jobs to master database")
        return new_count

    def _get_active_jobs(self):
        """Get currently active (non-expired) jobs."""
        active_jobs = []
        for job in self.master_jobs:
            if not self._is_job_expired(job):
                active_jobs.append(job)

        return active_jobs

    def _update_stats(self, new_jobs_count):
        """Update scraping statistics."""
        today = datetime.now().strftime("%Y-%m-%d")

        self.stats["total_runs"] += 1
        self.stats["total_jobs_found"] += new_jobs_count
        self.stats["last_run"] = datetime.now().isoformat()

        # Update daily stats
        if today not in self.stats["daily_stats"]:
            self.stats["daily_stats"][today] = {
                "runs": 0,
                "new_jobs": 0,
                "active_jobs": 0,
            }

        self.stats["daily_stats"][today]["runs"] += 1
        self.stats["daily_stats"][today]["new_jobs"] += new_jobs_count
        self.stats["daily_stats"][today]["active_jobs"] = len(self._get_active_jobs())

        # Update agency tracking
        for job in self.master_jobs:
            org = job.get("organization", "Unknown")
            if org not in self.stats["agencies_tracked"]:
                self.stats["agencies_tracked"][org] = 0
            self.stats["agencies_tracked"][org] += 1

    def run_scraping_cycle(self):
        """Run a complete scraping cycle."""
        self.logger.info("Starting scheduled scraping cycle...")

        try:
            # Run the scraper
            new_jobs = self.scraper.search_cybersecurity_jobs()

            # Merge new jobs
            new_count = self._merge_new_jobs(new_jobs)

            # Get active jobs
            active_jobs = self._get_active_jobs()

            # Save active jobs to files
            self._save_active_jobs(active_jobs)

            # Update statistics
            self._update_stats(new_count)

            # Save everything
            self._save_master_jobs()
            self._save_stats()

            # Log summary
            self.logger.info("Scraping cycle completed:")
            self.logger.info(f"  - New jobs found: {new_count}")
            self.logger.info(f"  - Total active jobs: {len(active_jobs)}")
            self.logger.info(f"  - Total jobs in database: {len(self.master_jobs)}")

            return {
                "success": True,
                "new_jobs": new_count,
                "active_jobs": len(active_jobs),
                "total_jobs": len(self.master_jobs),
            }

        except Exception as e:
            self.logger.error(f"Error in scraping cycle: {e}")
            return {"success": False, "error": str(e)}

    def _save_active_jobs(self, active_jobs):
        """Save active jobs to JSON and CSV files."""
        # Save to JSON
        with open(self.active_jobs_file, "w", encoding="utf-8") as f:
            json.dump(active_jobs, f, indent=2, ensure_ascii=False)

        # Save to CSV
        if active_jobs:
            df = pd.DataFrame(active_jobs)
            df.to_csv(self.csv_file, index=False, encoding="utf-8")

        self.logger.info(f"Saved {len(active_jobs)} active jobs to files")

    def print_summary(self):
        """Print a summary of current job data."""
        active_jobs = self._get_active_jobs()

        print("\\n" + "=" * 60)
        print("🔐 CYBERSECURITY JOBS SUMMARY")
        print("=" * 60)
        print(f"📊 Total jobs in database: {len(self.master_jobs)}")
        print(f"✅ Currently active jobs: {len(active_jobs)}")
        print(f"🔄 Total scraping runs: {self.stats['total_runs']}")
        print(f"📅 Last run: {self.stats.get('last_run', 'Never')}")

        if active_jobs:
            # Top agencies
            agency_counts = {}
            for job in active_jobs:
                org = job.get("organization", "Unknown")
                agency_counts[org] = agency_counts.get(org, 0) + 1

            print("\\n🏢 Top Agencies (Active Jobs):")
            for agency, count in sorted(
                agency_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   {agency}: {count} positions")

            # Sample recent jobs
            print("\\n💼 Recent Job Postings:")
            recent_jobs = sorted(
                active_jobs, key=lambda x: x.get("scraped_date", ""), reverse=True
            )[:3]
            for i, job in enumerate(recent_jobs, 1):
                print(f"   {i}. {job.get('position_title', 'N/A')}")
                print(
                    f"      {job.get('organization', 'N/A')} | {job.get('salary_range', 'N/A')}"
                )
                print(f"      Closes: {job.get('application_close_date', 'N/A')[:10]}")
                print()

        print("=" * 60)

    def setup_schedule(self):
        """Set up the scraping schedule."""
        # Run every 6 hours
        schedule.every(6).hours.do(self.run_scraping_cycle)

        # Also run daily at 9 AM
        schedule.every().day.at("09:00").do(self.run_scraping_cycle)

        # Clean up expired jobs weekly on Sundays at 2 AM
        schedule.every().sunday.at("02:00").do(self._cleanup_expired_jobs)

        self.logger.info("Scheduled job scraping every 6 hours and daily at 9 AM")

    def _cleanup_expired_jobs(self):
        """Remove expired jobs from the database."""
        original_count = len(self.master_jobs)
        self.master_jobs = [
            job for job in self.master_jobs if not self._is_job_expired(job)
        ]
        removed_count = original_count - len(self.master_jobs)

        if removed_count > 0:
            self.logger.info(f"Cleaned up {removed_count} expired jobs")
            self._save_master_jobs()

    def run_continuous(self):
        """Run the scheduler continuously."""
        self.logger.info("Starting continuous job scraper...")
        self.setup_schedule()

        # Run initial scraping
        print("Running initial scraping cycle...")
        self.run_scraping_cycle()
        self.print_summary()

        print("\\nScheduler started. Press Ctrl+C to stop.")
        print("Scraping will run every 6 hours and daily at 9 AM.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\\nScheduler stopped.")
            self.logger.info("Scheduler stopped by user")


def main():
    """Main function to run the scheduled scraper."""
    scraper = ScheduledJobScraper()

    # Check command line arguments for different modes
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "once":
            print("Running single scraping cycle...")
            result = scraper.run_scraping_cycle()
            scraper.print_summary()
            if result["success"]:
                print(f"✅ Success: Found {result['new_jobs']} new jobs")
            else:
                print(f"❌ Error: {result['error']}")
        elif mode == "summary":
            scraper.print_summary()
        elif mode == "continuous":
            scraper.run_continuous()
        else:
            print("Usage: python scheduled_scraper.py [once|summary|continuous]")
    else:
        # Default to single run
        print("Running single scraping cycle...")
        scraper.run_scraping_cycle()
        scraper.print_summary()


if __name__ == "__main__":
    main()
