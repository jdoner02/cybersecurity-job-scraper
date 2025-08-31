"""
Job Qualifications Extractor and Analyzer

This module provides object-oriented classes for extracting, analyzing,
and storing job qualifications from USAJobs postings. It creates structured
data that can be used for the frontend ranking system.
"""

import json
import re
import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
from datetime import datetime
import pandas as pd


@dataclass
class Qualification:
    """Represents a single qualification requirement."""
    
    text: str
    category: str  # 'education', 'experience', 'skill', 'certification', 'clearance'
    weight: float  # Importance weight (0.0-1.0)
    keywords: List[str]
    required: bool = True  # vs preferred/desired
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class JobPosting:
    """Enhanced job posting with extracted qualifications."""
    
    # Basic job info
    job_id: str
    title: str
    agency: str
    location: List[str]
    salary_range: str
    grade_level: str
    application_deadline: str
    url: str
    
    # Extracted qualifications
    qualifications: List[Qualification]
    education_requirements: List[str]
    experience_requirements: List[str]
    skill_requirements: List[str]
    certification_requirements: List[str]
    clearance_requirements: List[str]
    
    # Metadata
    extraction_date: str
    relevance_score: float = 0.0
    entry_level_score: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['qualifications'] = [q.to_dict() for q in self.qualifications]
        return data


