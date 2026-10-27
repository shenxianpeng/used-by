import argparse
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from pathlib import Path
from used_by import COMMENT_MARKER, RST_COMMENT_MARKER
from used_by.sources import (
    DEPS_DEV_ECOSYSTEMS,
    get_deps_dev_count,
)

SOURCES = ("github", "deps.dev")

FALSE_VALUES = {"", "0", "f", "false", "n", "no", "off"}
# A Markdown image link such as [![Used by](<image url>)](<link url>) that is
# followed only by whitespace, i.e. the badge right before the comment marker.
MD_BADGE_PATTERN = re.compile(r"\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\)(?=\s*$)")
# The count shown by a badge, e.g. "...&message=42&color=..." -> "42".
BADGE_COUNT_PATTERN = re.compile(r"[?&]message=(\d+)(?:&|\s|$)")


def str_to_bool(value: str) -> bool:
    """Parse a flag value such as an action input ("false" -> False)."""
    return value.strip().lower() not in FALSE_VALUES


def percentage(value: str) -> int:
    """Parse a whole-number percentage between 0 and 100."""
    try:
        number = int(value)
    except ValueError:
        number = -1
    if not 0 <= number <= 100:
        raise argparse.ArgumentTypeError(
            f"must be a whole number between 0 and 100, got {value!r}"
        )
    return number


def get_parser():
    parser = argparse.ArgumentParser(
        prog="used-by",
        description=(
            "Generate a Used By badge from GitHub dependents or deps.dev " "dependents."
        ),
    )

    parser.add_argument(
        "--source",
        default="github",
        choices=SOURCES,
        help=(
            "Where the count comes from: GitHub dependents of --repo, or "
            "deps.dev dependents of --package in --ecosystem. Defaults to github."
        ),
    )

    parser.add_argument(
        "--repo",
        help="GitHub repository name (e.g., shenxianpeng/used-by). Required for --source github.",
    )

    parser.add_argument(
        "--package",
        help="Package name for --source deps.dev (e.g., requests).",
    )

    parser.add_argument(
        "--ecosystem",
        choices=DEPS_DEV_ECOSYSTEMS,
        help="Package ecosystem for --source deps.dev.",
    )

    parser.add_argument(
        "--package-version",
        help=(
            "Package version for --source deps.dev, which counts dependents per "
            "version. Defaults to the version deps.dev marks as default."
        ),
    )

    parser.add_argument(
        "--file-path",
        default="README.md",
        help="The path to the file where the badge will be added. Defaults to README.md.",
    )

    parser.add_argument(
        "--badge-label",
        default="Used by",
        help="The badge display name. Defaults to Used by.",
    )

    parser.add_argument(
        "--badge-color",
        default="informational",
        help="The badge display color. Defaults to informational.",
    )

    parser.add_argument(
        "--badge-logo",
        default="slickpic",
        help="The badge display logo. Defaults to slickpic.",
    )

    parser.add_argument(
        "--update-badge",
        default=False,
        type=str_to_bool,
        help="Add or update badge if set. Defaults to False.",
    )

    parser.add_argument(
        "--max-drop",
        default=50,
        type=percentage,
        help=(
            "Do not update the badge when the count drops by more than this "
            "percentage, which usually means the source returned bad data. "
            "Use 100 to accept any drop. Defaults to 50."
        ),
    )

    return parser


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def get_repo_number(soup):
    counter = soup.find("a", class_="btn-link selected")
    if counter is None:
        raise ValueError(
            "Could not find the dependents count on the GitHub dependents page; "
            "the page layout may have changed."
        )
    repo_text = counter.get_text(strip=True)
    try:
        # GitHub renders large counts with thousands separators, e.g. "4,237,401"
        return int(repo_text.split()[0].replace(",", ""))
    except (ValueError, IndexError):
        # Never turn an unreadable page into a count of 0: that would reset
        # the badge and open a pull request with the wrong number.
        raise ValueError(
            f"Could not read the dependents count from {repo_text!r} on the "
            "GitHub dependents page; the page layout may have changed."
        ) from None


def get_dependents_number(url: str) -> int:
    total_number = 0
    soup = get_soup(url)
    menu_items = soup.find_all("a", class_="select-menu-item")

    if menu_items:  # menu_items is not empty
        for menu_item in menu_items:
            href = menu_item["href"]
            sub_soup = get_soup(url=f"https://github.com{href}")
            total_number += get_repo_number(sub_soup)
    else:
        total_number += get_repo_number(soup)

    return total_number


def generate_badge_url(deps_number, badge_label, badge_color, badge_logo) -> str:
    label = quote(badge_label)
    return f"https://img.shields.io/static/v1?label={label}&message={deps_number}&color={badge_color}&logo={badge_logo}"


def generate_markdown_badge(
    repo_name,
    deps_number,
    badge_label,
    badge_color,
    badge_logo,
    link_url=None,
) -> str:
    link_url = link_url or f"https://github.com/{repo_name}/network/dependents"
    badge_content = f"[![{badge_label}]({generate_badge_url(deps_number, badge_label, badge_color, badge_logo)})]({link_url})"
    return badge_content


