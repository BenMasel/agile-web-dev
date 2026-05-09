# Roadmap

This page tracks what's planned, in progress, and being considered for future development.

---

## Near-term

- **Migrations** — add a repeatable Flask-Migrate setup for clean database creation and upgrades
- **Selenium coverage** — add live-browser tests for the main assessed journeys
- **Frontend quality sweep** — improve focus states, responsive checks, no-JavaScript empty states, and API key handling
- **Bookmarking** — let signed-in users save useful benefits and resources

---

## Medium-term

- **Timetable clash detection** — flag units that run in conflicting time slots
- **Prerequisite graph** — visual map of prerequisite chains for a given degree
- **Contribution workflow** — in-app form to suggest corrections to unit data, which opens a GitHub PR automatically

---

## Long-term

- **Mobile app** — React Native wrapper around the same data API
- **Notifications** — opt-in alerts for unit changes, new resources, and exam schedule updates

---

## Ideas Under Consideration

These aren't committed to but are being discussed:

- **GPA calculator** — weighted average tool that respects UWA's grade scale
- **Unit comparison** — side-by-side view of two units (workload, outcomes, prerequisites)
- **Alumni notes** — tips from students who have already completed a unit

---

## Won't Do

To keep the scope manageable:

- **Lecture recordings** — these are already hosted on LMS and linking to them would require institutional access
- **Timetable builder** — the official UWA timetable tool already does this well; we'd rather link to it
