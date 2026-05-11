#!/usr/bin/env python3
"""Extract UWA club directory cards from the UWA Student Guild website."""

import re
from datetime import date
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

import yaml


BASE_URL = 'https://www.uwastudentguild.com/clubs'
CLUBS_DIR = Path(__file__).parent.parent / 'data' / 'clubs'
LAST_VERIFIED = date.today().isoformat()


def clean_html(value):
    """Strip tags/entities and normalise whitespace from small HTML snippets."""
    if not value:
        return ''
    text = re.sub(r'<.*?>', '', value, flags=re.S)
    return fix_mojibake(re.sub(r'\s+', ' ', unescape(text)).strip())


def fix_mojibake(value):
    """Repair common UTF-8 text that the Guild page exposes as Windows-1252 text."""
    if not isinstance(value, str) or 'â' not in value:
        return value
    try:
        return value.encode('latin-1').decode('utf-8')
    except UnicodeError:
        return value


def fetch_page(page):
    url = BASE_URL if page == 1 else f'{BASE_URL}?page={page}'
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=20) as response:
        return response.read().decode('utf-8', errors='replace')


def parse_clubs(html):
    card_starts = [
        match.start()
        for match in re.finditer(r'<div class="card card--club[^"]*">', html)
    ]
    card_starts.append(len(html))

    clubs = []
    for index in range(len(card_starts) - 1):
        card = html[card_starts[index]:card_starts[index + 1]]
        link = re.search(
            r'href="/clubs/([^"]+)" title="View more information about ([^"]+)"',
            card,
        )
        if not link:
            continue

        title = re.search(r'<h5 class="card-title card--club__title">(.*?)</h5>', card, re.S)
        subtitle = re.search(r'<p class="h5 card--club__subtitle">(.*?)</p>', card, re.S)
        meta = re.search(r'<span class="badge-pill[^"]*">(.*?)</span>', card, re.S)
        summary = re.search(r'<p class="card-text mt-2 card--club__summary">(.*?)</p>', card, re.S)

        slug = link.group(1).strip()
        name = clean_html(link.group(2))
        abbreviation = clean_html(title.group(1)) if title else ''
        subtitle_name = clean_html(subtitle.group(1)) if subtitle else ''
        if subtitle_name:
            name = subtitle_name

        categories = []
        if meta:
            categories = [
                part.strip().title()
                for part in clean_html(meta.group(1)).split(',')
                if part.strip()
            ]

        description = clean_html(summary.group(1)) if summary else ''
        if description.endswith('...'):
            description = description[:-3].rstrip()
        if not description:
            description = f'{name} is a student club at the University of Western Australia.'

        clubs.append({
            'slug': slug,
            'name': name,
            'abbreviation': abbreviation or None,
            'categories': categories,
            'icon_svg': '<circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.2" fill="none"/>',
            'description': description,
            'contact_email': None,
            'contact_phone': None,
            'website': f'{BASE_URL}/{slug}',
            'room': None,
            'social_media': {
                'instagram': None,
                'facebook': None,
                'discord': None,
            },
            'related_units': [],
            'related_resources': [],
            'source_url': f'{BASE_URL}/{slug}',
            'last_verified': LAST_VERIFIED,
            'active': True,
        })

    return clubs


def scrape_clubs(max_pages=20):
    seen = set()
    clubs = []

    for page in range(1, max_pages + 1):
        page_clubs = parse_clubs(fetch_page(page))
        if not page_clubs:
            break

        for club in page_clubs:
            if club['slug'] in seen:
                continue
            seen.add(club['slug'])
            clubs.append(club)

    return clubs


def write_missing_clubs(clubs):
    CLUBS_DIR.mkdir(parents=True, exist_ok=True)
    created = []
    skipped = []

    for club in clubs:
        path = CLUBS_DIR / f"{club['slug']}.yaml"
        if path.exists():
            skipped.append(path.name)
            continue

        content = '# Club data sourced from the UWA Student Guild clubs directory.\n'
        content += yaml.safe_dump(club, sort_keys=False, allow_unicode=True)
        path.write_text(content, encoding='utf-8')
        created.append(path.name)

    return created, skipped


def main():
    clubs = scrape_clubs()
    created, skipped = write_missing_clubs(clubs)

    print(f'Found {len(clubs)} clubs in the Guild directory.')
    print(f'Created {len(created)} new club files.')
    print(f'Skipped {len(skipped)} existing club files.')


if __name__ == '__main__':
    main()
