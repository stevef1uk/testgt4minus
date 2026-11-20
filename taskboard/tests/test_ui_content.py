from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_index_contains_required_ui_regions_and_controls():
    html = (ROOT / "templates" / "index.html").read_text()
    for element_id in (
        "project-form-region",
        "project-form",
        "project-list",
        "project-filter",
        "empty-state",
        "loading-state",
        "error-state",
    ):
        assert f'id="{element_id}"' in html


def test_index_loads_static_assets():
    html = (ROOT / "templates" / "index.html").read_text()
    assert 'src="/static/app.js"' in html
    assert 'href="/static/style.css"' in html


def test_app_uses_safe_text_rendering_and_required_api_routes():
    app = (ROOT / "static" / "app.js").read_text()
    assert "textContent" in app
    assert "/api/projects" in app
    assert "replaceChildren" in app