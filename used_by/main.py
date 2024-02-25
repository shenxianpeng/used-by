import argparse
import requests
from bs4 import BeautifulSoup


def get_parser():
    parser = argparse.ArgumentParser(prog='used-by', description="Generate Used By badge from GitHub dependents information.")

    parser.add_argument(
        '--repo',
        help='GitHub repository name. e.g. cpp-linter/cpp-linter-action'
    )

    return parser


def get_dependents_info(url: str) -> list:
    r = requests.get(url=url)
    soup = BeautifulSoup(r.content, "html.parser")

    # identify there is menu list or not
    menu_list = soup.find_all('a', class_='select-menu-item')

    total_number = 0    # total used by project number
    total_star = 0      # total used by project star number
    total_fork = 0      # total used by project fork number

    for m_list in menu_list:
        href = m_list['href']

        r = requests.get(url=f"https://github.com{href}")
        soup = BeautifulSoup(r.content, "html.parser")

        page_data = [
            "{}/{}".format(
                t.find('a', {"data-repository-hovercards-enabled":""}).text,
                t.find('a', {"data-hovercard-type":"repository"}).text
            )
            for t in soup.findAll("div", {"class": "Box-row"})
        ]

        total_number += len(page_data)

        span_tags = soup.find_all('span', class_='color-fg-muted text-bold pl-3')

        for span_tag in span_tags:
            svg_star_tag = span_tag.find('svg', class_='octicon octicon-star')
            svg_fork_tag = span_tag.find('svg', class_='octicon octicon-repo-forked')
            if svg_star_tag:
                total_star += int(span_tag.text.strip().replace(',', ''))
            if svg_fork_tag:
                total_fork += int(span_tag.text.strip().replace(',', ''))

    print(f"total_number is {total_number}")
    print(f"total_star is {total_star}")
    print(f"total_fork is {total_fork}")


def main():
    parser = get_parser()
    args = parser.parse_args()

    url = f"https://github.com/{args.repo}/network/dependents"
    
    get_dependents_info(url)

if __name__ == "__main__":
    main()