class QualificationExtractor:
    """Extracts and categorizes job qualifications from text."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Pattern definitions for different qualification types
        self.education_patterns = [
            r"bachelor['']?s?\s+degree",
            r"master['']?s?\s+degree", 
            r"phd|doctorate",
            r"associate['']?s?\s+degree",
            r"high school|hs diploma",
            r"college degree",
            r"undergraduate",
            r"graduate degree",
            r"computer science|cs degree",
            r"cybersecurity degree",
            r"information technology|it degree",
            r"engineering degree",
        ]
        
        self.experience_patterns = [
            r"(\d+)[\s\-]+years?\s+(?:of\s+)?experience",
            r"(\d+)[\s\-]+year\s+minimum",
            r"minimum\s+of\s+(\d+)\s+years?",
            r"at least\s+(\d+)\s+years?",
            r"(\d+)\+\s+years?",
            r"entry[\s\-]level",
            r"no experience required",
            r"recent graduate",
            r"internship experience",
        ]
        
        self.skill_patterns = [
            r"programming languages?:?\s*([a-zA-Z\s,]+)",
            r"proficient in:?\s*([a-zA-Z\s,]+)",
            r"knowledge of:?\s*([a-zA-Z\s,]+)",
            r"experience with:?\s*([a-zA-Z\s,]+)",
            r"familiar with:?\s*([a-zA-Z\s,]+)",
            r"skills in:?\s*([a-zA-Z\s,]+)",
        ]
        
        self.certification_patterns = [
            r"cissp|certified information systems security professional",
            r"cism|certified information security manager",
            r"cisa|certified information systems auditor",
            r"security\+|comptia security\+",
            r"network\+|comptia network\+",
            r"ceh|certified ethical hacker",
            r"gcih|giac certified incident handler",
            r"ciscp|cisco certified",
            r"aws certified|amazon web services",
            r"azure certified|microsoft azure",
            r"pmp|project management professional",
            r"itil certification",
        ]
        
        self.clearance_patterns = [
            r"secret clearance",
            r"top secret clearance",
            r"ts/sci|top secret/sci",
            r"public trust",
            r"security clearance required",
            r"clearance required",
            r"ability to obtain clearance",
            r"polygraph required",
        ]
        
        # Technology and tool keywords
        self.tech_keywords = {
            'programming': ['python', 'java', 'c++', 'javascript', 'sql', 'r', 'matlab'],
            'cybersecurity': ['firewall', 'ids', 'ips', 'siem', 'vulnerability', 'penetration'],
            'cloud': ['aws', 'azure', 'gcp', 'cloud computing', 'kubernetes', 'docker'],
            'data': ['data analysis', 'big data', 'machine learning', 'ai', 'analytics'],
            'networking': ['tcp/ip', 'routing', 'switching', 'vpn', 'dns', 'dhcp'],
            'os': ['windows', 'linux', 'unix', 'macos', 'active directory'],
        }
    
    def extract_qualifications(self, job_text: str) -> List[Qualification]:
        """Extract all qualifications from job posting text."""
        qualifications = []
        
        # Clean and normalize text
        text = self._clean_text(job_text)
        
        # Extract different types of qualifications
        qualifications.extend(self._extract_education(text))
        qualifications.extend(self._extract_experience(text))
        qualifications.extend(self._extract_skills(text))
        qualifications.extend(self._extract_certifications(text))
        qualifications.extend(self._extract_clearance(text))
        
        return qualifications
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for processing."""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\+\-\.\,\:\;\/\(\)]', ' ', text)
        
        return text.strip()
    
    def _extract_education(self, text: str) -> List[Qualification]:
        """Extract education requirements."""
        qualifications = []
        
        for pattern in self.education_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                qual_text = match.group(0)
                keywords = self._extract_keywords(qual_text)
                weight = self._calculate_weight(qual_text, 'education')
                
                qualification = Qualification(
                    text=qual_text,
                    category='education',
                    weight=weight,
                    keywords=keywords,
                    required=self._is_required(text, match.start(), match.end())
                )
                qualifications.append(qualification)
        
        return qualifications
    
    def _extract_experience(self, text: str) -> List[Qualification]:
        """Extract experience requirements."""
        qualifications = []
        
        for pattern in self.experience_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                qual_text = match.group(0)
                keywords = self._extract_keywords(qual_text)
                weight = self._calculate_weight(qual_text, 'experience')
                
                qualification = Qualification(
                    text=qual_text,
                    category='experience',
                    weight=weight,
                    keywords=keywords,
                    required=self._is_required(text, match.start(), match.end())
                )
                qualifications.append(qualification)
        
        return qualifications
    
    def _extract_skills(self, text: str) -> List[Qualification]:
        """Extract skill requirements."""
        qualifications = []
        
        # Extract from patterns first
        self._extract_skills_from_patterns(text, qualifications)
        
        # Extract technology keywords
        self._extract_tech_skills(text, qualifications)
        
        return qualifications
    
    def _extract_skills_from_patterns(self, text: str, qualifications: List[Qualification]) -> None:
        """Extract skills using regex patterns."""
        for pattern in self.skill_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    skill_list = match.group(1)
                    # Parse individual skills
                    skills = [s.strip() for s in re.split(r'[,;]', skill_list) if s.strip()]
                    
                    for skill in skills:
                        keywords = self._extract_keywords(skill)
                        weight = self._calculate_weight(skill, 'skill')
                        
                        qualification = Qualification(
                            text=skill,
                            category='skill',
                            weight=weight,
                            keywords=keywords,
                            required=self._is_required(text, match.start(), match.end())
                        )
                        qualifications.append(qualification)
    
    def _extract_tech_skills(self, text: str, qualifications: List[Qualification]) -> None:
        """Extract technology keywords as skills."""
        for category, tech_list in self.tech_keywords.items():
            for tech in tech_list:
                if tech in text:
                    keywords = [tech]
                    weight = self._calculate_weight(tech, 'skill')
                    
                    qualification = Qualification(
                        text=tech,
                        category='skill',
                        weight=weight,
                        keywords=keywords,
                        required=True  # Assume tech skills are generally required
                    )
                    qualifications.append(qualification)
    
    def _extract_certifications(self, text: str) -> List[Qualification]:
        """Extract certification requirements."""
        qualifications = []
        
        for pattern in self.certification_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                qual_text = match.group(0)
                keywords = self._extract_keywords(qual_text)
                weight = self._calculate_weight(qual_text, 'certification')
                
                qualification = Qualification(
                    text=qual_text,
                    category='certification',
                    weight=weight,
                    keywords=keywords,
                    required=self._is_required(text, match.start(), match.end())
                )
                qualifications.append(qualification)
        
        return qualifications
    
    def _extract_clearance(self, text: str) -> List[Qualification]:
        """Extract security clearance requirements."""
        qualifications = []
        
        for pattern in self.clearance_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                qual_text = match.group(0)
                keywords = self._extract_keywords(qual_text)
                weight = self._calculate_weight(qual_text, 'clearance')
                
                qualification = Qualification(
                    text=qual_text,
                    category='clearance',
                    weight=weight,
                    keywords=keywords,
                    required=True  # Clearance is typically required
                )
                qualifications.append(qualification)
        
        return qualifications
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from qualification text."""
        # Simple keyword extraction - split on common separators
        keywords = re.findall(r'\b\w+\b', text.lower())
        # Filter out common words
        stop_words = {'the', 'and', 'or', 'of', 'in', 'to', 'with', 'for', 'is', 'are', 'be'}
        return [kw for kw in keywords if kw not in stop_words and len(kw) > 2]
    
    def _calculate_weight(self, text: str, category: str) -> float:
        """Calculate importance weight for a qualification."""
        base_weights = {
            'education': 0.8,
            'experience': 0.9,
            'skill': 0.7,
            'certification': 0.6,
            'clearance': 0.5
        }
        
        weight = base_weights.get(category, 0.5)
        
        # Adjust based on text content
        if 'required' in text.lower():
            weight += 0.1
        elif 'preferred' in text.lower() or 'desired' in text.lower():
            weight -= 0.1
        
        return min(1.0, max(0.1, weight))
    
    def _is_required(self, full_text: str, start: int, end: int) -> bool:
        """Determine if a qualification is required vs preferred."""
        # Look at surrounding context
        context_start = max(0, start - 50)
        context_end = min(len(full_text), end + 50)
        context = full_text[context_start:context_end]
        
        required_indicators = ['required', 'must', 'mandatory', 'essential']
        preferred_indicators = ['preferred', 'desired', 'nice to have', 'plus']
        
        required_count = sum(1 for indicator in required_indicators if indicator in context)
        preferred_count = sum(1 for indicator in preferred_indicators if indicator in context)
        
        return required_count >= preferred_count


class JobQualificationAnalyzer:
    """Analyzes and ranks jobs based on qualification matching."""
    
    def __init__(self):
        self.extractor = QualificationExtractor()
        self.logger = logging.getLogger(__name__)
    
    def process_job_posting(self, job_data: Dict) -> JobPosting:
        """Process a single job posting and extract qualifications."""
        
        # Extract text fields for analysis
        text_fields = [
            job_data.get('qualifications_summary', ''),
            job_data.get('job_summary', ''),
            job_data.get('position_title', ''),
            job_data.get('major_duties', ''),
        ]
        
        full_text = ' '.join(filter(None, text_fields))
        
        # Extract qualifications
        qualifications = self.extractor.extract_qualifications(full_text)
        
        # Categorize qualifications
        education_reqs = [q.text for q in qualifications if q.category == 'education']
        experience_reqs = [q.text for q in qualifications if q.category == 'experience']
        skill_reqs = [q.text for q in qualifications if q.category == 'skill']
        cert_reqs = [q.text for q in qualifications if q.category == 'certification']
        clearance_reqs = [q.text for q in qualifications if q.category == 'clearance']
        
        # Create enhanced job posting
        job_posting = JobPosting(
            job_id=job_data.get('position_id', ''),
            title=job_data.get('position_title', ''),
            agency=job_data.get('organization', ''),
            location=job_data.get('locations', []),
            salary_range=job_data.get('salary_range', ''),
            grade_level=job_data.get('grade_level', ''),
            application_deadline=job_data.get('application_close_date', ''),
            url=job_data.get('position_uri', ''),
            qualifications=qualifications,
            education_requirements=education_reqs,
            experience_requirements=experience_reqs,
            skill_requirements=skill_reqs,
            certification_requirements=cert_reqs,
            clearance_requirements=clearance_reqs,
            extraction_date=datetime.now().isoformat(),
        )
        
        # Calculate scores
        job_posting.relevance_score = self._calculate_relevance_score(qualifications)
        job_posting.entry_level_score = self._calculate_entry_level_score(qualifications)
        
        return job_posting
    
    def _calculate_relevance_score(self, qualifications: List[Qualification]) -> float:
        """Calculate relevance score based on qualifications."""
        if not qualifications:
            return 0.0
        
        total_weight = sum(q.weight for q in qualifications)
        cybersec_weight = sum(q.weight for q in qualifications 
                            if any(kw in ['cyber', 'security', 'information'] 
                                  for kw in q.keywords))
        
        return min(1.0, cybersec_weight / max(1, total_weight))
    
    def _calculate_entry_level_score(self, qualifications: List[Qualification]) -> float:
        """Calculate entry-level suitability score."""
        entry_level_indicators = ['entry', 'junior', 'recent', 'graduate', 'intern']
        high_exp_indicators = ['senior', 'lead', 'principal', '5+', '10+']
        
        entry_score = 0.0
        penalty_score = 0.0
        
        for qual in qualifications:
            qual_text = qual.text.lower()
            
            # Positive indicators
            if any(indicator in qual_text for indicator in entry_level_indicators):
                entry_score += qual.weight
            
            # Negative indicators
            if any(indicator in qual_text for indicator in high_exp_indicators):
                penalty_score += qual.weight
        
        # Calculate final score (0.0 to 1.0)
        total_weight = sum(q.weight for q in qualifications)
        if total_weight == 0:
            return 0.5  # Neutral if no qualifications found
        
        final_score = (entry_score - penalty_score) / total_weight
        return max(0.0, min(1.0, (final_score + 1.0) / 2.0))  # Normalize to 0-1
    
    def rank_jobs_by_qualifications(self, user_profile: Dict, jobs: List[JobPosting]) -> List[Tuple[JobPosting, float]]:
        """Rank jobs based on how well they match user qualifications."""
        
        ranked_jobs = []
        
        for job in jobs:
            match_score = self._calculate_match_score(user_profile, job)
            ranked_jobs.append((job, match_score))
        
        # Sort by match score (highest first)
        ranked_jobs.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_jobs
    
    def _calculate_match_score(self, user_profile: Dict, job: JobPosting) -> float:
        """Calculate how well a job matches a user's profile."""
        
        user_skills = set(user_profile.get('skills', []))
        user_education = user_profile.get('education_level', '')
        user_experience = user_profile.get('years_experience', 0)
        user_certifications = set(user_profile.get('certifications', []))
        
        return self._compute_qualification_match(job, user_skills, user_education, user_experience, user_certifications)
    
    def _compute_qualification_match(self, job: JobPosting, user_skills: Set[str], 
                                   user_education: str, user_experience: int, 
                                   user_certifications: Set[str]) -> float:
        """Compute the qualification match score for a job."""
        total_score = 0.0
        max_possible_score = 0.0
        
        for qual in job.qualifications:
            max_possible_score += qual.weight
            score_gained = 0.0
            
            if qual.category == 'skill':
                score_gained = self._score_skill_match(qual, user_skills)
            elif qual.category == 'education':
                score_gained = self._score_education_match(qual, user_education)
            elif qual.category == 'experience':
                score_gained = self._score_experience_match(qual, user_experience)
            elif qual.category == 'certification':
                score_gained = self._score_certification_match(qual, user_certifications)
            
            total_score += score_gained
        
        # Return normalized score
        return total_score / max_possible_score if max_possible_score > 0 else 0.0
    
    def _score_skill_match(self, qual: Qualification, user_skills: Set[str]) -> float:
        """Score skill qualification match."""
        qual_keywords = set(qual.keywords)
        return qual.weight if qual_keywords.intersection(user_skills) else 0.0
    
    def _score_education_match(self, qual: Qualification, user_education: str) -> float:
        """Score education qualification match."""
        return qual.weight if user_education.lower() in qual.text.lower() else 0.0
    
    def _score_experience_match(self, qual: Qualification, user_experience: int) -> float:
        """Score experience qualification match."""
        years_match = re.search(r'(\d+)', qual.text)
        if years_match:
            required_years = int(years_match.group(1))
            return qual.weight if user_experience >= required_years else 0.0
        else:
            # If no specific years mentioned, give partial credit
            return qual.weight * 0.5
    
    def _score_certification_match(self, qual: Qualification, user_certifications: Set[str]) -> float:
        """Score certification qualification match."""
        qual_keywords = set(qual.keywords)
        return qual.weight if qual_keywords.intersection(user_certifications) else 0.0


