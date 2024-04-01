import pytest
import pytest_mock
from bs4 import BeautifulSoup
from used_by.main import (
    get_soup,
    get_repo_number,
    get_dependents_number,
    generate_badge_url,
    generate_markdown_badge,
    generate_rst_badge,
    get_existing_badge,
    update_existing_badge,
    print_badge_content,
)
from used_by import COMMENT_MARKER

# test get_soup using pytest and pytest-mock


@pytest.fixture
def mock_requests_get(mocker):
    mock_response = mocker.MagicMock()
    mock_response.content = b"<html><body><a class='select-menu-item' href='/repo1'></a><a class='select-menu-item' href='/repo2'></a></body></html>"
    mocker.patch("requests.get", return_value=mock_response)


def test_get_soup(mock_requests_get):
    url = "http://example.com"
    soup = get_soup(url)
    assert isinstance(soup, BeautifulSoup)


def test_get_repo_number(mocker):
    html_content = (
        "<a class='btn-link selected' href='http://example.com'>4 Repositories</a>"
    )
    mock_soup = BeautifulSoup(html_content, "html.parser")
    mocker.patch("used_by.main.get_soup", return_value=mock_soup)
    repo_number = get_repo_number(mock_soup)
    assert repo_number == 4


def test_get_dependents_number_when_menu_items_is_empty(mocker):
    url = "http://example.com"
    html_content = (
        "<a class='btn-link selected' href='http://example.com'>4 Repositories</a>"
    )
    mock_soup = BeautifulSoup(html_content, "html.parser")
    mocker.patch("used_by.main.get_soup", return_value=mock_soup)
    dependents_number = get_dependents_number(url)
    assert dependents_number == 4


def test_get_dependents_number_when_menu_items_is_not_empty(mocker):
    url = "http://example.com"
    html_content = b"<a class='select-menu-item' href='/repo1'><a class='btn-link selected' href='http://example.com'>4 Repositories</a></a><a class='select-menu-item' href='/repo2'><a class='btn-link selected' href='http://example.com'>4 Repositories</a></a>"
    mock_soup = BeautifulSoup(html_content, "html.parser")
    mocker.patch("used_by.main.get_soup", return_value=mock_soup)
    dependents_number = get_dependents_number(url)
    assert dependents_number == 8


def test_generate_badge_url():
    deps_number = 4
    badge_label = "Used By"
    badge_color = "blue"
    badge_logo = "github"
    badge_url = "https://img.shields.io/static/v1?label=Used%20By&message=4&color=blue&logo=github"
    assert badge_url == generate_badge_url(
        deps_number, badge_label, badge_color, badge_logo
    )


def test_generate_markdown_badge():
    repo_name = "used-by"
    deps_number = 4
    badge_label = "Used By"
    badge_color = "blue"
    badge_logo = "github"
    badge_content = "[![Used By](https://img.shields.io/static/v1?label=Used%20By&message=4&color=blue&logo=github)](https://github.com/used-by/network/dependents)"
    assert badge_content == generate_markdown_badge(
        repo_name, deps_number, badge_label, badge_color, badge_logo
    )


def test_generate_rst_badge():
    repo_name = "used-by"
    deps_number = 4
    badge_label = "Used By"
    badge_color = "blue"
    badge_logo = "github"
    assert (
        f".. image:: {generate_badge_url(deps_number, badge_label, badge_color, badge_logo)}"
        in generate_rst_badge(
            repo_name, deps_number, badge_label, badge_color, badge_logo
        )
    )
    assert (
        f":target: https://github.com/{repo_name}/network/dependents"
        in generate_rst_badge(
            repo_name, deps_number, badge_label, badge_color, badge_logo
        )
    )
    assert f":alt: {badge_label}" in generate_rst_badge(
        repo_name, deps_number, badge_label, badge_color, badge_logo
    )


def test_get_existing_badge(mocker):
    file_path = "dummy_file.md"
    badge_content = f"badge{COMMENT_MARKER}"
    mocker.patch("builtins.open", mocker.mock_open(read_data=badge_content))
    badge = get_existing_badge(file_path)
    assert badge == "badge"


def test_update_existing_badge(mocker):
    file_path = "dummy_file.md"
    existing_badge = "existing_badge"
    new_badge = "new_badge"
    file_contents = f"{existing_badge}{COMMENT_MARKER}"
    mocker.patch("builtins.open", mocker.mock_open(read_data=file_contents))
    update_existing_badge(file_path, existing_badge, new_badge)
    assert f"{new_badge}{COMMENT_MARKER}" != file_contents


def test_print_existing_badge(capfd):
    badge_string = "badge_content"
    print_badge_content(badge_string, flag=True)

    captured = capfd.readouterr()

    expected_output = (
        "Existing Badge:\n" + "=" * 80 + f"\n{badge_string}\n" + "=" * 80 + "\n\n"
    )
    assert captured.out == expected_output


def test_print_new_badge(capfd):
    badge_string = "badge_content"
    print_badge_content(badge_string, flag=False)

    captured = capfd.readouterr()

    expected_output = (
        "New Badge:\n" + "=" * 80 + f"\n{badge_string}\n" + "=" * 80 + "\n\n"
    )
    assert captured.out == expected_output
