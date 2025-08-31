"""
Data Analysis Example for USAJobs Cybersecurity Scraper

This script demonstrates how to analyze the scraped job data
and extract useful insights for students.
"""

import json
import pandas as pd
from datetime import datetime
from collections import Counter
import re
from config import ENTRY_LEVEL_KEYWORDS


def load_job_data():
    """Load the scraped job data."""
    try:
        with open(
            "job_data/active_cybersecurity_jobs.json", "r", encoding="utf-8"
        ) as f:
            return json.load(f)
    except FileNotFoundError:
        print("No job data found. Run the scraper first!")
        return []


def analyze_salaries(jobs):
    """Analyze salary information."""
    salaries = []

    for job in jobs:
        salary_range = job.get("salary_range", "")
        if salary_range and salary_range != "Not specified":
            # Extract salary numbers
            numbers = re.findall(r"\$([0-9,]+)", salary_range)
            if len(numbers) >= 2:
                try:
                    min_sal = int(numbers[0].replace(",", ""))
                    max_sal = int(numbers[1].replace(",", ""))
                    avg_sal = (min_sal + max_sal) / 2
                    salaries.append(
                        {
                            "job": job.get("position_title", ""),
                            "agency": job.get("organization", ""),
                            "min": min_sal,
                            "max": max_sal,
                            "avg": avg_sal,
                            "location": ", ".join(job.get("locations", [])),
                        }
                    )
                except ValueError:
                    continue

    return salaries


def analyze_agencies(jobs):
    """Analyze job distribution by agency."""
    agencies = Counter()
    agency_details = {}

    for job in jobs:
        org = job.get("organization", "Unknown")
        agencies[org] += 1

        if org not in agency_details:
            agency_details[org] = {"jobs": [], "departments": set(), "locations": set()}

        agency_details[org]["jobs"].append(job.get("position_title", ""))
        agency_details[org]["departments"].add(job.get("department", ""))
        agency_details[org]["locations"].update(job.get("locations", []))

    return agencies, agency_details


def analyze_locations(jobs):
    """Analyze job distribution by location."""
    locations = Counter()

    for job in jobs:
        job_locations = job.get("locations", [])
        for location in job_locations:
            # Extract state from location string
            if "," in location:
                state = location.split(",")[-1].strip()
                locations[state] += 1

    return locations


def find_entry_level_opportunities(jobs):
    """Find the best entry-level opportunities."""
    entry_level_jobs = []

    for job in jobs:
        job_text = f"{job.get('position_title', '')} {job.get('qualifications_summary', '')}".lower()

        # Check for entry-level indicators from config
        if any(indicator in job_text for indicator in ENTRY_LEVEL_KEYWORDS):
            # Check that it doesn't require extensive experience
            exclusions = [
                "10+ years",
                "15+ years",
                "senior",
                "lead",
                "principal",
                "manager",
            ]
            if not any(exclusion in job_text for exclusion in exclusions):
                entry_level_jobs.append(job)

    return entry_level_jobs


def analyze_keywords(jobs):
    """Analyze most common keywords in job postings."""
    all_keywords = []

    for job in jobs:
        keywords = job.get("relevant_keywords", [])
        all_keywords.extend(keywords)

    return Counter(all_keywords)


