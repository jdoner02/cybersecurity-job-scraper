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
cybersecurity-job-scraper/
├── .env                        # API credentials (create this)
├── .gitignore                  # Git ignore patterns
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── config.py                   # Configuration settings
├── usajobs_client.py          # Core API client
├── cybersecurity_scraper.py   # Main scraping logic
├── scheduled_scraper.py       # Scheduled job management
├── analyze_jobs.py            # Data analysis tools
├── demo.py                    # Quick demo script
└── job_data/                  # Data storage directory (auto-created)
    ├── master_jobs_database.json
    ├── active_cybersecurity_jobs.json
    ├── active_cybersecurity_jobs.csv
    ├── entry_level_cybersecurity_jobs.csv
    ├── no_clearance_cybersecurity_jobs.csv
    └── scraping_stats.json
```

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jdoner02/cybersecurity-job-scraper.git
   cd cybersecurity-job-scraper
   ```

2. **Set up Python virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\\Scripts\\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**:
   - Get your USAJobs API key from [developer.usajobs.gov](https://developer.usajobs.gov/)
   - Create a `.env` file with your credentials:
   ```
   USAJOBS_API_KEY=your_api_key_here
   USAJOBS_EMAIL=your_email@example.com
   ```

## 🚀 Quick Start

Run the demo script to see the system in action:

```bash
python demo.py
```

This will:
1. Test your API connection
2. Fetch recent cybersecurity job postings
3. Filter for relevant positions
4. Generate a summary report
5. Save data to the `job_data/` directory

## 📊 Usage Examples

### Run a One-Time Job Search
```bash
python scheduled_scraper.py once
```

### Start Scheduled Job Collection (runs every 6 hours)
```bash
python scheduled_scraper.py start
```

### Analyze Collected Data
```bash
python analyze_jobs.py
```

### View Sample Output
The system will create several files in the `job_data/` directory:
- `active_cybersecurity_jobs.json` - All current job postings
- `entry_level_cybersecurity_jobs.csv` - Filtered entry-level positions
- `no_clearance_cybersecurity_jobs.csv` - Jobs not requiring security clearance

## 📈 Analysis Features

The analysis script provides:
- Salary range analysis
- Geographic distribution of opportunities
- Agency-by-agency breakdown
- Entry-level opportunity identification
- Security clearance requirements
- Most common keywords and skills

## 🎓 For Students

This tool is specifically designed for NCAE cybersecurity students to:
1. **Discover Opportunities**: Find federal positions you might not know existed
2. **Track Requirements**: Understand what skills are most in-demand
3. **Plan Applications**: Focus on positions matching your background
4. **Monitor Trends**: See how the job market evolves over time

### Key Benefits for New Graduates:
- Identifies positions that don't require security clearance
- Filters for entry-level and trainee positions
- Highlights internships and fellowship programs
- Shows salary ranges to help with career planning

## 🔧 Configuration

Customize the search by editing `config.py`:
- Add new search keywords
- Modify occupational series codes
- Adjust entry-level indicators
- Change scheduling intervals

## 📋 Data Output

Each job posting includes:
- Position title and department
- Salary range and grade level
- Location(s)
- Application deadline
- Qualifications summary
- Security clearance requirements
- Relevant keywords matched
- Agency and organization details

## 🤝 Contributing

This project is designed for educational use. Students are encouraged to:
- Fork the repository
- Add new filtering capabilities
- Improve the analysis features
- Submit pull requests with enhancements

## ⚡ Performance Notes

- Initial run may take 2-3 minutes to fetch all data
- Subsequent runs are faster due to duplicate detection
- API rate limiting is automatically handled
- Data is cached locally to minimize API calls

## 📋 Requirements

- Python 3.7+
- USAJobs.gov API key (free)
- Internet connection
- ~50MB disk space for data storage

## 🔒 Privacy & Security

- No personal data is collected
- API credentials are stored locally only
- All data comes from public USAJobs.gov listings
- No tracking or analytics

## 📚 Educational Context

Developed as part of cybersecurity workforce development initiatives to help NCAE students:
- Understand the federal hiring process
- Identify career pathways in cybersecurity
- Build skills in data analysis and automation
- Connect academic learning with career opportunities

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section below
2. Review the API documentation at developer.usajobs.gov
3. Ensure your API credentials are correctly configured

## 🐛 Troubleshooting

**No jobs found?**
- Verify your API key is valid
- Check your internet connection
- Ensure the email in .env matches your API registration

**Analysis script errors?**
- Run the scraper first to generate data
- Check that job_data directory exists
- Verify Python dependencies are installed

**Permission errors?**
- Ensure you have write permissions in the project directory
- Check that .env file is readable

---

*This project is intended for educational use by cybersecurity students. Always follow your institution's guidelines for academic projects and respect API usage terms.*