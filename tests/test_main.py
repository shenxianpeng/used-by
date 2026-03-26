import sys
import tempfile
import os
import pytest
import pytest_mock
import requests
from bs4 import BeautifulSoup
from used_by.main import (
    get_soup,
    get_repo_number,
    get_dependents_number,
    generate_badge_url,
    generate_markdown_badge,
    generate_rst_badge,
    get_existing_badge,
    add_new_badge,
    update_existing_badge,
    print_badge_content,
    main,
)
from used_by import COMMENT_MARKER, RST_COMMENT_MARKER

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


def test_get_soup_raises_on_http_error(mocker):
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mocker.patch("requests.get", return_value=mock_response)
    with pytest.raises(requests.HTTPError):
        get_soup("http://example.com/notfound")


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


def test_get_existing_rst_badge(mocker):
    file_path = "dummy_file.rst"
    badge_content = ".. image:: https://example.com/badge\n   :target: https://github.com/user/repo/network/dependents\n   :alt: Used by"
    file_data = f"{RST_COMMENT_MARKER}\n{badge_content}\n{RST_COMMENT_MARKER}\n"
    mocker.patch("builtins.open", mocker.mock_open(read_data=file_data))
    badge = get_existing_badge(file_path)
    assert badge == badge_content


def test_get_existing_rst_badge_returns_empty_when_no_badge(mocker):
    file_path = "dummy_file.rst"
    mocker.patch("builtins.open", mocker.mock_open(read_data="No badge here\n"))
    badge = get_existing_badge(file_path)
    assert badge == ""


def test_add_new_badge_rst_writes_with_markers():
    badge_content = ".. image:: https://example.com/badge\n   :target: https://github.com/user/repo/network/dependents\n   :alt: Used by"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".rst", delete=False) as f:
        f.write("Existing content\n")
        tmp = f.name
    try:
        add_new_badge(tmp, badge_content)
        with open(tmp, encoding="utf-8") as f:
            written = f.read()
        assert f"\n{RST_COMMENT_MARKER}\n{badge_content}\n{RST_COMMENT_MARKER}\n" in written
        assert "Existing content" in written
    finally:
        os.unlink(tmp)


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


# Tests for main()


def test_main_adds_new_md_badge(mocker):
    mocker.patch("sys.argv", ["used-by", "--repo", "user/repo"])
    mocker.patch("used_by.main.get_existing_badge", return_value="")
    mocker.patch("used_by.main.get_dependents_number", return_value=10)
    mocker.patch("used_by.main.generate_markdown_badge", return_value="new_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_add = mocker.patch("used_by.main.add_new_badge")

    main()

    mock_add.assert_called_once_with("README.md", "new_badge")


def test_main_updates_existing_md_badge(mocker):
    mocker.patch(
        "sys.argv",
        ["used-by", "--repo", "user/repo", "--update-badge", "true"],
    )
    mocker.patch("used_by.main.get_existing_badge", return_value="old_badge")
    mocker.patch("used_by.main.get_dependents_number", return_value=10)
    mocker.patch("used_by.main.generate_markdown_badge", return_value="new_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_update = mocker.patch("used_by.main.update_existing_badge")

    main()

    mock_update.assert_called_once_with("README.md", "old_badge", "new_badge")


def test_main_skips_update_when_badge_unchanged(mocker):
    mocker.patch("sys.argv", ["used-by", "--repo", "user/repo"])
    mocker.patch("used_by.main.get_existing_badge", return_value="same_badge")
    mocker.patch("used_by.main.get_dependents_number", return_value=10)
    mocker.patch("used_by.main.generate_markdown_badge", return_value="same_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_update = mocker.patch("used_by.main.update_existing_badge")
    mock_add = mocker.patch("used_by.main.add_new_badge")

    main()

    mock_update.assert_not_called()
    mock_add.assert_not_called()


def test_main_adds_new_rst_badge(mocker):
    mocker.patch(
        "sys.argv",
        ["used-by", "--repo", "user/repo", "--file-path", "README.rst"],
    )
    mocker.patch("used_by.main.get_existing_badge", return_value="")
    mocker.patch("used_by.main.get_dependents_number", return_value=5)
    mock_rst = mocker.patch("used_by.main.generate_rst_badge", return_value="rst_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_add = mocker.patch("used_by.main.add_new_badge")

    main()

    mock_rst.assert_called_once()
    mock_add.assert_called_once_with("README.rst", "rst_badge")


def test_main_updates_existing_rst_badge(mocker):
    mocker.patch(
        "sys.argv",
        ["used-by", "--repo", "user/repo", "--file-path", "README.rst", "--update-badge", "true"],
    )
    mocker.patch("used_by.main.get_existing_badge", return_value="old_rst_badge")
    mocker.patch("used_by.main.get_dependents_number", return_value=5)
    mocker.patch("used_by.main.generate_rst_badge", return_value="new_rst_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_update = mocker.patch("used_by.main.update_existing_badge")

    main()

    mock_update.assert_called_once_with("README.rst", "old_rst_badge", "new_rst_badge")


def test_main_unsupported_file_type(mocker, capsys):
    mocker.patch(
        "sys.argv",
        ["used-by", "--repo", "user/repo", "--file-path", "README.txt"],
    )
    mocker.patch("used_by.main.get_existing_badge", return_value="")
    mocker.patch("used_by.main.get_dependents_number", return_value=5)
    mocker.patch("used_by.main.print_badge_content")
    mock_add = mocker.patch("used_by.main.add_new_badge")

    main()

    mock_add.assert_not_called()
    captured = capsys.readouterr()
    assert "Unsupported file type" in captured.out
