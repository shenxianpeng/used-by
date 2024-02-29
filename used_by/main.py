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


def get_soup(url: str):
    r = requests.get(url=url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def get_dependents_info(url: str) -> list:
    soup = get_soup(url=url)

    # identify there is menu list or not
    menu_list = soup.find_all('a', class_='select-menu-item')

    total_number = total_star = total_fork = 0

    for m_list in menu_list:
        href = m_list['href']
        soup = get_soup(url=f"https://github.com{href}")

        repo_text = soup.find('a', class_='btn-link selected').get_text(strip=True)

        # Extract the number of repositories
        repo_number = int(repo_text.split()[0])

        total_number += repo_number

    return total_number


def main():
    parser = get_parser()
    args = parser.parse_args()

    url = f"https://github.com/{args.repo}/network/dependents"
    
    result = get_dependents_info(url)
    print(result)

if __name__ == "__main__":
    main()
