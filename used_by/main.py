import argparse
import requests
from urllib.parse import quote
from bs4 import BeautifulSoup


def get_parser():
    parser = argparse.ArgumentParser(
        prog="used-by",
        description="Generate Used By badge from GitHub dependents information.",
    )

    parser.add_argument(
        "--repo", help="GitHub repository name. e.g. cpp-linter/cpp-linter-action"
    )

    parser.add_argument(
        "--doc-type",
        default="md",
        help="Supports md(Markdown) and rst(reStructuredText). Defaults to `md`.",
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


def gen_md_badge(
    repo_name, deps_number, label="Used by", color="informational", logo="slickpic"
) -> str:
    md_text = f"""<!--used-by-badge-start-->
[![](https://img.shields.io/static/v1?label={quote(label)}&message={deps_number}&color={color}&logo={logo})](https://github.com/{repo_name}/network/dependents)
<!--used-by-badge-end-->"""
    return md_text


def gen_rst_badge(
    repo_name, deps_number, label="Used by", color="informational", logo="slickpic"
) -> str:
    rst_text = f""".. image:: https://img.shields.io/static/v1?label={quote(label)}&message={deps_number}&color={color}&logo={logo}
    :target: https://github.com/{repo_name}/network/dependents
    :alt: used-by"""
    return rst_text


def main():
    parser = get_parser()
    args = parser.parse_args()
    repo_name = args.repo
    doc_type = args.doc_type.lower()

    url = f"https://github.com/{repo_name}/network/dependents"
    deps_number = get_dependents_number(url)

    if "md" in doc_type:
        print(gen_md_badge(repo_name, deps_number))
    elif "rst" in doc_type:
        print(gen_rst_badge(repo_name, deps_number))
    else:
        raise NotImplementedError(f"Not support {doc_type}.")


if __name__ == "__main__":
    main()
