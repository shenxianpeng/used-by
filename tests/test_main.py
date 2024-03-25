import pytest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from used_by.main import (
    get_soup,
    get_dependents_number,
)


@pytest.fixture
def mock_requests_get(mocker):
    mock_response = MagicMock()
    mock_response.content = b"<html><body><a class='select-menu-item' href='/repo1'></a><a class='select-menu-item' href='/repo2'></a></body></html>"
    mocker.patch("requests.get", return_value=mock_response)


@pytest.fixture
def mock_sub_soup(mocker):
    mock_sub_soup = MagicMock()
    mock_sub_soup.find.return_value = MagicMock(
        get_text=MagicMock(return_value="3 repositories")
    )
    mocker.patch("used_by.main.get_soup", return_value=mock_sub_soup)


def test_get_soup(mock_requests_get):
    url = "http://example.com"
    soup = get_soup(url)
    assert isinstance(soup, BeautifulSoup)


def test_get_dependents_number(mock_requests_get, mock_sub_soup):
    url = "http://example.com"
    dependents_number = get_dependents_number(url)

    assert dependents_number == 3
