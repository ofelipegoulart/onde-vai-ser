import json

import bs4
import requests
from bs4 import BeautifulSoup

from crawlers.parentcrawler import ParentCrawler
from crawlertype import CrawlerType
from event.event import Event
from eventtype import EventType

TIMEOUT = 120


class Sympla(ParentCrawler):

    def __init__(self, event_type, page_counter):
        super().__init__()
        self.url: str = 'https://www.sympla.com.br/api/v1/'
        self.event_type: EventType = event_type
        self.headers: {} = {
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
        self.cookies = None
        self.json_data = None
        self.search_page_soup = None
        self.page_counter: int = page_counter
        self.event_list = list()

    def set_search_page_soup(self, search_page_soup: bs4.BeautifulSoup):
        self.search_page_soup = search_page_soup

    def get_search_page_soup(self) -> bs4.BeautifulSoup:
        return self.search_page_soup

    def set_event_list(self, event_list: []):
        self.event_list = event_list

    def get_event_list(self) -> []:
        return self.event_list

    def start_connection(self):
        print(f"[{CrawlerType.SYMPLA.value}] Iniciando conexão...")
        cookies_req = requests.get('https://www.sympla.com.br/', timeout=120)
        self.cookies = cookies_req.cookies
        base_url = 'https://www.sympla.com.br/api/v1/matrixComponent?uuid=todos-eventos&matrix_uuid='
        url = ''
        match self.event_type.name:
            case 'BALADA' | 'SHOWS':
                url = base_url + 'collection-festas-e-shows'
            case 'TEATRO':
                url = base_url + 'collection-teatros-e-espetaculos'
            case 'STANDUP':
                url = base_url + 'collection-stand-up'
            case 'CONGRESSOS':
                url = base_url + 'collection-congressos-e-palestras'
            case 'INFANTIL':
                url = base_url + 'collection-infantil'
            case 'CURSO':
                url = base_url + 'collection-cursos-e-workshops'
            case 'ESPORTIVO':
                url = base_url + 'collection-esportes'
            case 'GASTRONOMIA':
                url = base_url + 'collection-gastronomia'
            case 'TODOS':
                url = 'https://www.sympla.com.br/api/v1/matrixComponent?uuid=todos-eventos'
            case _:
                print("Error")
        if self.event_type.name != "TODOS":
            req = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=TIMEOUT)
            response = req.json()
            response['component']['service_params']['city'] = 'Florian%C3%B3polis'
            response['component']['service_params']['sort'] = 'location-sort'
            response['component']['service_params']['page'] = self.page_counter
            self.json_data = {'service': '/v4/mapsearch', 'params': response['component']['service_params']}
        else:
            self.json_data = {"service": "/v4/mapsearch",
                              "params": {"collections": "", "range": "", "need_pay": "", "include_organizers": 1,
                                         "only": "name,start_date,end_date,images,event_type,duration_type,location,id,global_score,start_date_formats,end_date_formats,url,company,type,organizer,event",
                                         "components_limit": "2", "components_page": "1",
                                         "include_response": "true", "limit": "24",
                                         "location": "-27.5878,-48.54764", "page": self.page_counter,
                                         "sort": "location-score", "start_date": "", "end_date": "",
                                         "state": "SC", "city": ""}}

    def search_page(self):
        print(f"[{CrawlerType.SYMPLA.value}] Entrando na página de busca...")
        req = requests.post(self.url + 'search', json=self.json_data, timeout=TIMEOUT)
        page = BeautifulSoup(req.content, 'lxml')
        self.set_search_page_soup(page)
        self.url = req.url

    def get_events(self):
        print(f"[{CrawlerType.SYMPLA.value}] Buscando eventos do tipo {self.event_type.value.upper()}...")
        page = self.get_search_page_soup()
        data = json.loads(page.text)['result']['events']['data']
        for evento in data:
            event_instance = Event("", self.event_type, "", "", "", "", "", self.url)
            if evento['location']['city'] in ['Florianópolis', 'São José']:
                event_instance.set_name(evento['name'])
                event_instance.set_date(evento['start_date'])
                event_instance.set_open_hour(evento['start_date'])
                event_instance.set_location(evento['location']['name'])
                event_instance.set_city(evento['location']['city'])
                if self.event_type is not EventType.TODOS:
                    event_instance.set_event_type(self.event_type.value.capitalize())
                else:
                    event_instance.set_event_type(self.event_type.value.capitalize())
                    # event_instance.set_event_type(self.get_event_type_on_api(evento['name']))
                self.event_list.append(event_instance)
        return self.get_event_list()

    # def get_event_type_on_api(self, name):
    #     for event in SymplaEventType:
    #         if event.name != "GASTRONOMIA":
    #             collections = event.value
    #             json_data = {"service": "/v4/search/term",
    #                          "params": {"collections": collections, "location": "-27.5878,-48.54764", "page": "1",
    #                                     "q": unidecode(name)}}
    #             req = requests.post('https://www.sympla.com.br/api/v1/search', json=json_data, timeout=TIMEOUT)
    #             response = req.json()['total']
    #
    #             if response == 1:
    #                 return self.get_default_eventtype(event)
    #
    #     return self.get_event_type_on_api(name)
    #
    # def get_default_eventtype(self, event_type):
    #     for enum in EventType:
    #         if enum.name == event_type.name:
    #             return enum
    #         else:
    #             TypeError("Não encontrado")

    def check_if_more_events(self):
        self.page_counter += 1
        page = self.get_search_page_soup()
        total = json.loads(page.text)['result']['events']['total']
        data = json.loads(page.text)['result']['events']['data']
        self.page_counter -= 1
        if total > 1 and 'Florianópolis' in str(data):
            return True
        else:
            return False
