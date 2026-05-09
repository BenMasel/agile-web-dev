#!/usr/bin/env python3
"""Extract UWA clubs from the UWA Student Guild website."""

import json
import re
import sys
from pathlib import Path

# Clubs extracted from https://www.uwastudentguild.com/clubs
# This is a curated list based on the guild website structure
CLUBS_DATA = [
    {"slug": "180-degrees-consulting", "name": "180 Degrees Consulting", "abbreviation": "180DC", "categories": ["Business", "Volunteering"]},
    {"slug": "8-ball-club", "name": "8 Ball Club", "abbreviation": "8BC", "categories": ["Hobby Activities", "Sports & Fitness"]},
    {"slug": "aiesec", "name": "AIESEC", "abbreviation": "AIESEC", "categories": ["Multicultural", "Volunteering"]},
    {"slug": "amnesty-international-uwa", "name": "Amnesty International UWA", "abbreviation": "AIUWA", "categories": ["Volunteering"]},
    {"slug": "anthropology-society-of-uwa", "name": "Anthropology Society of UWA", "abbreviation": "AnthSoc", "categories": ["Academic"]},
    {"slug": "archaeological-society-of-wa", "name": "Archaeological Society of WA", "abbreviation": "ARCHSOC", "categories": ["Academic", "Arts", "Science"]},
    {"slug": "architecture-landscape-visual-arts-student-society-of-uwa", "name": "Architecture, Landscape & Visual Arts Student Society of UWA", "abbreviation": "ALVA", "categories": ["Academic", "Arts", "Creative"]},
    {"slug": "arts-union-of-uwa", "name": "Arts Union of UWA", "abbreviation": "AU", "categories": ["Arts"]},
    {"slug": "asia-australia-youth-association", "name": "Asia-Australia Youth Association", "abbreviation": "AAYA", "categories": ["Multicultural"]},
    {"slug": "asian-students-in-australia", "name": "Asian Students in Australia", "abbreviation": "ASIA", "categories": ["Multicultural", "Social"]},
    {"slug": "association-of-indonesian-postgraduate-students-and-scholars-in-australia", "name": "Association of Indonesian Postgraduate Students and Scholars in Australia", "abbreviation": "AIPSSA", "categories": ["Multicultural"]},
    {"slug": "australasian-union-of-jewish-students", "name": "Australasian Union of Jewish Students", "abbreviation": "AUJS", "categories": ["Faith"]},
    {"slug": "australia-china-youth-association", "name": "Australia-China Youth Association", "abbreviation": "ACYA", "categories": ["Multicultural", "Social"]},
    {"slug": "bachelor-of-philosophy-honours-union", "name": "Bachelor of Philosophy (Honours) Union", "abbreviation": "BPhil", "categories": ["Academic"]},
    {"slug": "bahai-society", "name": "Baha'i Society", "abbreviation": "Bahai", "categories": ["Faith"]},
    {"slug": "biomedical-engineering-society-of-wa", "name": "Biomedical Engineering Society of WA", "abbreviation": "BES", "categories": ["Engineering"]},
    {"slug": "blackstone-society", "name": "Blackstone Society", "abbreviation": "Blackstone", "categories": ["Academic", "Law"]},
    {"slug": "bloom-uwa", "name": "Bloom UWA", "abbreviation": "Bloom", "categories": ["Business"]},
    {"slug": "chemical-and-process-engineering-club-the-cpec", "name": "Chemical & Process Engineering Club UWA", "abbreviation": "CPEC", "categories": ["Engineering"]},
    {"slug": "chemnbio-molecular-sciences-club", "name": "CHeMnBiO Molecular Sciences Club", "abbreviation": "CHeMnBiO", "categories": ["Academic", "Science"]},
]

def generate_club_yaml(club_data):
    """Generate YAML content for a club."""
    yaml_content = f"""# PLACEHOLDER - this club data is from UWA Student Guild and used for development/testing.
# If you have more accurate information or additional details, please submit a PR.
slug: {club_data['slug']}
name: {club_data['name']}
abbreviation: {club_data['abbreviation']}
categories: {club_data['categories']}

# icon_svg is rendered raw into an <svg> tag via Jinja's |safe filter.
# Use currentColor for strokes so the accent_color propagates automatically.
icon_svg: '<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.2" fill="none"/>'

description: >
  {club_data['name']} is a student club at the University of Western Australia. 
  For more information, visit the UWA Student Guild website at https://www.uwastudentguild.com/clubs/{club_data['slug']}.

active: true
"""
    return yaml_content

def main():
    base_path = Path(__file__).parent.parent / "data" / "clubs"
    
    print(f"Generating club YAML files in {base_path}")
    
    for club in CLUBS_DATA:
        yaml_content = generate_club_yaml(club)
        filepath = base_path / f"{club['slug']}.yaml"
        
        # Skip if file already exists (don't overwrite existing clubs)
        if filepath.exists():
            print(f"⊘ Skipped {club['slug']} (already exists)")
            continue
        
        filepath.write_text(yaml_content)
        print(f"✓ Created {filepath.name}")
    
    print(f"\nGenerated {len([c for c in CLUBS_DATA if not (base_path / f'{c['slug']}.yaml').exists()])} new club files")

if __name__ == "__main__":
    main()
