import sys
import tempfile
import os
import pytest
import pytest_mock
import requests
from bs4 import BeautifulSoup
from used_by.main import (
    get_parser,
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
        assert (
            f"\n{RST_COMMENT_MARKER}\n{badge_content}\n{RST_COMMENT_MARKER}\n"
            in written
        )
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
        [
            "used-by",
            "--repo",
            "user/repo",
            "--file-path",
            "README.rst",
            "--update-badge",
            "true",
        ],
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


# Helpers that mimic the markup of https://github.com/<owner>/<repo>/network/dependents

REPO = "octo/demo"
DEPENDENTS_URL = f"https://github.com/{REPO}/network/dependents"


def make_dependents_page(repositories, packages=()):
    """Return a minimal page with the same structure as GitHub's dependents page."""
    menu = "".join(
        f'<a href="{href}" class="select-menu-item" role="menuitemradio">'
        f'<span class="select-menu-item-text">{name}</span></a>'
        for name, href in packages
    )
    return (
        f'<html><body><div class="select-menu-list">{menu}</div>'
        '<div class="table-list-header-toggle states">'
        '<a class="btn-link selected" href="?dependent_type=REPOSITORY">'
        '<svg class="octicon octicon-code-square"><path d="M0 0"></path></svg>'
        f"\n    {repositories}\n    Repositories\n</a>"
        '<a class="btn-link " href="?dependent_type=PACKAGE">'
        '<svg class="octicon octicon-package"></svg>\n    2\n    Packages\n</a>'
        "</div></body></html>"
    ).encode()


@pytest.fixture
def fake_github(mocker):
    """Patch requests.get to serve pages from ``fake_github.pages`` by URL."""
    pages = {}

    def fake_get(url, timeout=None):
        response = mocker.MagicMock()
        if url in pages:
            response.content = pages[url]
        else:
            response.raise_for_status.side_effect = requests.HTTPError(
                f"404 Client Error: Not Found for url: {url}"
            )
        return response

    mock_get = mocker.patch("requests.get", side_effect=fake_get)
    mock_get.pages = pages
    return mock_get


def md_badge(count, repo=REPO):
    return generate_markdown_badge(repo, count, "Used by", "informational", "slickpic")


def rst_badge(count, repo=REPO):
    return generate_rst_badge(repo, count, "Used by", "informational", "slickpic")


def run_main(mocker, *args):
    mocker.patch("sys.argv", ["used-by", "--repo", REPO, *args])
    main()


# get_parser


def test_get_parser_defaults():
    args = get_parser().parse_args(["--repo", REPO])
    assert args.repo == REPO
    assert args.file_path == "README.md"
    assert args.badge_label == "Used by"
    assert args.badge_color == "informational"
    assert args.badge_logo == "slickpic"
    assert args.update_badge is False


def test_get_parser_reads_all_options():
    args = get_parser().parse_args(
        [
            "--repo=octo/demo",
            "--file-path=docs/index.rst",
            "--badge-label=Dependents",
            "--badge-color=green",
            "--badge-logo=github",
            "--update-badge=true",
        ]
    )
    assert args.file_path == "docs/index.rst"
    assert args.badge_label == "Dependents"
    assert args.badge_color == "green"
    assert args.badge_logo == "github"
    assert args.update_badge is True


# get_soup / get_repo_number / get_dependents_number


def test_get_soup_uses_timeout_and_parses_response(fake_github):
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(3)

    soup = get_soup(DEPENDENTS_URL)

    fake_github.assert_called_once_with(DEPENDENTS_URL, timeout=10)
    assert soup.find("a", class_="btn-link selected") is not None


def test_get_repo_number_reads_github_markup():
    soup = BeautifulSoup(make_dependents_page(5), "html.parser")
    assert get_repo_number(soup) == 5


@pytest.mark.parametrize("text", ["Repositories", ""])
def test_get_repo_number_returns_zero_when_count_is_not_a_number(text):
    soup = BeautifulSoup(f"<a class='btn-link selected'>{text}</a>", "html.parser")
    assert get_repo_number(soup) == 0


def test_get_dependents_number_single_package(fake_github):
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(7)

    assert get_dependents_number(DEPENDENTS_URL) == 7
    fake_github.assert_called_once_with(DEPENDENTS_URL, timeout=10)


def test_get_dependents_number_sums_every_package(fake_github):
    package_a = f"/{REPO}/network/dependents?package_id=UGFja2FnZS0x"
    package_b = f"/{REPO}/network/dependents?package_id=UGFja2FnZS0y%3D%3D"
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(
        5, packages=[("demo", package_a), ("octo/demo", package_b)]
    )
    fake_github.pages[f"https://github.com{package_a}"] = make_dependents_page(5)
    fake_github.pages[f"https://github.com{package_b}"] = make_dependents_page(2)

    assert get_dependents_number(DEPENDENTS_URL) == 7
    assert [call.args[0] for call in fake_github.call_args_list] == [
        DEPENDENTS_URL,
        f"https://github.com{package_a}",
        f"https://github.com{package_b}",
    ]


def test_get_dependents_number_propagates_http_errors(fake_github):
    with pytest.raises(requests.HTTPError):
        get_dependents_number(DEPENDENTS_URL)


# badge generation


def test_generate_badge_url_quotes_label():
    url = generate_badge_url(1, "Used by & co", "blue", "github")
    assert "label=Used%20by%20%26%20co&message=1&" in url


# reading and writing badges in files


def test_get_existing_badge_md_on_later_line(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"# Demo\n\nIntro text.\n{md_badge(3)}{COMMENT_MARKER}\n")
    assert get_existing_badge(readme) == md_badge(3)


def test_get_existing_badge_md_returns_empty_without_marker(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nNo badge yet.\n")
    assert get_existing_badge(readme) == ""


def test_get_existing_badge_rst_extension_is_case_insensitive(tmp_path):
    readme = tmp_path / "README.RST"
    readme.write_text(
        f"Demo\n====\n\n{RST_COMMENT_MARKER}\n{rst_badge(3)}\n{RST_COMMENT_MARKER}\n"
    )
    assert get_existing_badge(readme) == rst_badge(3)


def test_update_existing_badge_rewrites_only_the_badge(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text(f"# Demo\n{md_badge(3)}{COMMENT_MARKER}\nFooter\n")

    update_existing_badge(readme, md_badge(3), md_badge(4))

    assert readme.read_text() == f"# Demo\n{md_badge(4)}{COMMENT_MARKER}\nFooter\n"
    assert capsys.readouterr().out == "Updated existing badge.\n"


def test_add_new_badge_md_appends_badge_with_marker(tmp_path, capsys):
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n")

    add_new_badge(readme, md_badge(3))

    assert readme.read_text() == f"# Demo\n\n{md_badge(3)} {COMMENT_MARKER}"
    assert capsys.readouterr().out == "Added new badge.\n"


# main() end to end, with only the network mocked


def test_main_end_to_end_markdown(tmp_path, monkeypatch, mocker, fake_github):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n")

    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(3)
    run_main(mocker)
    assert readme.read_text() == f"# Demo\n\n{md_badge(3)} {COMMENT_MARKER}"

    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(4)
    run_main(mocker, "--update-badge", "true")
    assert readme.read_text() == f"# Demo\n\n{md_badge(4)}{COMMENT_MARKER}"

    run_main(mocker, "--update-badge", "true")
    assert readme.read_text() == f"# Demo\n\n{md_badge(4)}{COMMENT_MARKER}"


def test_main_end_to_end_rst(tmp_path, monkeypatch, mocker, fake_github):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.rst"
    readme.write_text("Demo\n====\n")

    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(3)
    run_main(mocker, "--file-path", "README.rst")
    expected = f"Demo\n====\n\n{RST_COMMENT_MARKER}\n{{}}\n{RST_COMMENT_MARKER}\n"
    assert readme.read_text() == expected.format(rst_badge(3))

    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(9)
    run_main(mocker, "--file-path", "README.rst", "--update-badge", "true")
    assert readme.read_text() == expected.format(rst_badge(9))


def test_main_keeps_outdated_badge_without_update_flag(
    tmp_path, monkeypatch, mocker, fake_github
):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    original = f"# Demo\n{md_badge(3)}{COMMENT_MARKER}\n"
    readme.write_text(original)
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(4)

    run_main(mocker)

    assert readme.read_text() == original


def test_main_update_flag_without_existing_badge_only_appends(
    tmp_path, monkeypatch, mocker, fake_github
):
    # Regression test: replacing the empty "existing badge" used to insert the
    # new badge between every character of the file.
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text("# Demo\n\nSome text.\n")
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(3)

    run_main(mocker, "--update-badge", "true")

    assert readme.read_text() == (
        f"# Demo\n\nSome text.\n\n{md_badge(3)} {COMMENT_MARKER}"
    )


def test_main_update_flag_without_existing_badge_skips_update(mocker):
    mocker.patch("used_by.main.get_existing_badge", return_value="")
    mocker.patch("used_by.main.get_dependents_number", return_value=10)
    mocker.patch("used_by.main.generate_markdown_badge", return_value="new_badge")
    mocker.patch("used_by.main.print_badge_content")
    mock_update = mocker.patch("used_by.main.update_existing_badge")
    mock_add = mocker.patch("used_by.main.add_new_badge")

    run_main(mocker, "--update-badge", "true")

    mock_update.assert_not_called()
    mock_add.assert_called_once_with("README.md", "new_badge")


@pytest.mark.parametrize("text, expected", [("1,234", 1234), ("4,237,401", 4237401)])
def test_get_repo_number_handles_thousands_separators(text, expected):
    # Regression test: GitHub formats large counts as "4,237,401 Repositories".
    soup = BeautifulSoup(make_dependents_page(text), "html.parser")
    assert get_repo_number(soup) == expected


def test_get_dependents_number_sums_large_package_counts(fake_github):
    package = f"/{REPO}/network/dependents?package_id=UGFja2FnZS0x"
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(
        "1,234", packages=[("demo", package)]
    )
    fake_github.pages[f"https://github.com{package}"] = make_dependents_page("1,234")

    assert get_dependents_number(DEPENDENTS_URL) == 1234


def test_get_repo_number_raises_clear_error_when_counter_is_missing():
    # e.g. GitHub changed its markup or served an unexpected page
    soup = BeautifulSoup(
        "<html><body>Something went wrong</body></html>", "html.parser"
    )
    with pytest.raises(ValueError, match="Could not find the dependents count"):
        get_repo_number(soup)


def test_main_fails_without_touching_file_when_counter_is_missing(
    tmp_path, monkeypatch, mocker, fake_github
):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    original = f"# Demo\n{md_badge(3)}{COMMENT_MARKER}\n"
    readme.write_text(original)
    fake_github.pages[DEPENDENTS_URL] = b"<html><body>Unexpected page</body></html>"

    with pytest.raises(ValueError):
        run_main(mocker, "--update-badge", "true")

    assert readme.read_text() == original


@pytest.mark.parametrize("value", ["false", "False", "FALSE", "0", "no", "off", ""])
def test_get_parser_update_badge_false_values(value):
    # Regression test: the action passes --update-badge=false by default, which
    # used to be kept as the (truthy) string "false".
    args = get_parser().parse_args(["--repo", REPO, f"--update-badge={value}"])
    assert args.update_badge is False


@pytest.mark.parametrize("value", ["true", "True", "1", "yes", "on"])
def test_get_parser_update_badge_true_values(value):
    args = get_parser().parse_args(["--repo", REPO, f"--update-badge={value}"])
    assert args.update_badge is True


def test_main_keeps_outdated_badge_when_update_badge_is_false(
    tmp_path, monkeypatch, mocker, fake_github
):
    monkeypatch.chdir(tmp_path)
    readme = tmp_path / "README.md"
    original = f"# Demo\n{md_badge(3)}{COMMENT_MARKER}\n"
    readme.write_text(original)
    fake_github.pages[DEPENDENTS_URL] = make_dependents_page(4)

    run_main(mocker, "--update-badge=false")

    assert readme.read_text() == original
