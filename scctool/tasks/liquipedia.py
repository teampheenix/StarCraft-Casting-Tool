"""Data grabber for Liquipedia."""
import logging
import re
import urllib.parse
import time

import requests
from bs4 import BeautifulSoup

import scctool.settings.translation
from scctool import __version__ as scct_version

# create logger
module_logger = logging.getLogger(__name__)
_ = scctool.settings.translation.gettext


class LiquipediaGrabber:
    """Grab data from Liquipedia."""

    _base_url = 'https://liquipedia.net'

    def __init__(self):
        """Init the grabber."""
        scct_url = "https://teampheenix.github.io/StarCraft-Casting-Tool/"
        self._session = requests.Session()
        self._session.trust_env = False
        self._headers = dict()
        self._headers["User-Agent"] = "StarCraftCastingTool v{} ({})".format(
            scct_version, scct_url)
        self._headers["Accept-Encoding"] = "gzip"

    def image_search(self, search_str):
        """Search for an image."""
        params = {'title': 'Special:Search',
                  'profile': 'advanced', 'fulltext': 'Search', 'ns6': 1}
        params['search'] = str(search_str).strip()
        source = '{}/commons/index.php?{}'.format(
            self._base_url, urllib.parse.urlencode(params))

        urllib.parse.urlencode(params)
        r = self._session.get(source)

        soup = BeautifulSoup(r.content, 'html.parser')
        r = re.compile(
            r'\((\d+,?\d*)\s+×\s+(\d+,?\d*)\s\((\d+)\s+([KM]*B)\)\)')
        try:
            for result in soup.find("ul",
                                    class_="mw-search-results").find_all("li"):
                try:
                    link = result.find("a", class_="image")
                    href = link['href']
                    thumb = link.find("img")['src']
                    data = result.find(
                        "div", class_="mw-search-result-data").contents[0]
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
        """Get all image sizes available for an image."""
        r = self._session.get(self._base_url + image)
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
        """Get all image sizes available for an image by using the API."""
        pass

    def get_map(self, map_name, retry=False):
        """Search for an map."""
        params = dict()
        params['action'] = "opensearch"
        if retry:
            time.sleep(1)
            params['search'] = str(map_name).strip() + ' LE'
        else:
            params['search'] = str(map_name).strip()
        module_logger.info(f'Try to find map {params["search"]}')
        params['limit'] = 1
        params['namespace'] = 0

        url = f'{self._base_url}/starcraft2/api.php'
        r = self._session.get(
            url, headers=self._headers, params=params)
        try:
            r.raise_for_status()
            data = r.json()
        except Exception:
            raise MapNotFound

        try:
            liquipedia_map = data[1][0]
        except IndexError:
            if not retry:
                return self.get_map(map_name, retry=True)
            else:
                raise MapNotFound
        if map:
            params = dict()
            params['action'] = "parse"
            params['format'] = "json"
            params['page'] = liquipedia_map.replace(' ', '_')

            url = f'{self._base_url}/starcraft2/api.php'

            data = self._session.get(url, headers=self._headers,
                                     params=params).json()
            content = data['parse']['text']['*']
            soup = BeautifulSoup(content, 'html.parser')
            liquipedia_map = LiquipediaMap(soup)
            redirect = liquipedia_map.redirect()
            if liquipedia_map.is_map():
                return liquipedia_map
            elif redirect:
                return self.get_map(redirect, retry=False)
            elif not retry:
                return self.get_map(map_name, retry=True)
            else:
                raise MapNotFound
        elif not retry:
            return self.get_map(map_name, retry=True)
        else:
            raise MapNotFound

    def get_ladder_mappool(self, players_per_team=1):
        """Get the current 1v1 ladder mappool."""
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
        for result in soup.find_all("th", class_="navbox-group"):
            if result.contents[0].strip() == f"{players_per_team} vs {players_per_team}":
                for mymap in result.findNext("td").find_all('a'):
                    yield mymap.contents[0].replace("LE", '').strip()
                break

    def get_map_stats(self, maps):
        """Get map statistics of specified maps."""
        params = dict()
        params['action'] = "parse"
        params['format'] = "json"
        params['prop'] = "text"
        params['contentmodel'] = "wikitext"
        params['utf8'] = 1
        params['text'] = "{{Tournament statistics/intro}}"

        if len(maps) < 1:
            return

        for sc2map in maps:
            params['text'] = (
                params['text']
                + "{{Map statistics row|tournament=+|map="
                + sc2map.strip() + "}}")
        params['text'] = params['text'] + "</div>"
        url = f'{self._base_url}/starcraft2/api.php'
        data = requests.get(url, headers=self._headers, params=params).json()
        content = data['parse']['text']['*']
        soup = BeautifulSoup(content, 'html.parser')
        for map_stats in soup.find_all("tr", class_="stats-map-row"):
            data = dict()
            data['map'] = map_stats.find(
                'td', class_='stats-map-name').find('a').text.replace(
                    'LE', '').strip()
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
    """StarCraft 2 map present on Liquipedia."""

    def __init__(self, soup):
        """Init the map with BeautifulSoup."""
        self._soup = soup

    def is_map(self):
        """Test if this is an actual map."""
        return self._soup.find(
            href='/starcraft2/Template:Infobox_map') is not None

    def redirect(self):
        redirect = self._soup.find("div", class_="redirectMsg")
        if redirect:
            link = redirect.find(
                'a', attrs={'href': re.compile("^/starcraft2/")}).get('href')
            return link.replace('/starcraft2/', '')
        else:
            return ''

    def get_name(self):
        """Get the name of the map."""
        infobox = self._soup.find("div", class_="fo-nttax-infobox")
        map_name = infobox.find("div", class_="infobox-header").text
        map_name = map_name.replace("[e]", "")
        map_name = map_name.replace("[h]", "")
        map_name = map_name.replace("LE", "")
        map_name = map_name.replace("GSL", "")
        return map_name.strip()

    def get_info(self):
        """Get info about map."""
        key = ""
        data = dict()
        infobox = self._soup.find("div", class_="fo-nttax-infobox")
        for cell in infobox.find_all("div", class_="infobox-cell-2"):
            if 'infobox-description' in cell.get("class"):
                key = cell.getText().replace(":", "")
            else:
                if key:
                    try:
                        key = key.lower().replace(" ", "-")
                        data[key] = cell.getText()
                        key = ""
                    except Exception:
                        pass
                else:
                    raise ValueError('Key is missing in Infobox')
        return data

    def get_map_images(self):
        """Get map images."""
        return self._soup.find('a', class_='image')['href']

    def get_stats(self):
        """Get map statistics."""
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
    """Map not found on Liquipedia exception."""

    pass
