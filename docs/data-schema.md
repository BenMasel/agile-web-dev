# Data Schema

All site content is stored as YAML files under `data/`. Each subdirectory has a JSON Schema in `data/schemas/` that defines the required and optional fields. This page documents the structure for each content type.

---

## Units

**Path:** `data/units/<CODE>.yaml` (e.g. `data/units/CITS1001.yaml`)

```yaml
code: CITS1001
title: Software Engineering with Java
level: 1
credit_points: 6
availability: [1]
faculty: Science
school: Computer Science and Software Engineering
source_url: "https://www.handbooks.uwa.edu.au/unitdetails?code=CITS1001"
handbook_year: 2026
last_verified: "2026-04-18"

associated_clubs:
  - physsoc

resources:
  youtube_channels:
    - name: "CS Dojo"
      url: "https://youtube.com/@csdojo"
  platforms:
    - name: "LeetCode"
      url: "https://leetcode.com"
  textbooks:
    - title: "Introduction to Java"
      author: "Daniel Liang"
```

**Required fields:** `code`, `title`, `level`, `credit_points`, `availability`, `faculty`, `school`, `source_url`, `handbook_year`, `last_verified`

---

## Degrees

**Path:** `data/degrees/<slug>.yaml` (e.g. `data/degrees/bachelor-of-engineering.yaml`)

```yaml
slug: bachelor-of-engineering
title: Bachelor of Engineering (Honours)
faculty: Faculty of Engineering and Mathematical Sciences
duration_years: 4
credit_points: 192
source_url: "https://www.handbooks.uwa.edu.au/majordetails?code=MJD-ESOFT"
handbook_year: 2026
last_verified: "2026-04-18"

years:
  - year: 1
    semesters:
      - number: 1
        label: Semester 1
        units:
          - code: GENG1000
            title: Introduction to engineering
            credit_points: 6
            type: core
```

**Required fields:** `slug`, `title`, `faculty`, `duration_years`, `credit_points`, `source_url`, `handbook_year`, `last_verified`, `years`

---

## Clubs

**Path:** `data/clubs/<slug>.yaml` (e.g. `data/clubs/uwa-computing-students-association.yaml`)

```yaml
slug: uwa-computing-students-association
name: UWA Computing Students Association
abbreviation: CASSA
description: |
  The computing and IT student society at UWA. Runs hackathons,
  industry nights, and study sessions.
accent_color: "#6CA0F0"
```

**Required fields:** `slug`, `name`, `abbreviation`, `description`, `accent_color`

---

## Benefits

**Path:** `data/benefits/<category>/<benefit>.yaml`

Benefits are grouped into category folders. Each category has `_category.yaml` metadata and one YAML file per benefit.

```yaml
name: GitHub Student Developer Pack
value: Free
url: "https://education.github.com/pack"
description: Free access to developer tools via GitHub Education.
tags:
  - github
  - dev-tools
```

---

## Schemas

JSON Schemas for each content type live in `data/schemas/`. They are used by the data validation script during development:

```bash
uv run python scripts/validate_data.py
```

The validator checks units, degrees, clubs, benefit categories, and benefits against their schemas. It also checks that real-looking unit codes referenced by degrees or prerequisites exist in `data/units`, and that unit `associated_clubs` references exist in `data/clubs`.
