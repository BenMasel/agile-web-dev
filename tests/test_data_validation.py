from scripts.validate_data import run_validation


def test_yaml_catalogue_validates_against_schemas():
    assert run_validation() == []


def test_search_index_contains_all_catalogue_types(app):
    from app.routes import build_search_index

    with app.app_context():
        index = build_search_index()

    types = {item['type'] for item in index}
    assert {'unit', 'degree', 'club'} <= types
