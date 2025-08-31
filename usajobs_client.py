"""
USAJobs API Client for Cybersecurity Job Scraping

This module provides functionality to interact with the USAJobs API
to fetch cybersecurity-related job postings suitable for students
from computer science, cybersecurity, and secure AI programs at NCAE schools.

Author: USAJobs Cybersecurity Scraper Project
License: MIT
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class USAJobsAPI:
    """Client for interacting with the USAJobs API."""

    def __init__(self, log_level: str = "INFO"):
        """Initialize the API client with credentials from environment variables.
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.base_url = "https://data.usajobs.gov/api"
        self.api_key = os.getenv("USAJOBS_API_KEY")
        self.email = os.getenv("USAJOBS_EMAIL")

        if not self.api_key or not self.email:
            raise ValueError(
                "USAJobs API credentials not found in environment variables. "
                "Please ensure USAJOBS_API_KEY and USAJOBS_EMAIL are set."
            )

        self.headers = {
            "Host": "data.usajobs.gov",
            "User-Agent": f"{self.email}",
            "Authorization-Key": self.api_key,
            "Content-Type": "application/json",
        }

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
        self.logger.info("USAJobs API client initialized")

    def make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make a request to the USAJobs API.

        Args:
            endpoint: API endpoint (e.g., 'search', 'codelist/cyberworkroles')
            params: Query parameters for the request

        Returns:
            JSON response data or None if request fails
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            self.logger.info(f"Making request to: {url}")
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test the API connection by making a simple request.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.make_request("search", {"ResultsPerPage": 1})
            if result and "SearchResult" in result:
                self.logger.info("API connection test successful")
                return True
            else:
                self.logger.error(
                    "API connection test failed - unexpected response format"
                )
                return False
        except Exception as e:
            self.logger.error(f"API connection test failed: {e}")
            return False

    def get_cybersecurity_work_roles(self) -> Optional[List[Dict]]:
        """
        Fetch the list of cybersecurity work roles from the API.

        Returns:
            List of cybersecurity work role codes and descriptions
        """
        result = self.make_request("codelist/cyberworkroles")
        if result and "CodeList" in result:
            return result["CodeList"][0]["ValidValue"]
        return None

    def get_cybersecurity_work_groupings(self) -> Optional[List[Dict]]:
        """
        Fetch the list of cybersecurity work groupings from the API.

        Returns:
            List of cybersecurity work grouping codes and descriptions
        """
        result = self.make_request("codelist/cyberworkgroupings")
        if result and "CodeList" in result:
            return result["CodeList"][0]["ValidValue"]
        return None

    def get_occupational_series(self) -> Optional[List[Dict]]:
        """
        Fetch the list of occupational series codes.

        Returns:
            List of occupational series codes and descriptions
        """
        result = self.make_request("codelist/occupationalseries")
        if result and "CodeList" in result:
            return result["CodeList"][0]["ValidValue"]
        return None

    def get_agency_subelements(self) -> Optional[List[Dict]]:
        """
        Fetch the list of agency subelements.

        Returns:
            List of agency codes and descriptions
        """
        result = self.make_request("codelist/agencysubelements")
        if result and "CodeList" in result:
            return result["CodeList"][0]["ValidValue"]
        return None

    def search_jobs(self, **kwargs) -> Optional[Dict]:
        """
        Search for jobs using the USAJobs API.

        Args:
            **kwargs: Search parameters (Keyword, JobCategoryCode, etc.)

        Returns:
            Search results or None if request fails
        """
        # Set default parameters for better results
        default_params = {
            "ResultsPerPage": 500,  # Maximum allowed
            "WhoMayApply": "public",  # Public positions
            "Fields": "full",  # Get full job details
        }

        # Merge provided parameters with defaults
        params = {**default_params, **kwargs}

        result = self.make_request("search", params)
        if result and "SearchResult" in result:
            return result["SearchResult"]
        return None


if __name__ == "__main__":
    # Test the API client
    api = USAJobsAPI()

    # Test connection
    if api.test_connection():
        print("✅ API connection successful!")

        # Test fetching cybersecurity data
        print("\n🔍 Fetching cybersecurity work roles...")
        cyber_roles = api.get_cybersecurity_work_roles()
        if cyber_roles:
            print(f"Found {len(cyber_roles)} cybersecurity work roles")
            for role in cyber_roles[:3]:  # Show first 3
                print(f"  - {role.get('Code', 'N/A')}: {role.get('Value', 'N/A')}")

        print("\n🔍 Fetching cybersecurity work groupings...")
        cyber_groupings = api.get_cybersecurity_work_groupings()
        if cyber_groupings:
            print(f"Found {len(cyber_groupings)} cybersecurity work groupings")
            for grouping in cyber_groupings[:3]:  # Show first 3
                print(
                    f"  - {grouping.get('Code', 'N/A')}: {grouping.get('Value', 'N/A')}"
                )
    else:
        print("❌ API connection failed!")