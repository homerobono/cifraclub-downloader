import argparse
import re
import requests
from bs4 import BeautifulSoup
from os import path

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('html', nargs='?')
html = arg_parser.parse_args().html

def clear_unnecessary_tags(soup):
    garbage = []
    garbage += soup.find_all('script')
    garbage.append(soup.find('div', id="side-menu"))
    garbage.append(soup.find('div', id="c-troca"))
    garbage.append(soup.find('div', id="c-capo"))
    garbage.append(soup.find('div', id="c-tom"))

    for el in garbage:
        try:
            el.extract()
        except AttributeError:
            pass

def fix_css_link(soup):
    link = soup.find('link', rel="stylesheet")
    url = link['href']
    filename = re.match('.*\/([^/]*\.css)', url).group(1)
    link['href'] = f'../../../css/{filename}'

    if re.match(r'^(http|//)', url) and not path.exists(f'css/{filename}'):
        url = re.sub(r'^//', r'http://', url)
        print("Downloading css")
        css_data = requests.get(url)
        with open(f'css/{filename}', 'wb') as css_file:
            css_file.write(css_data.content)

def fix_cifraclub_logo(soup):
    link = soup.find('img', class_="logo")
    url = link['src']
    match = re.match('.*\/(([^/]*\.svg).*)', url)
    fileurl = match.group(1)
    filename = match.group(2)
    link['src'] = f'../../../img/{fileurl}'

    if re.match(r'^(http|//)', url) and not path.exists(f'img/{filename}'):
        url = re.sub(r'^//', r'http://', url)
        print("Downloading logo")
        logo_data = requests.get(url)
        with open(f'img/{filename}', 'wb') as logo_file:
            logo_file.write(logo_data.content)

def remove_page_size(soup):
    pass
    # TODO
    #soup.find('*', class_='tam_a4')....


if __name__ == '__main__':
    with open(html) as html_file:
        raw_html = html_file.read()
    soup = BeautifulSoup(raw_html, features="html.parser")
    
    clear_unnecessary_tags(soup)
    fix_css_link(soup)
    fix_cifraclub_logo(soup)
    remove_page_size(soup)

    with open(html, 'w') as html_file:
        html_file.write(soup.prettify())

