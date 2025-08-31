"""
Configuration settings for the USAJobs Cybersecurity Scraper
"""

# Search Keywords - Add or modify based on your interests
CYBERSECURITY_KEYWORDS = {
    "cybersecurity",
    "cyber security",
    "information security",
    "infosec",
    "computer security",
    "network security",
    "data security",
    "cyber",
    "information assurance",
    "cybersec",
    "security analyst",
    "security engineer",
    "penetration test",
    "vulnerability",
    "incident response",
    "forensics",
    "risk assessment",
    "compliance",
    "governance",
    "security architecture",
    "threat intelligence",
    "malware",
    "encryption",
    "cryptography",
    "secure coding",
    "application security",
    "cloud security",
    "endpoint security",
}

CS_AI_KEYWORDS = {
    "computer science",
    "software engineer",
    "software developer",
    "programmer",
    "data scientist",
    "machine learning",
    "artificial intelligence",
    "AI/ML",
    "deep learning",
    "neural network",
    "data analysis",
    "algorithm",
    "python",
    "java",
    "c++",
    "javascript",
    "database",
    "web development",
    "mobile development",
    "cloud computing",
    "devops",
    "system administrator",
    "network administrator",
    "IT specialist",
    "technology",
    "digital",
    "automation",
    "robotics",
    "data mining",
    "big data",
    "analytics",
}

ENTRY_LEVEL_KEYWORDS = {
    "intern",
    "internship",
    "trainee",
    "entry level",
    "entry-level",
    "junior",
    "associate",
    "recent graduate",
    "new graduate",
    "GS-07",
    "GS-08",
    "GS-09",
    "GS-11",
    "GS-12",
    "GS-13",
    "student",
    "fellowship",
    "pathways",
    "recent college",
}

# Occupational Series Codes for IT/Cybersecurity
IT_SERIES_CODES = {
    "2210",  # Information Technology Management
    "0854",  # Computer Engineering
    "1550",  # Computer Science
    "0855",  # Electronics Engineering
    "0391",  # Telecommunications
    "0332",  # Computer Operations
    "2150",  # Transportation Industry Analysis
    "0343",  # Management and Program Analysis
    "1515",  # Operations Research
    "1529",  # Mathematical Statistics
}

# Scheduling Configuration
SCHEDULE_CONFIG = {
    "run_every_hours": 6,  # Run every X hours
    "daily_run_time": "09:00",  # Daily run time (24-hour format)
    "weekly_cleanup_day": "sunday",  # Day for cleanup
    "weekly_cleanup_time": "02:00",  # Time for weekly cleanup
}

# API Configuration
API_CONFIG = {
    "results_per_page": 500,  # Maximum results per API call
    "rate_limit_delay": 1,  # Seconds between API calls
    "max_retries": 3,  # Number of retry attempts
    "timeout": 30,  # Request timeout in seconds
}

# Data Management
DATA_CONFIG = {
    "data_directory": "job_data",
    "master_database_file": "master_jobs_database.json",
    "active_jobs_file": "active_cybersecurity_jobs.json",
    "csv_file": "active_cybersecurity_jobs.csv",
    "stats_file": "scraping_stats.json",
    "max_summary_length": 500,  # Max characters for job summary
    "max_quals_length": 300,  # Max characters for qualifications
}

# Target Agencies (Optional: Can be used for prioritization)
PRIORITY_AGENCIES = {
    "Department of Defense",
    "Department of Homeland Security",
    "Department of Justice",
    "Central Intelligence Agency",
    "National Security Agency",
    "Federal Bureau of Investigation",
    "Department of Veterans Affairs",
    "Department of Treasury",
    "Department of Energy",
    "National Institute of Standards and Technology",
}

# Exclusion Terms (Jobs to avoid)
EXCLUSION_TERMS = {
    "secret clearance required",  # If you don't have clearance yet
    "10+ years experience",
    "15+ years experience",
    "20+ years experience",
    "senior executive",
    "chief information officer",
    "executive level",
}

# Student-Friendly Terms (Boost relevance)
STUDENT_FRIENDLY_TERMS = {
    "no experience required",
    "training provided",
    "mentorship",
    "professional development",
    "career development",
    "recent graduate",
    "entry level",
    "internship",
    "fellowship",
    "pathways program",
}