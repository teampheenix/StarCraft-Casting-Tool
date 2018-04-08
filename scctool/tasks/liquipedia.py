"""Data grabber for Liquipedia."""
import logging
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

# create logger
module_logger = logging.getLogger('scctool.tasks.liquipedia')


class LiquipediaGrabber:

    _base_url = 'http://liquipedia.net'

    def __init__(self):
        pass

    def image_search(self, search_str):
        params = {'title': 'Special:Search',
                  'profile': 'advanced', 'fulltext': 'Search', 'ns6': 1}
        params['search'] = str(search_str).strip()
        source = '{}/commons/index.php?{}'.format(
            self._base_url, urllib.parse.urlencode(params))

        urllib.parse.urlencode(params)
        r = requests.get(source)

        soup = BeautifulSoup(r.content, 'html.parser')
        try:
            for result in soup.find("ul", class_="mw-search-results").find_all("li"):
                try:
                    link = result.find("a", class_="image")
                    href = link['href']
                    thumb = link.find("img")['src']
                    data = result.find(
                        "div", class_="mw-search-result-data").contents[0]
                    r = re.compile(
                        r'\((\d+,?\d*)\s+×\s+(\d+,?\d*)\s\((\d+)\s+([KM]*B)\)\)')
                    data = r.match(data)
                    pixel = int(data.group(1).replace(",", "")) * \
                        int(data.group(2).replace(",", ""))
                    if(pixel > 10000):
                        yield href, thumb
                except Exception:
                    continue
        except Exception:
            pass

    def get_images(self, image):
        r = requests.get(self._base_url + image)
        regex = re.compile(r'(\d+,?\d*)\s+×\s+(\d+,?\d*)')
        soup = BeautifulSoup(r.content, 'html.parser')
        images = dict()
        for item in soup.select('div[class*="mw-filepage-"]'):
            for link in item.findAll("a"):
                data = regex.match(link.contents[0])
                pixel = int(data.group(1).replace(",", "")) * \
                    int(data.group(2).replace(",", ""))
                images[pixel] = link['href']
        if len(images) == 0:
            link = soup.find("div", class_="fullMedia").find("a")
            data = regex.match(link.contents[0])
            try:
                pixel = int(data.group(1).replace(",", "")) * \
                    int(data.group(2).replace(",", ""))
            except Exception:
                pixel = 0
            images[pixel] = link['href']

        return images

    def get_map(self, map_name):
        # "http://liquipedia.net/starcraft2/index.php?search=Blackpink"
        params = {}
        params['search'] = str(map_name).strip()
        source = '{}/starcraft2/index.php?{}'.format(
            self._base_url, urllib.parse.urlencode(params))

        urllib.parse.urlencode(params)
        r = requests.get(source)
        soup = BeautifulSoup(r.content, 'html.parser')

        map = LiquipediaMap(soup)
        if not map.is_map():
            raise MapNotFound
        else:
            return map


class LiquipediaMap:

    def __init__(self, soup):
        self._soup = soup

    def is_map(self):
        for cat in self._soup.find("div", id="catlinks").find_all("a"):
            if cat['title'] == "Category:Maps":
                return True
        return False

    def get_name(self):
        infobox = self._soup.find("div", class_="fo-nttax-infobox")
        map = infobox.find("div", class_="infobox-header").text
        map = map.replace("[e]", "")
        map = map.replace("[h]", "")
        map = map.replace("LE", "")
        return map.strip()

    def get_info(self):
        key = ""
        data = dict()
        infobox = self._soup.find("div", class_="fo-nttax-infobox")
        for cell in infobox.find_all("div", class_="infobox-cell-2"):
            if 'infobox-description' in cell.get("class"):
                key = cell.contents[0].strip().replace(":", "")
            else:
                if key:
                    data[key] = cell.contents[0].strip()
                    key = ""
                else:
                    raise ValueError('Key is missing in Infobox')
        return data

    def get_stats(self):
        data = dict()
        try:
            data['Games'] = self._soup.find(
                "td", class_="stats-map-number").text.strip()
            data['TvZ'] = self._soup.find(
                "td", class_="stats-tvz-4").text.strip()
            data['ZvP'] = self._soup.find(
                "td", class_="stats-zvp-4").text.strip()
            data['PvT'] = self._soup.find(
                "td", class_="stats-pvt-4").text.strip()
        except AttributeError:
            return dict()
        return data

    def get_map_images(self):
        return self._soup.find('a', class_='image')['href']


class MapNotFound(Exception):
    pass
