import requests
from bs4 import BeautifulSoup

from enumerator.cralwertype import CrawlerType

TIMEOUT = 300


class Utils:

    def __init__(self):
        self.attr = None

    def get_regular_element_pensa_no_evento(self, attr: any) -> str:
        parsed_element = attr.find('b').parent.text.strip().split(':')[1]
        return parsed_element

    def get_open_hour_pensa_no_evento(self, attr: any):
        hour = attr.find('b').parent.contents[3]
        return hour

    def get_location_element_pensa_no_evento(self, attr: any) -> str:
        href_location = attr.find('b').parent.find('a').attrs['href']
        request_location = requests.get(url=href_location, timeout=TIMEOUT)
        soup_request_location = BeautifulSoup(request_location.content, "lxml")
        location = soup_request_location.title.text.strip().split('-')[0]
        return location

    def get_city_element_pensa_no_evento(self, attr: any) -> str:
        href_location = attr.find('b').parent.find('a').attrs['href']
        request_location = requests.get(url=href_location, timeout=TIMEOUT)
        soup_request_location = BeautifulSoup(request_location.content, "lxml")
        div_city = soup_request_location.find('div', attrs={'class': 'col-12 mb-3 text-left'})
        if div_city is None:
            return
        else:
            city = div_city.find('b').parent.text.split('?')[1].split('\n')[0].split('-')[1].split('-')[0].split('/')[0]
            return city

    def get_event_type_by_url(self, url: str, brand_name: CrawlerType):
        if brand_name == CrawlerType.PENSA_NO_EVENTO:
            partes_url = url.split("/")
            if len(partes_url) >= 4:
                return partes_url[3]
            else:
                return ""
