import argparse
import requests
import re
from urllib.parse import quote
from bs4 import BeautifulSoup
from pathlib import Path
from used_by import COMMENT_MARKER


def get_parser():
    parser = argparse.ArgumentParser(
        prog="used-by",
        description="Generate Used By badge from GitHub dependents information.",
    )

    parser.add_argument(
        "--repo", help="GitHub repository name. e.g. cpp-linter/cpp-linter-action"
    )

    parser.add_argument(
        "--file-path",
        default="README.md",
        help="The path to file. Defaults to `README.md`.",
    )

    parser.add_argument(
        "--badge-label",
        default="Used by",
        help="The badge display name. Defaults to `Used by`.",
    )

    parser.add_argument(
        "--badge-color",
        default="informational",
        help="The badge display color. Defaults to `informational`.",
    )

    parser.add_argument(
        "--badge-logo",
        default="slickpic",
        help="The badge display color. Defaults to `slickpic`.",
    )

    parser.add_argument(
        "--update-badge",
        default=False,
        help="Add or update badge if it is True. Defaults to `False`.",
    )

    return parser


def get_soup(url: str) -> BeautifulSoup:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup


def get_dependents_number(url: str) -> int:
    soup = get_soup(url)
    menu_items = soup.find_all("a", class_="select-menu-item")

    total_number = 0

    for menu_item in menu_items:
        href = menu_item["href"]
        sub_soup = get_soup(url=f"https://github.com{href}")
        repo_text = sub_soup.find("a", class_="btn-link selected").get_text(strip=True)
        repo_number = int(repo_text.split()[0])
        total_number += repo_number

    return total_number


def gen_badge_content(
    repo_name,
    deps_number,
    file_type,
    label="Used by",
    color="informational",
    logo="slickpic",
) -> str:
    if "md" in file_type:
        badge_content = f"[![used-by](https://img.shields.io/static/v1?label={quote(label)}&message={deps_number}&color={color}&logo={logo})](https://github.com/{repo_name}/network/dependents)"
    elif "rst" in file_type:
        badge_content = f"""
.. image:: https://img.shields.io/static/v1?label={quote(label)}&message={deps_number}&color={color}&logo={logo}
 :target: https://github.com/{repo_name}/network/dependents
 :alt: used-by"""
    else:
        raise NotImplementedError(f"Not support {file_type}.")
    return badge_content


def get_existing_badge(file_path) -> str:
    with open(file_path) as file:
        file_contents = file.read()
        if COMMENT_MARKER not in file_contents:
            return ""
        pattern = rf"{COMMENT_MARKER}(.*?){COMMENT_MARKER}"
        matches = re.findall(pattern, file_contents, re.DOTALL)
        if matches:
            existing_badge = matches[0].strip()

    return existing_badge


def update_existing_badge(file_path, existing_badge, new_badge) -> None:
    with open(file_path) as file:
        file_contents = file.read()

    new_file_contents = file_contents.replace(existing_badge, new_badge)

    with open(file_path, "w") as file:
        file.write(new_file_contents)
    print("updated existing badge.")


# FIXME: add thread comments to pull request.
def post_thread_badge(new_badge) -> None:
    print(COMMENT_MARKER + "\n" + new_badge + "\n" + COMMENT_MARKER)


def main():
    parser = get_parser()
    args = parser.parse_args()
    repo_name = args.repo
    file_path = args.file_path
    file_type = Path(file_path).suffix[1:].lower()  # Remove the dot from the extension
    badge_label = args.badge_label
    badge_color = args.badge_color
    badge_logo = args.badge_logo
    update_badge = args.update_badge

    url = f"https://github.com/{repo_name}/network/dependents"
    deps_number = get_dependents_number(url)

    existing_badge = get_existing_badge(file_path)
    print(f"existing_badge is {existing_badge}")
    new_badge = gen_badge_content(
        repo_name,
        deps_number,
        file_type,
        label=badge_label,
        color=badge_color,
        logo=badge_logo,
    )
    print(f"new_badge is {new_badge}")
    if new_badge == existing_badge:
        return
    if update_badge:
        update_existing_badge(file_path, existing_badge, new_badge)
    if existing_badge == "":
        post_thread_badge(new_badge)


if __name__ == "__main__":
    main()
