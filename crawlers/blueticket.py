import json

import requests
from bs4 import BeautifulSoup

from crawlers.parentcrawler import ParentCrawler
from event.event import Event
from eventtype import EventType
from utils.utils import Utils

TIMEOUT = 120


class Blueticket(ParentCrawler):

    def __init__(self):
        super().__init__()
        self.url = 'https://www.blueticket.com.br'
        self.params = {
            'cidade': 'Florianópolis',
            'uf': 'SC',
            'categoria': '',
        }
        self.cookies = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'TERMINAL': '27b9665e',
            'Content-Type': 'application/json;charset=utf-8',
            'PDV': '100',
            'POS': '100',
            'Origin': self.url,
            'Connection': 'keep-alive',
            'Referer': self.url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        self.event_type = EventType.SHOWS
        self.page_soup = None
        self.event_list = list()

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_cookies(self, cookies):
        self.cookies = cookies

    def get_cookies(self):
        return self.cookies

    def set_page_soup(self, page_soup):
        self.page_soup = page_soup

    def get_page_soup(self):
        return self.page_soup

    def get_category_event(self):
        if self.event_type == EventType.SHOWS:
            return '11'
        if self.event_type == EventType.TEATRO:
            return '12'
        if self.event_type == EventType.INFANTIL:
            return '14'
        if self.event_type == EventType.BALADA:
            return '1'
        if self.event_type == EventType.CURSO:
            return '20'
        if self.event_type == EventType.CONGRESSOS:
            return '21'
        if self.event_type == EventType.ESPORTIVO:
            return '4'

    def start_connection(self):
        self.set_cookies({
            'theme': 'default',
            'hover-time': '1s',
        })

    def search_page(self):
        json_data = {}
        self.params['categoria'] = self.get_category_event()
        req = requests.post('https://soulapi.blueticket.com.br/api/v2/events/list', params=self.params,
                            headers=self.headers, cookies=self.cookies, json=json_data)
        if req.status_code == 200:
            self.set_url(req.url)
            soup = BeautifulSoup(req.content, 'lxml')
            self.set_page_soup(soup)

    def get_events(self):
        page = self.get_page_soup()
        events = json.loads(page.text)
        event_instance = Event("", "", "", "", "", "", "", "")
        for event in events:
            event_instance.set_name(event["nome"])
            event_instance.set_date(Utils().convert_date_blueticket(event["data_exibicao"]))
            if event['horario_exibicao'] is None:
                event_instance.set_open_hour(None)
            else:
                if len(event['horario_exibicao'].split()) > 1:
                    event_instance.set_open_hour(event['horario_exibicao'].split()[1])
                else:
                    event_instance.set_open_hour(None)
            event_instance.set_location(event["local"])
            event_instance.set_event_type(self.event_type.value)
            event_instance.set_url_event(self.url)
            self.event_list.append(event_instance)
