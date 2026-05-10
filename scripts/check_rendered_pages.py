from html.parser import HTMLParser
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app


PAGES = [
    ('Home', '/'),
    ('Planner', '/planner'),
    ('Unit detail', '/unit/CITS3403'),
    ('Degree detail', '/degree/BS-CS'),
    ('Resources', '/resources'),
    ('Benefits', '/benefits'),
    ('Auth', '/auth'),
    ('Settings', '/settings'),
]


class BasicHtmlCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        for name, value in attrs:
            if name == 'id' and value:
                self.ids.add(value)


def run_checks():
    app = create_app('config.TestConfig')
    failures = []
    with app.test_client() as client:
        for label, path in PAGES:
            response = client.get(path)
            if response.status_code != 200:
                failures.append(f'{label} returned {response.status_code}')
                continue
            parser = BasicHtmlCheck()
            parser.feed(response.get_data(as_text=True))
            required = {'html', 'head', 'body', 'title'}
            missing = required - set(parser.tags)
            if missing:
                failures.append(f'{label} missing required tags: {", ".join(sorted(missing))}')
    return failures


if __name__ == '__main__':
    errors = run_checks()
    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)
    print('Rendered page checks passed.')
