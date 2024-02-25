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


def has_next_page(soup) -> bool:
    '''identify if there is next button'''
    paginate_container = soup.find("div", {"class": "paginate-container"}).find('a', text='Next')
    if paginate_container:
       return True
    else:
        return False


def get_page_number(soup):
    page_data = [
        "{}/{}".format(
            t.find('a', {"data-repository-hovercards-enabled":""}).text,
            t.find('a', {"data-hovercard-type":"repository"}).text
        )
        for t in soup.findAll("div", {"class": "Box-row"})
    ]

    return len(page_data)


def get_star_number(soup):
    span_tags = soup.find_all('span', class_='color-fg-muted text-bold pl-3')
    total_star = 0 
    for span_tag in span_tags:
        svg_star_tag = span_tag.find('svg', class_='octicon octicon-star')
        if svg_star_tag:
            total_star += int(span_tag.text.strip().replace(',', ''))

    return total_star


def get_fork_number(soup):
    span_tags = soup.find_all('span', class_='color-fg-muted text-bold pl-3')
    total_fork = 0 
    for span_tag in span_tags:
        svg_fork_tag = span_tag.find('svg', class_='octicon octicon-repo-forked')
        if svg_fork_tag:
            total_fork += int(span_tag.text.strip().replace(',', ''))

    return total_fork


def process_pagination(soup):
    '''get and return next page soup information.'''
    paginate_container = soup.find("div", {"class": "paginate-container"}).find('a', text='Next')
    if paginate_container:
        href = paginate_container["href"]
        print(href) # next page url
        return get_soup(url=href)
    return None


def get_dependents_info(url: str) -> list:
    soup = get_soup(url=url)

    # identify there is menu list or not
    menu_list = soup.find_all('a', class_='select-menu-item')

    total_number = total_star = total_fork = 0

    for m_list in menu_list:
        href = m_list['href']
        soup = get_soup(url=f"https://github.com{href}")
        
        total_number += get_page_number(soup)
        total_star += get_star_number(soup)
        total_fork += get_fork_number(soup)

        while has_next_page(soup):
            soup = process_pagination(soup)
            total_number += get_page_number(soup)
            total_star += get_star_number(soup)
            total_fork += get_fork_number(soup)

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
