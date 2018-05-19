"""Data grabber for Liquipedia."""
import logging
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

from scctool import __version__ as scct_version

# create logger
module_logger = logging.getLogger('scctool.tasks.liquipedia')


class LiquipediaGrabber:

    _base_url = 'https://liquipedia.net'

    def __init__(self):
        scct_url = "https://teampheenix.github.io/StarCraft-Casting-Tool/"
        self._headers = dict()
        self._headers["User-Agent"] = "StarCraftCastingTool v{} ({})".format(
            scct_version, scct_url)

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

    def get_images_new(self, image):
        print(image)

    def get_map(self, map_name):
        params = dict()
        params['action'] = "opensearch"
        params['search'] = str(map_name).strip()
        params['limit'] = 1
        params['namespace'] = 0

        url = '{}/starcraft2/api.php'.format(self._base_url)
        data = requests.get(url, headers=self._headers, params=params).json()
        map = data[1][0]
        if map:
            params = dict()
            params['action'] = "parse"
            params['format'] = "json"
            params['page'] = map

            url = '{}/starcraft2/api.php'.format(self._base_url)

            data = requests.get(url, headers=self._headers,
                                params=params).json()
            content = data['parse']['text']['*']
            soup = BeautifulSoup(content, 'html.parser')
            map = LiquipediaMap(soup)
            if not map.is_map():
                raise MapNotFound
            else:
                return map
        else:
            raise MapNotFound

    def get_ladder_mappool(self):
        params = dict()
        params['action'] = "parse"
        params['format'] = "json"
        params['prop'] = "text"
        params['contentmodel'] = "wikitext"
        params['utf8'] = 1
        params['text'] = "{{MapNavbox}}"

        url = '{}/starcraft2/api.php'.format(self._base_url)

        data = requests.get(url, headers=self._headers, params=params).json()
        content = data['parse']['text']['*']
        soup = BeautifulSoup(content, 'html.parser')
        for result in soup.find_all("td", class_="navbox-group"):
            if result.contents[0].strip() == "1 vs 1":
                for map in result.findNext("td").find_all('a'):
                    yield map.contents[0].replace("LE", '').strip()
                break

    def get_map_stats(self, maps):
        params = dict()
        params['action'] = "parse"
        params['format'] = "json"
        params['prop'] = "text"
        params['contentmodel'] = "wikitext"
        params['utf8'] = 1
        params['text'] = ""

        if len(maps) < 1:
            return

        for map in maps:
            params['text'] = params['text'] + \
                "{{Map statistics|map=" + map.strip() + "}}"

        url = '{}/starcraft2/api.php'.format(self._base_url)
        data = requests.get(url, headers=self._headers, params=params).json()
        content = data['parse']['text']['*']
        soup = BeautifulSoup(content, 'html.parser')
        for map_stats in soup.find_all("tr", class_="stats-map-row"):
            data = dict()
            data['map'] = map_stats.find(
                'td', class_='stats-map-name').find('a').text.strip()
            data['games'] = map_stats.find(
                "td", class_="stats-map-number").text.strip()
            data['tvz'] = map_stats.find(
                "td", class_="stats-tvz-4").text.strip()
            data['zvp'] = map_stats.find(
                "td", class_="stats-zvp-4").text.strip()
            data['pvt'] = map_stats.find(
                "td", class_="stats-pvt-4").text.strip()
            yield data


class LiquipediaMap:

    def __init__(self, soup):
        self._soup = soup

    def is_map(self):
        return self._soup.find(href='/starcraft2/Template:Infobox_map') is not None

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
                    try:
                        key = key.lower().replace(" ", "-")
                        data[key] = cell.contents[0].strip()
                        key = ""
                    except Exception:
                        pass
                else:
                    raise ValueError('Key is missing in Infobox')
        return data

    def get_map_images(self):
        return self._soup.find('a', class_='image')['href']

    def get_stats(self):
        data = dict()
        try:
            data['games'] = self._soup.find(
                "td", class_="stats-map-number").text.strip()
            data['tvz'] = self._soup.find(
                "td", class_="stats-tvz-4").text.strip()
            data['zvp'] = self._soup.find(
                "td", class_="stats-zvp-4").text.strip()
            data['pvt'] = self._soup.find(
                "td", class_="stats-pvt-4").text.strip()
        except AttributeError:
            return dict()
        return data


class MapNotFound(Exception):
    pass