def generate_rst_badge(
    repo_name, deps_number, badge_label, badge_color, badge_logo, link_url=None
) -> str:
    link_url = link_url or f"https://github.com/{repo_name}/network/dependents"
    badge_content = (
        f".. image:: {generate_badge_url(deps_number, badge_label, badge_color, badge_logo)}\n"
        f"   :target: {link_url}\n"
        f"   :alt: {badge_label}"
    )
    return badge_content


def get_existing_badge(file_path) -> str:
    file_type = Path(file_path).suffix[1:].lower()
    with open(file_path, encoding="utf-8") as file:
        file_contents = file.read()
    if file_type == "rst":
        matches = re.finditer(
            rf"{RST_COMMENT_MARKER}\n(.*?)\n{RST_COMMENT_MARKER}",
            file_contents,
            re.DOTALL,
        )
    else:
        matches = re.finditer(rf"(.*?){COMMENT_MARKER}", file_contents, re.MULTILINE)
    for match in matches:
        badge = match.group(1)
        if file_type == "rst":
            return badge
        # Keep other badges or text on the same line out of the match so that
        # updating the badge does not delete them.
        md_badge = MD_BADGE_PATTERN.search(badge)
        return md_badge.group() if md_badge else badge
    return ""


def get_badge_count(badge: str):
    """Return the count shown by a badge, or None if it shows none."""
    match = BADGE_COUNT_PATTERN.search(badge)
    return int(match.group(1)) if match else None


def is_suspicious_drop(old_count, new_count, max_drop) -> bool:
    """True when the count fell by more than max_drop percent."""
    if old_count is None or old_count == 0:
        return False
    return (old_count - new_count) * 100 > old_count * max_drop


def update_existing_badge(file_path, existing_badge, new_badge) -> None:
    with open(file_path, encoding="utf-8") as file:
        file_contents = file.read()
    new_file_contents = file_contents.replace(existing_badge, new_badge)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_file_contents)
    print("Updated existing badge.")


# FIXME: add thread comments to pull request.
def add_new_badge(file_path, new_badge) -> None:
    file_type = Path(file_path).suffix[1:].lower()
    with open(file_path, "a", encoding="utf-8") as file:
        if file_type == "rst":
            file.write(f"\n{RST_COMMENT_MARKER}\n{new_badge}\n{RST_COMMENT_MARKER}\n")
        else:
            file.write(f"\n{new_badge} {COMMENT_MARKER}")
    print("Added new badge.")


def print_badge_content(badge_string, flag=False) -> None:
    if flag:
        print("Existing Badge:")
    else:
        print("New Badge:")
    print("=" * 80)
    print(f"{badge_string}")
    print("=" * 80 + "\n")


def check_source_args(parser, args) -> None:
    """Stop with a usage error when the chosen source is missing an option."""
    if args.source == "github":
        if not args.repo:
            parser.error("--repo is required for --source github")
        return
    if not args.package:
        parser.error("--package is required for --source deps.dev")
    if not args.ecosystem:
        parser.error("--ecosystem is required for --source deps.dev")


def get_count(args):
    """Return (count, link) from the source chosen with --source."""
    if args.source == "deps.dev":
        return get_deps_dev_count(args.ecosystem, args.package, args.package_version)
    url = f"https://github.com/{args.repo}/network/dependents"
    return get_dependents_number(url), url


def main():
    parser = get_parser()
    args = parser.parse_args()
    check_source_args(parser, args)

    repo_name = args.repo
    file_path = args.file_path
    file_type = Path(file_path).suffix[1:].lower()  # Remove the dot from the extension
    badge_label = args.badge_label
    badge_color = args.badge_color
    badge_logo = args.badge_logo
    update_badge = args.update_badge

    existing_badge = get_existing_badge(file_path)
    print_badge_content(existing_badge, flag=True)

    deps_number, link_url = get_count(args)

    if "md" == file_type:
        new_badge = generate_markdown_badge(
            repo_name, deps_number, badge_label, badge_color, badge_logo, link_url
        )
    elif "rst" == file_type:
        new_badge = generate_rst_badge(
            repo_name, deps_number, badge_label, badge_color, badge_logo, link_url
        )
    else:
        print(f"Unsupported file type: .{file_type}. Only .md and .rst are supported.")
        return

    print_badge_content(new_badge)
    if new_badge == existing_badge:
        return

    if existing_badge == "":
        add_new_badge(file_path, new_badge)
    elif update_badge:
        old_count = get_badge_count(existing_badge)
        if is_suspicious_drop(old_count, deps_number, args.max_drop):
            # Shown as a warning annotation when running in GitHub Actions.
            print(
                f"::warning::Not updating the badge: the dependents count dropped "
                f"from {old_count} to {deps_number}, more than the allowed "
                f"{args.max_drop}%. If the drop is real, rerun with a higher "
                "--max-drop (max-drop input), or 100 to accept any drop."
            )
            return
        update_existing_badge(file_path, existing_badge, new_badge)


if __name__ == "__main__":
    main()