def main():
    """Demo function for testing the qualification extractor."""
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Sample job posting data
    sample_job = {
        'position_id': 'TEST-001',
        'position_title': 'Cybersecurity Analyst',
        'organization': 'Department of Defense',
        'locations': ['Washington, DC'],
        'salary_range': '$65,000 - $85,000',
        'grade_level': 'GS-12',
        'application_close_date': '2025-09-30',
        'position_uri': 'https://example.com/job/1',
        'qualifications_summary': '''
        Bachelor's degree in Computer Science, Cybersecurity, or related field required.
        2-3 years of experience in information security preferred.
        Must have knowledge of network security protocols and vulnerability assessment.
        Security+ certification desired. 
        Ability to obtain Secret clearance required.
        Experience with Python, SQL, and SIEM tools a plus.
        ''',
        'job_summary': 'Analyze cybersecurity threats and implement security measures.',
    }
    
    # Initialize analyzer
    analyzer = JobQualificationAnalyzer()
    
    # Process job posting
    job_posting = analyzer.process_job_posting(sample_job)
    
    # Display results
    print("🔍 Job Qualification Analysis Results")
    print("=" * 50)
    print(f"Job Title: {job_posting.title}")
    print(f"Agency: {job_posting.agency}")
    print(f"Relevance Score: {job_posting.relevance_score:.2f}")
    print(f"Entry-Level Score: {job_posting.entry_level_score:.2f}")
    print(f"Total Qualifications Found: {len(job_posting.qualifications)}")
    
    print("\n📋 Extracted Qualifications:")
    for i, qual in enumerate(job_posting.qualifications, 1):
        print(f"{i}. {qual.category.upper()}: {qual.text}")
        print(f"   Weight: {qual.weight:.2f}, Required: {qual.required}")
        print(f"   Keywords: {', '.join(qual.keywords[:5])}")
        print()
    
    # Sample user profile for matching
    user_profile = {
        'skills': ['python', 'network security', 'vulnerability assessment'],
        'education_level': 'Bachelor\'s degree',
        'years_experience': 2,
        'certifications': ['security+']
    }
    
    # Calculate match score
    match_score = analyzer._calculate_match_score(user_profile, job_posting)
    print(f"🎯 Match Score for Sample User: {match_score:.2f}")


if __name__ == "__main__":
    main()