def generate_report(jobs):
    """Generate a comprehensive analysis report."""
    if not jobs:
        print("No job data to analyze!")
        return

    print("=" * 60)
    print("🔐 CYBERSECURITY JOBS ANALYSIS REPORT")
    print("=" * 60)
    print(f"📊 Total active positions: {len(jobs)}")
    print(f"📅 Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Salary Analysis
    print("\\n💰 SALARY ANALYSIS")
    print("-" * 30)
    salaries = analyze_salaries(jobs)

    if salaries:
        salary_df = pd.DataFrame(salaries)
        print(f"Average salary range: ${salary_df['avg'].mean():,.0f}")
        print(f"Median salary range: ${salary_df['avg'].median():,.0f}")
        print(
            f"Salary range: ${salary_df['min'].min():,.0f} - ${salary_df['max'].max():,.0f}"
        )

        print("\\nTop 5 Highest Paying Positions:")
        top_salaries = salary_df.nlargest(5, "avg")
        for i, row in top_salaries.iterrows():
            print(f"  {row['job'][:50]}... | ${row['avg']:,.0f} avg | {row['agency']}")

    # Agency Analysis
    print("\\n🏢 AGENCY ANALYSIS")
    print("-" * 30)
    agencies, _ = analyze_agencies(jobs)

    print("Top 10 Agencies by Job Count:")
    for agency, count in agencies.most_common(10):
        print(
            f"  {agency[:40]}{'.' if len(agency) > 40 else '':<40} {count:>3} positions"
        )

    # Location Analysis
    print("\\n📍 LOCATION ANALYSIS")
    print("-" * 30)
    locations = analyze_locations(jobs)

    print("Top 10 States by Job Count:")
    for state, count in locations.most_common(10):
        print(f"  {state:<20} {count:>3} positions")

    # Entry Level Analysis
    print("\\n🎓 ENTRY-LEVEL OPPORTUNITIES")
    print("-" * 30)
    entry_level = find_entry_level_opportunities(jobs)
    print(f"Entry-level suitable positions: {len(entry_level)}")

    if entry_level:
        print("\\nSample Entry-Level Positions:")
        for i, job in enumerate(entry_level[:5], 1):
            print(f"  {i}. {job.get('position_title', '')}")
            print(
                f"     {job.get('organization', '')} | {job.get('salary_range', 'N/A')}"
            )
            print(f"     Closes: {job.get('application_close_date', '')[:10]}")

    # Keyword Analysis
    print("\\n🔍 KEYWORD ANALYSIS")
    print("-" * 30)
    keywords = analyze_keywords(jobs)

    print("Most Common Keywords:")
    for keyword, count in keywords.most_common(10):
        print(f"  {keyword:<20} {count:>3} jobs")

    # Security Clearance Requirements
    print("\\n🔒 SECURITY CLEARANCE")
    print("-" * 30)
    clearance_required = sum(
        1 for job in jobs if job.get("security_clearance_required", False)
    )
    print(
        f"Positions requiring security clearance: {clearance_required} ({clearance_required/len(jobs)*100:.1f}%)"
    )
    print(
        f"Positions without clearance requirement: {len(jobs) - clearance_required} ({(len(jobs) - clearance_required)/len(jobs)*100:.1f}%)"
    )

    print("\\n" + "=" * 60)
    print("💡 TIP: Focus on positions without clearance requirements")
    print("   if you're just starting your cybersecurity career!")
    print("=" * 60)


def export_filtered_jobs(jobs, filter_type="entry_level"):
    """Export filtered job lists for targeted applications."""
    if filter_type == "entry_level":
        filtered_jobs = find_entry_level_opportunities(jobs)
        filename = "entry_level_cybersecurity_jobs"
    elif filter_type == "no_clearance":
        filtered_jobs = [
            job for job in jobs if not job.get("security_clearance_required", False)
        ]
        filename = "no_clearance_cybersecurity_jobs"
    else:
        filtered_jobs = jobs
        filename = "all_cybersecurity_jobs"

    # Export to CSV
    if filtered_jobs:
        df = pd.DataFrame(filtered_jobs)
        csv_filename = f"job_data/{filename}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\\n📁 Exported {len(filtered_jobs)} jobs to {csv_filename}")

    return filtered_jobs


def main():
    """Main analysis function."""
    print("Loading job data...")
    jobs = load_job_data()

    if jobs:
        generate_report(jobs)

        # Export specialized lists
        print("\\n📊 CREATING SPECIALIZED JOB LISTS")
        print("-" * 40)
        export_filtered_jobs(jobs, "entry_level")
        export_filtered_jobs(jobs, "no_clearance")

        print(
            "\\n✅ Analysis complete! Check the job_data directory for exported lists."
        )
    else:
        print("No data to analyze. Run the scraper first with:")
        print("  python scheduled_scraper.py once")


if __name__ == "__main__":
    main()
