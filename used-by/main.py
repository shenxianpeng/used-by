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

        print(page_data)
        print(len(page_data))
        paginationContainer = soup.find("div", {"class":"paginate-container"}).find('a')
        if paginationContainer:
            url = paginationContainer["href"]
        else:
            return


def main():
    parser = get_parser()
    args = parser.parse_args()

    url = f"https://github.com/{args.repo}/network/dependents"
    
    get_dependents_info(url)

if __name__ == "__main__":
    main()
