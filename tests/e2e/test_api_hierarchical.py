#!/usr/bin/env python
"""
Test script for hierarchical navigation API endpoints.

This tests the complete user journey:
1. List universities
2. Get university → colleges
3. Get college → departments
4. Get department → professors
5. Get professor → laboratories
6. Get laboratory → members and papers
"""

import json
from sqlalchemy.orm import Session
from src.core.database import SessionLocal
from src.domain.models import (
    University, College, Department, Professor, Laboratory, ResearchPaper
)


def test_hierarchical_navigation():
    """Test the hierarchical navigation flow"""
    db = SessionLocal()

    try:
        print("=" * 80)
        print("🚀 Testing Hierarchical Navigation API")
        print("=" * 80)

        # 1. Get all universities
        print("\n1️⃣  UNIVERSITIES")
        print("-" * 80)
        universities = db.query(University).all()
        print(f"Total universities: {len(universities)}")
        for uni in universities:
            print(f"  📍 {uni.name_ko} (ID: {uni.id})")
            print(f"     Ranking: #{uni.ranking}, Tier: {uni.tier.name}")
            print(f"     Colleges: {len(uni.colleges)}")

        # 2. Get first university's colleges
        print("\n2️⃣  COLLEGES")
        print("-" * 80)
        if universities:
            uni = universities[0]
            print(f"University: {uni.name_ko}")
            for college in uni.colleges:
                print(f"  📚 {college.name_ko} (ID: {college.id})")
                print(f"     Departments: {len(college.departments)}")

                # 3. Get college's departments
                print(f"\n3️⃣  DEPARTMENTS in {college.name_ko}")
                print("-" * 80)
                for dept in college.departments:
                    print(f"  🏛️  {dept.name_ko} (ID: {dept.id})")
                    print(f"     Faculty: {dept.faculty_count}")
                    print(f"     Professors: {len(dept.professors)}")

                    # 4. Get department's professors
                    print(f"\n4️⃣  PROFESSORS in {dept.name_ko}")
                    print("-" * 80)
                    for prof in dept.professors:
                        print(f"  👨‍🏫 {prof.name_ko} (ID: {prof.id})")
                        print(f"     Title: {prof.title}")
                        print(f"     H-Index: {prof.h_index}")
                        print(f"     Publications: {prof.publications_count}")
                        print(f"     Research Interests: {prof.research_interests}")
                        print(f"     Laboratories: {len(prof.laboratories)}")

                        # 5. Get professor's laboratories
                        for lab in prof.laboratories:
                            print(f"\n5️⃣  LABORATORY: {lab.name_ko} (ID: {lab.id})")
                            print("-" * 80)
                            print(f"  Research Areas: {lab.research_areas}")
                            desc = lab.description or "No description"
                            desc_preview = desc[:100] + "..." if len(desc) > 100 else desc
                            print(f"  Description: {desc_preview}")
                            print(f"  Current Projects: {lab.current_projects}")
                            print(f"  Funding Info: {lab.funding_info}")
                            print(f"  Facilities: {lab.facilities}")
                            print(f"  Members: {len(lab.members)}")
                            print(f"  Papers: {len(lab.papers)}")

                            # 6. Get lab members
                            print(f"\n6️⃣  LAB MEMBERS")
                            print("-" * 80)
                            for member in lab.members:
                                print(f"  👤 {member.name_ko} ({member.role.value})")
                                print(f"     Email: {member.email}")
                                print(f"     Research Topic: {member.research_topic}")
                                print(f"     Joined: {member.joined_year}")

                            # 7. Get lab papers
                            print(f"\n7️⃣  RESEARCH PAPERS")
                            print("-" * 80)
                            for paper in lab.papers:
                                print(f"  📄 {paper.title}")
                                print(f"     Authors: {paper.authors}")
                                print(f"     Year: {paper.publication_year}")
                                print(f"     Venue: {paper.venue}")
                                print(f"     Citations: {paper.citation_count}")
                                print(f"     Keywords: {paper.keywords}")
                                print(f"     URL: {paper.url}")

        # Print summary statistics
        print("\n" + "=" * 80)
        print("📊 SUMMARY STATISTICS")
        print("=" * 80)
        universities_count = db.query(University).count()
        colleges_count = db.query(College).count()
        departments_count = db.query(Department).count()
        professors_count = db.query(Professor).count()
        labs_count = db.query(Laboratory).count()
        papers_count = db.query(ResearchPaper).count()

        print(f"Universities:  {universities_count}")
        print(f"Colleges:      {colleges_count}")
        print(f"Departments:   {departments_count}")
        print(f"Professors:    {professors_count}")
        print(f"Laboratories:  {labs_count}")
        print(f"Papers:        {papers_count}")

        print("\n✅ All data loaded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    test_hierarchical_navigation()
