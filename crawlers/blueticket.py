import json

import bs4
import requests
from bs4 import BeautifulSoup

from crawlers.parentcrawler import ParentCrawler
from crawlertype import CrawlerType
from event.event import Event
from eventtype import EventType
from utils.utils import Utils

TIMEOUT = 120


class Blueticket(ParentCrawler):

    def __init__(self, event_type):
        super().__init__()
        self.url: str = 'https://www.blueticket.com.br'
        self.params: {} = {
            'cidade': 'Florianópolis',
            'uf': 'SC',
            'categoria': '',
        }
        self.event_type: CrawlerType = event_type
        self.cookies: any = None
        self.headers_connection: {} = None
        self.headers_search: {} = {
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
        self.search_page_soup: bs4.BeautifulSoup = BeautifulSoup()
        self.event_list: [] = list()

    def set_url(self, url: str):
        self.url = url

    def get_url(self) -> str:
        return self.url

    def set_cookies(self, cookies: any):
        self.cookies = cookies

    def get_cookies(self) -> any:
        return self.cookies

    def set_search_page_soup(self, search_page_soup: bs4.BeautifulSoup):
        self.search_page_soup = search_page_soup

    def get_search_page_soup(self) -> bs4.BeautifulSoup:
        return self.search_page_soup

    def set_event_list(self, event_list: []):
        self.event_list = event_list

    def get_event_list(self) -> []:
        return self.event_list

    def get_category_event(self) -> str:
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
        print(f"[{CrawlerType.BLUETICKET.value}] Iniciando conexão...")
        self.set_cookies({
            'theme': 'default',
            'hover-time': '1s',
        })

    def search_page(self):
        print(f"[{CrawlerType.BLUETICKET.value}] Entrando na página de busca...")
        json_data = {}
        self.params['categoria'] = self.get_category_event()
        req = requests.post('https://soulapi.blueticket.com.br/api/v2/events/list', params=self.params,
                            headers=self.headers_search, cookies=self.cookies, json=json_data)
        if req.status_code == 200:
            self.set_url(req.url)
            soup = BeautifulSoup(req.content, 'lxml')
            self.set_search_page_soup(soup)

    def get_events(self) -> []:
        print(f"[{CrawlerType.BLUETICKET.value}] Buscando eventos do tipo {self.event_type.value}...")
        page = self.get_search_page_soup()
        events = json.loads(page.text)
        for event in events:
            event_instance = self.get_event_info(event)
            self.event_list.append(event_instance)
        return self.get_event_list()

    def get_event_info(self, event: any) -> Event:
        event_instance = Event("", "", "", "", "", "", "", "")
        event_instance.set_name(event["nome"])
        event_instance.set_date(Utils().get_regular_date(event["data_exibicao"], CrawlerType.BLUETICKET))
        if event['horario_exibicao'] is None:
            event_instance.set_open_hour(None)
        else:
            if len(event['horario_exibicao'].split()) > 1:
                event_instance.set_open_hour(event['horario_exibicao'].split()[1])
            else:
                event_instance.set_open_hour(None)
                event_instance.set_location(event["local"])
                event_instance.set_event_type(self.event_type.value.capitalize())
                event_instance.set_city(self.params['cidade'])
                event_instance.set_url_event(self.url)
        return event_instance
