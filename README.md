# USAJobs Cybersecurity Job Scraper for NCAE Students

A comprehensive job scraping system designed specifically for students in computer science, cybersecurity, and secure AI programs at NCAE (National Centers of Academic Excellence) designated schools.

## 🎯 Purpose

This project automatically fetches and filters federal job postings from USAJobs.gov that are relevant for cybersecurity students, focusing on:
- Entry-level and internship positions
- Cybersecurity-related roles
- Information Technology positions
- Computer Science and AI/ML opportunities
- Positions suitable for recent graduates

## 🚀 Features

- **Comprehensive Search**: Searches multiple keywords and occupational series codes
- **Smart Filtering**: Identifies relevant positions for cybersecurity/CS students
- **Entry-Level Focus**: Filters for positions suitable for new graduates
- **Scheduled Execution**: Runs automatically to keep job listings current
- **Data Persistence**: Maintains a database of all discovered positions
- **Export Options**: Saves data in both JSON and CSV formats
- **Agency Tracking**: Provides insights into which agencies have the most opportunities

## 📁 Project Structure

```
job-scraper-demo/
├── .env                        # API credentials
├── .gitignore                  # Git ignore patterns
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── usajobs_client.py          # Core API client
├── cybersecurity_scraper.py   # Main scraping logic
├── scheduled_scraper.py       # Scheduled job management
├── analyze_jobs.py            # Data analysis tools
├── demo.py                    # Quick demo script
└── job_data/                  # Data storage directory
    ├── master_jobs_database.json
    ├── active_cybersecurity_jobs.json
    ├── active_cybersecurity_jobs.csv
    ├── entry_level_cybersecurity_jobs.csv
    ├── no_clearance_cybersecurity_jobs.csv
    └── scraping_stats.json
```

## 🛠️ Installation

1. **Clone or download the project files**

2. **Set up Python virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\\Scripts\\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install requests python-dotenv schedule pandas
   ```

4. **Configure API credentials**:
   - Get your USAJobs API key from [developer.usajobs.gov](https://developer.usajobs.gov/)
   - Create a `.env` file with your credentials:
   ```
   USAJOBS-API-KEY='your_api_key_here'
   USAJOBS-API-EMAIL='your_email_here'
   ```

## 🔧 Usage

### Quick Start (Recommended for first use)
```bash
python demo.py
```
This runs a complete demo that will:
1. Check your API credentials
2. Fetch current cybersecurity jobs
3. Analyze the data and generate reports
4. Create CSV files for easy review

### Manual Commands

#### Single Run
```bash
python scheduled_scraper.py once
```

#### View Current Summary
```bash
python scheduled_scraper.py summary
```

#### Analyze Existing Data
```bash
python analyze_jobs.py
```

#### Continuous Monitoring (Runs every 6 hours)
```bash
python scheduled_scraper.py continuous
```

#### Test API Connection
```bash
python usajobs_client.py
```

## 📊 Output Files

The scraper generates several output files in the `job_data/` directory:

- **`active_cybersecurity_jobs.json`**: Current active job postings in JSON format
- **`active_cybersecurity_jobs.csv`**: Current active job postings in CSV format
- **`entry_level_cybersecurity_jobs.csv`**: Filtered list of entry-level opportunities
- **`no_clearance_cybersecurity_jobs.csv`**: Jobs that don't require security clearance
- **`master_jobs_database.json`**: Complete database of all discovered jobs
- **`scraping_stats.json`**: Statistics and tracking information

## 🔍 Search Criteria

The scraper searches for positions using:

### Keywords
- Cybersecurity terms: "cybersecurity", "information security", "cyber security"
- Technical roles: "software engineer", "data scientist", "IT specialist"
- AI/ML positions: "artificial intelligence", "machine learning", "data analysis"
- Entry-level terms: "intern", "entry level", "recent graduate", "pathways"

### Occupational Series Codes
- 2210: Information Technology Management
- 1550: Computer Science
- 0854: Computer Engineering
- Plus 24 other IT-related series

### Filtering Criteria
- **Relevance**: Must contain cybersecurity, computer science, or AI-related keywords
- **Entry-Level Suitability**: Prioritizes positions for GS-07 through GS-13 levels
- **Public Eligibility**: Only includes positions open to the public
- **Active Status**: Filters out expired job postings

## 📈 Recent Results

The scraper typically finds:
- **375+ active positions** in initial runs
- **Top agencies**: Veterans Health Administration, Air National Guard, Naval Systems Command
- **Salary ranges**: $34K - $195K depending on level and location
- **Geographic distribution**: Nationwide federal positions

## 🔐 Security & Best Practices

- API credentials are stored securely in environment variables
- Rate limiting is implemented to respect USAJobs API limits
- Comprehensive error handling and logging
- Data validation and deduplication

## 🎓 For NCAE Students

This tool is specifically designed for students at schools designated as National Centers of Academic Excellence in:
- Cyber Defense (CAE-CD)
- Cyber Operations (CAE-CO)
- Research (CAE-R)

The filtering algorithms prioritize positions that match the skillsets and career paths typical for these programs.

## 🔄 Scheduling

The automated scheduler:
- Runs every 6 hours during active monitoring
- Performs daily searches at 9:00 AM
- Weekly cleanup of expired postings
- Maintains comprehensive statistics

## 📝 Logging

All activities are logged to:
- Console output for immediate feedback
- `usajobs_scraper.log` file for detailed records
- Statistics tracking for performance monitoring

## 🚨 Troubleshooting

### Common Issues

1. **API Connection Errors**: Verify your API key and email in `.env`
2. **No Results Found**: Check your internet connection and API quotas
3. **Permission Errors**: Ensure the script has write access to create data files

### Debug Mode
Run the demo script for comprehensive testing:
```bash
python demo.py
```

Or test individual components:
```bash
python usajobs_client.py  # Test API connection
python analyze_jobs.py    # Test data analysis
```

## 📧 Support

For questions about:
- **API Access**: Contact USAJobs developer support
- **NCAE Programs**: Consult your school's cybersecurity department
- **Federal Hiring**: Visit [help.usajobs.gov](https://help.usajobs.gov/)

## 📄 License

This project is provided as-is for educational and career development purposes for NCAE students and cybersecurity professionals.

## 🤝 Contributing

To improve the scraper:
1. Add new relevant keywords to the search criteria
2. Enhance filtering logic for better job relevance
3. Improve data export formats
4. Add new scheduling options

---

**Happy Job Hunting! 🔍💼**

*This tool helps you stay ahead of federal cybersecurity opportunities - perfect for launching your career in government cybersecurity roles.*
