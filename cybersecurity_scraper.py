"""
Cybersecurity Job Scraper for NCAE Students

This module contains the main job scraping logic specifically designed
for students in computer science, cybersecurity, and secure AI programs
at NCAE (National Centers of Academic Excellence) designated schools.

Author: USAJobs Cybersecurity Scraper Project
License: MIT
"""

import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Set

import pandas as pd

from config import (
    CYBERSECURITY_KEYWORDS,
    CS_AI_KEYWORDS,
    ENTRY_LEVEL_KEYWORDS,
    IT_SERIES_CODES,
    API_CONFIG,
)
from usajobs_client import USAJobsAPI


class CybersecurityJobScraper:
    """Main job scraper for cybersecurity-related positions."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the job scraper.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.api = USAJobsAPI(log_level)
        
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

        # Load reference data
        self.cyber_roles = {}
        self.cyber_groupings = {}
        self.it_occupational_series = set()
        self.agencies = {}

        self._load_reference_data()

        # Import keywords from config
        self.cybersecurity_keywords = CYBERSECURITY_KEYWORDS
        self.cs_ai_keywords = CS_AI_KEYWORDS
        self.entry_level_indicators = ENTRY_LEVEL_KEYWORDS
        self.it_series_codes = IT_SERIES_CODES

    def _load_reference_data(self):
        """Load reference data from the API."""
        try:
            # Load cybersecurity work roles
            roles = self.api.get_cybersecurity_work_roles()
            if roles:
                self.cyber_roles = {role["Code"]: role["Value"] for role in roles}
                self.logger.info(
                    f"Loaded {len(self.cyber_roles)} cybersecurity work roles"
                )

            # Load cybersecurity work groupings
            groupings = self.api.get_cybersecurity_work_groupings()
            if groupings:
                # Handle different key names in groupings (GroupingName vs Value)
                for g in groupings:
                    code = g.get("Code", "")
                    name = g.get("GroupingName") or g.get("Value", "")
                    if code and name:
                        self.cyber_groupings[code] = name
                self.logger.info(
                    f"Loaded {len(self.cyber_groupings)} cybersecurity work groupings"
                )

            # Load occupational series and identify IT-related ones
            occ_series = self.api.get_occupational_series()
            if occ_series:
                for series in occ_series:
                    code = series.get("Code", "")
                    value = series.get("Value", "").lower()
                    if any(
                        keyword in value
                        for keyword in [
                            "information technology",
                            "computer",
                            "cyber",
                            "data",
                            "software",
                            "network",
                        ]
                    ):
                        self.it_occupational_series.add(code)

                self.logger.info(
                    f"Identified {len(self.it_occupational_series)} IT-related occupational series"
                )

            # Load agencies
            agencies = self.api.get_agency_subelements()
            if agencies:
                self.agencies = {agency["Code"]: agency["Value"] for agency in agencies}
                self.logger.info(f"Loaded {len(self.agencies)} agencies")

        except Exception as e:
            self.logger.error(f"Error loading reference data: {e}")

    def _is_relevant_job(self, job: Dict) -> bool:
        """
        Check if a job is relevant for cybersecurity/CS/AI students.

        Args:
            job: Job data from API

        Returns:
            True if job is relevant, False otherwise
        """
        # Get job text fields
        position_title = (
            job.get("MatchedObjectDescriptor", {}).get("PositionTitle", "").lower()
        )
        job_summary = (
            job.get("MatchedObjectDescriptor", {}).get("JobSummary", "").lower()
        )
        qualifications = (
            job.get("MatchedObjectDescriptor", {})
            .get("QualificationSummary", "")
            .lower()
        )

        # Combine all text for searching
        job_text = f"{position_title} {job_summary} {qualifications}"

        # Check for cybersecurity keywords
        cyber_match = any(
            keyword in job_text for keyword in self.cybersecurity_keywords
        )

        # Check for CS/AI keywords
        cs_ai_match = any(keyword in job_text for keyword in self.cs_ai_keywords)

        # Check occupational series
        job_category = job.get("MatchedObjectDescriptor", {}).get("JobCategory", [])
        series_match = False
        if job_category:
            for category in job_category:
                code = category.get("Code", "")
                if code in self.it_series_codes or code in self.it_occupational_series:
                    series_match = True
                    break

        return cyber_match or cs_ai_match or series_match

    def _is_entry_level_suitable(self, job: Dict) -> bool:
        """
        Check if a job is suitable for entry-level candidates.

        Args:
            job: Job data from API

        Returns:
            True if suitable for entry-level, False otherwise
        """
        # Get relevant fields
        position_title = (
            job.get("MatchedObjectDescriptor", {}).get("PositionTitle", "").lower()
        )
        job_summary = (
            job.get("MatchedObjectDescriptor", {}).get("JobSummary", "").lower()
        )
        qualifications = (
            job.get("MatchedObjectDescriptor", {})
            .get("QualificationSummary", "")
            .lower()
        )

        # Check pay grade (GS-07 to GS-13 are typically entry to mid-level)
        pay_plan = job.get("MatchedObjectDescriptor", {}).get(
            "PositionRemuneration", []
        )
        grade_match = False
        if pay_plan:
            for plan in pay_plan:
                min_grade = plan.get("MinimumRange", "")
                max_grade = plan.get("MaximumRange", "")
                if any(
                    grade in f"{min_grade} {max_grade}"
                    for grade in ["07", "08", "09", "11", "12", "13"]
                ):
                    grade_match = True
                    break

        # Combine text for keyword search
        job_text = f"{position_title} {job_summary} {qualifications}"

        # Check for entry-level indicators
        entry_level_match = any(
            indicator in job_text for indicator in self.entry_level_indicators
        )

        # Exclude jobs requiring extensive experience (simple heuristic)
        experience_exclusions = [
            "senior",
            "10+ years",
            "15+ years",
            "20+ years",
            "senior level",
            "principal",
            "lead",
            "manager",
            "director",
            "chief",
            "executive",
            "expert level",
        ]

        has_exclusions = any(
            exclusion in job_text for exclusion in experience_exclusions
        )

        return (entry_level_match or grade_match) and not has_exclusions

    def search_cybersecurity_jobs(self, days_back: int = 30) -> List[Dict]:
        """
        Search for cybersecurity-related jobs suitable for NCAE students.

        Args:
            days_back: Number of days back to search for jobs (for future use)

        Returns:
            List of relevant job postings
        """
        all_jobs = []

        # Note: days_back parameter reserved for future date filtering functionality

        # Search parameters for different types of positions
        search_params_list = [
            # Cybersecurity-focused searches
            {"Keyword": "cybersecurity"},
            {"Keyword": "information security"},
            {"Keyword": "cyber security"},
            {"Keyword": "security analyst"},
            {"Keyword": "information assurance"},
            # IT and Computer Science searches
            {"Keyword": "computer science"},
            {"Keyword": "software engineer"},
            {"Keyword": "data scientist"},
            {"Keyword": "information technology"},
            {"Keyword": "IT specialist"},
            # AI and Machine Learning
            {"Keyword": "artificial intelligence"},
            {"Keyword": "machine learning"},
            {"Keyword": "data analysis"},
            # Entry-level specific searches
            {"Keyword": "intern cybersecurity"},
            {"Keyword": "entry level IT"},
            {"Keyword": "recent graduate technology"},
            {"Keyword": "pathways cybersecurity"},
            # Occupational series searches
            {"JobCategoryCode": "2210"},  # IT Management
            {"JobCategoryCode": "1550"},  # Computer Science
            {"JobCategoryCode": "0854"},  # Computer Engineering
        ]

        for params in search_params_list:
            try:
                self.logger.info(f"Searching with parameters: {params}")

                # Add common filters
                params.update(
                    {
                        "WhoMayApply": "public",
                        "HiringPath": "public",
                        "Fields": "full",
                        "ResultsPerPage": 500,
                    }
                )

                # Perform search
                results = self.api.search_jobs(**params)

                if results and "SearchResultItems" in results:
                    jobs = results["SearchResultItems"]
                    self.logger.info(f"Found {len(jobs)} jobs for search: {params}")

                    # Filter and process jobs
                    for job in jobs:
                        if self._is_relevant_job(job) and self._is_entry_level_suitable(
                            job
                        ):
                            # Extract and clean job data
                            processed_job = self._process_job_data(job)
                            if processed_job:
                                all_jobs.append(processed_job)

                # Rate limiting - be respectful to the API
                time.sleep(API_CONFIG['rate_limit_delay'])

            except Exception as e:
                self.logger.error(f"Error in search with params {params}: {e}")
                continue

        # Remove duplicates based on announcement number
        unique_jobs = []
        seen_announcements = set()

        for job in all_jobs:
            announcement_num = job.get("announcement_number")
            if announcement_num and announcement_num not in seen_announcements:
                seen_announcements.add(announcement_num)
                unique_jobs.append(job)

        self.logger.info(f"Found {len(unique_jobs)} unique relevant jobs")
        return unique_jobs

    def _process_job_data(self, job: Dict) -> Optional[Dict]:
        """
        Process and clean job data for storage.

        Args:
            job: Raw job data from API

        Returns:
            Cleaned job data dictionary
        """
        try:
            # Check if job is actually a dictionary
            if not isinstance(job, dict):
                self.logger.warning(f"Job data is not a dictionary: {type(job)}")
                return None

            descriptor = job.get("MatchedObjectDescriptor", {})

            # Check if descriptor is valid
            if not isinstance(descriptor, dict):
                self.logger.warning(
                    f"MatchedObjectDescriptor is not a dictionary: {type(descriptor)}"
                )
                return None

            # Extract agency information
            organization = descriptor.get("OrganizationName", "Unknown")
            dept_code = descriptor.get("DepartmentName", "Unknown")

            # Extract location information
            locations = descriptor.get("PositionLocation", [])
            location_strings = []
            for loc in locations:
                city = loc.get("CityName", "")
                state = loc.get("CountrySubDivisionCode", "")
                if city and state:
                    location_strings.append(f"{city}, {state}")

            # Extract pay information
            pay_info = descriptor.get("PositionRemuneration", [])
            salary_range = "Not specified"
            if pay_info:
                min_pay = pay_info[0].get("MinimumRange", "")
                max_pay = pay_info[0].get("MaximumRange", "")
                if min_pay and max_pay:
                    salary_range = f"${min_pay} - ${max_pay}"

            # Extract job category/series
            job_categories = descriptor.get("JobCategory", [])
            series_info = []
            for cat in job_categories:
                code = cat.get("Code", "")
                name = cat.get("Name", "")
                if code and name:
                    series_info.append(f"{code}: {name}")

            return {
                "announcement_number": descriptor.get("PositionID", ""),
                "position_title": descriptor.get("PositionTitle", ""),
                "organization": organization,
                "department": dept_code,
                "locations": location_strings,
                "salary_range": salary_range,
                "job_series": series_info,
                "application_close_date": descriptor.get("ApplicationCloseDate", ""),
                "publication_start_date": descriptor.get("PublicationStartDate", ""),
                "job_summary": (
                    descriptor.get("JobSummary", "")[:500] + "..."
                    if len(descriptor.get("JobSummary", "")) > 500
                    else descriptor.get("JobSummary", "")
                ),
                "qualifications_summary": (
                    descriptor.get("QualificationSummary", "")[:300] + "..."
                    if len(descriptor.get("QualificationSummary", "")) > 300
                    else descriptor.get("QualificationSummary", "")
                ),
                "position_uri": descriptor.get("PositionURI", ""),
                "apply_uri": (
                    descriptor.get("ApplyURI", [])[0]
                    if descriptor.get("ApplyURI")
                    and len(descriptor.get("ApplyURI", [])) > 0
                    else ""
                ),
                "scraped_date": datetime.now().isoformat(),
                "relevant_keywords": self._find_relevant_keywords(descriptor),
                "security_clearance_required": "security clearance"
                in descriptor.get("JobSummary", "").lower()
                or "clearance" in descriptor.get("QualificationSummary", "").lower(),
            }

        except Exception as e:
            self.logger.error(f"Error processing job data: {e}")
            return None

    def _find_relevant_keywords(self, descriptor: Dict) -> List[str]:
        """Find relevant keywords in job description."""
        job_text = f"{descriptor.get('PositionTitle', '')} {descriptor.get('JobSummary', '')} {descriptor.get('QualificationSummary', '')}".lower()

        found_keywords = []
        all_keywords = self.cybersecurity_keywords.union(self.cs_ai_keywords).union(
            self.entry_level_indicators
        )

        for keyword in all_keywords:
            if keyword in job_text:
                found_keywords.append(keyword)

        return found_keywords[:10]  # Limit to top 10 matches

    def save_jobs_to_file(self, jobs: List[Dict], filename: str = None):
        """
        Save jobs to JSON and CSV files.

        Args:
            jobs: List of job dictionaries
            filename: Base filename (without extension)
        """
        if not filename:
            filename = f"cybersecurity_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save to JSON
        json_filename = f"{filename}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved {len(jobs)} jobs to {json_filename}")

        # Save to CSV
        if jobs:
            df = pd.DataFrame(jobs)
            csv_filename = f"{filename}.csv"
            df.to_csv(csv_filename, index=False, encoding="utf-8")
            self.logger.info(f"Saved {len(jobs)} jobs to {csv_filename}")

    def run_search_and_save(self, days_back: int = 30):
        """
        Run the complete job search and save results.

        Args:
            days_back: Number of days back to search
        """
        self.logger.info("Starting cybersecurity job search for NCAE students...")

        jobs = self.search_cybersecurity_jobs(days_back)

        if jobs:
            self.save_jobs_to_file(jobs)

            # Print summary
            print("\n📊 Job Search Summary:")
            print(f"   Found {len(jobs)} relevant positions")
            print(f"   Search period: {days_back} days")
            print("   Saved to files with timestamp")

            # Show top agencies
            agencies = {}
            for job in jobs:
                org = job.get("organization", "Unknown")
                agencies[org] = agencies.get(org, 0) + 1

            print("\n🏢 Top Agencies:")
            for agency, count in sorted(
                agencies.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   {agency}: {count} positions")

            # Show sample positions
            print("\n💼 Sample Positions:")
            for i, job in enumerate(jobs[:3]):
                print(
                    f"   {i+1}. {job.get('position_title', 'N/A')} at {job.get('organization', 'N/A')}"
                )
                print(
                    f"      Location: {', '.join(job.get('locations', ['Not specified']))}"
                )
                print(f"      Salary: {job.get('salary_range', 'Not specified')}")
                print()
        else:
            print("No relevant jobs found.")


if __name__ == "__main__":
    scraper = CybersecurityJobScraper()
    scraper.run_search_and_save(days_back=30)
