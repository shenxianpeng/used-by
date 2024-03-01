import pytest
from used_by.main import get_soup, get_dependents_number


@pytest.fixture
def sample_html():
    return """
    <div class="select-menu-item">
        <a class="btn-link selected" href="/some_url">42 repos</a>
    </div>
    """


@pytest.fixture
def mocked_get_soup(monkeypatch, sample_html):
    class MockResponse:
        def __init__(self, content):
            self.content = content

    def mock_get(url):
        return MockResponse(sample_html)

    monkeypatch.setattr("used_by.main.requests.get", mock_get)


def test_get_soup(mocked_get_soup):
    soup = get_soup("https://example.com")
    assert soup.find("a", class_="btn-link selected").get_text(strip=True) == "42 repos"


def test_get_dependents_number(mocked_get_soup):
    dependents_number = get_dependents_number("https://example.com")
    assert dependents_number == 42
