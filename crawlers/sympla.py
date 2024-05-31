import json

import requests
from bs4 import BeautifulSoup

from crawlertype import CrawlerType
from event.event import Event
from eventtype import EventType
from parentcrawler import ParentCrawler
from utils.utils import Utils

TIMEOUT = 120


class Sympla(ParentCrawler):

    def __init__(self, event_type):
        super().__init__()
        self.url = 'https://www.sympla.com.br/api/v1/search?category-type=/v4/search'
        self.event_type = event_type
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Content-Type': 'application/json;charset=utf-8',
            'X-KL-kfa-Ajax-Request': 'Ajax_Request',
            'Origin': 'https://www.sympla.com.br',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
            'Priority': 'u=4',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        self.json_data = {
            'service': '/v4/search',
            'params': {
                'only': 'name,start_date,end_date,images,event_type,duration_type,location,id,global_score,start_date_formats,end_date_formats,url,company,type',
                'has_banner': '1',
                'themes': '99',
                'sort': 'location-score',
                'formats': '80',
                'type': 'normal',
                'city': 'Florian%C3%B3polis',
                'location': '-27.5878,-48.54764',
                # 'user_id': '776269',
            }
        }

        self.search_page_soup = None
        self.event_list = list()

    def set_search_page_soup(self, search_page_soup):
        self.search_page_soup = search_page_soup

    def get_search_page_soup(self):
        return self.search_page_soup

    def set_event_list(self, event_list):
        self.event_list = event_list

    def get_event_list(self):
        return self.event_list

    def set_json_data(self, json_data):
        self.json_data = json_data

    def get_json_data(self):
        return self.json_data

    def start_connection(self):
        if self.event_type in [EventType.SHOWS, EventType.BALADA]:
            self.headers['Referer'] = 'https://www.sympla.com.br/eventos/florianopolis-sc/show-musica-festa'

    def search_page(self):
        json_data = self.get_json_data()
        req = requests.post(self.url, headers=self.headers, json=json_data, timeout=TIMEOUT)
        page = BeautifulSoup(req.content, 'lxml')
        self.set_search_page_soup(page)

    def get_events(self):
        page = self.get_search_page_soup()
        data = json.loads(page.text)
        event_instance = Event("", "", "", "", "", "", "", "")
        for event in data["data"]:
            event_instance.set_name(event["name"])
            event_instance.set_date(
                Utils().get_regular_date(event["start_date"], CrawlerType.SYMPLA))
            event_instance.set_open_hour(event["start_date"].split('T')[1].split("+")[0][0:5])
            event_instance.set_location(event["location"]["name"])
            event_instance.set_city(event["location"]["city"])
            event_instance.set_event_type(self.event_type.value)
            event_instance.set_url_event(self.url)
            self.event_list.append(event_instance)
        return self.get_event_list()
