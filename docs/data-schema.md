# Data Schema

All site content is stored as YAML files under `data/`. Each subdirectory has a JSON Schema in `data/schemas/` that defines the required and optional fields. This page documents the structure for each content type.

---

## Units

**Path:** `data/units/<CODE>.yaml` (e.g. `data/units/CITS1001.yaml`)

```yaml
code: CITS1001
title: Software Engineering with Java
faculty: Faculty of Engineering and Mathematical Sciences
credit_points: 6
level: 1
semester: 1          # 1, 2, or 12 (both)

associated_clubs:
  - uwa-computing-students-association

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

**Required fields:** `code`, `title`, `faculty`, `credit_points`, `level`, `semester`

---

## Degrees

**Path:** `data/degrees/<slug>.yaml` (e.g. `data/degrees/bachelor-of-engineering.yaml`)

```yaml
slug: bachelor-of-engineering
title: Bachelor of Engineering (Honours)
faculty: Faculty of Engineering and Mathematical Sciences
duration_years: 4
credit_points: 192
```

**Required fields:** `slug`, `title`, `faculty`, `duration_years`, `credit_points`

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

**Path:** `data/benefits/benefits.yaml`

Benefits are grouped into categories. Each category contains a list of benefit objects.

```yaml
categories:
  - id: software
    label: Software
    accent_color: "#6CA0F0"
    accent_bg: "rgba(100, 160, 255, 0.1)"
    description: Free and discounted software for students
    icon_svg: "<path ... />"
    benefits:
      - name: GitHub Student Developer Pack
        value: Free
        url: "https://education.github.com/pack"
        description: Free access to developer tools via GitHub Education.
        tags:
          - github
          - dev-tools
```

---

## Schemas

JSON Schemas for each content type live in `data/schemas/`. They are used to validate YAML files during development. To validate a file manually:

```bash
uv run python -c "
import yaml, json, jsonschema
data = yaml.safe_load(open('data/units/CITS1001.yaml'))
schema = json.load(open('data/schemas/unit.json'))
jsonschema.validate(data, schema)
print('valid')
"
```
