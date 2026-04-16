import os
import markdown
from flask import Blueprint, render_template, redirect, url_for, abort

docs_bp = Blueprint('docs', __name__)

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs')

# Extensions enabled for all docs pages:
#   fenced_code  — ``` code blocks
#   tables       — GFM-style tables
#   toc          — generates <div class="toc"> and adds id= to headings
#   attr_list    — lets authors add HTML attributes to elements
MD_EXTENSIONS = ['fenced_code', 'tables', 'toc', 'attr_list']


def _get_all_docs():
    """
    Return a sorted list of dicts for every .md file in the docs/ directory.
    Each dict has 'slug' and 'title' (derived from the first H1, or the filename).
    """
    if not os.path.exists(DOCS_DIR):
        return []
    docs = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if not filename.endswith('.md'):
            continue
        slug = filename[:-3]
        # Default title from filename, overridden by the first H1 in the file.
        title = slug.replace('-', ' ').replace('_', ' ').title()
        path = os.path.join(DOCS_DIR, filename)
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
        docs.append({'slug': slug, 'title': title})
    return docs


@docs_bp.route('/docs')
@docs_bp.route('/docs/')
def index():
    """Redirect /docs to the first available doc page."""
    all_docs = _get_all_docs()
    if not all_docs:
        abort(404)
    return redirect(url_for('docs.page', slug=all_docs[0]['slug']))


@docs_bp.route('/docs/<slug>')
def page(slug):
    """Render a single docs page from docs/<slug>.md."""
    path = os.path.join(DOCS_DIR, f'{slug}.md')
    if not os.path.exists(path):
        abort(404)

    with open(path, encoding='utf-8') as f:
        source = f.read()

    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    content_html = md.convert(source)
    # The toc extension attaches a .toc attribute containing the rendered TOC HTML.
    toc_html = getattr(md, 'toc', '')

    return render_template(
        'docs/page.html',
        content=content_html,
        toc=toc_html,
        slug=slug,
        all_docs=_get_all_docs(),
    )
