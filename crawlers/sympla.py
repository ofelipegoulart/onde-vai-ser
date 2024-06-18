import json

import bs4
import requests
from bs4 import BeautifulSoup

from crawlers.parentcrawler import ParentCrawler
from enumerator.crawlertype import CrawlerType
from enumerator.eventtype import EventType
from event.event import Event
from utils.utils import Utils

TIMEOUT = 120


class Sympla(ParentCrawler):

    def __init__(self, event_type):
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
        self.cookies: {} = None
        self.json_data = None
        self.search_page_soup = None
        self.event_counter: int = 0
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
                TypeError(f"[{CrawlerType.SYMPLA.value}] Ocorreu um erro. Verifique o parâmetro tipo de evento")
        if self.event_type.name != "TODOS":
            req = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=TIMEOUT)
            response = req.json()
            response['component']['service_params']['city'] = 'Florian%C3%B3polis'
            response['component']['service_params']['sort'] = 'location-sort'
            response['component']['service_params']['page'] = self.page_counter
            self.json_data = {'service': '/v4/mapsearch', 'params': response['component']['service_params']['url']}
        else:
            self.json_data = {"service": "/v4/search",
                              "params": {
                                  "include_response": "true", "limit": "300",
                                  "location": "-27.5878,-48.54764",
                                  "sort": "location-score",
                                  "state": "SC", "city": "Florianopolis"}}

    def search_page(self):
        print(f"[{CrawlerType.SYMPLA.value}] Entrando na página de busca...")
        req = requests.post(self.url + 'search', json=self.json_data, cookies=self.cookies, timeout=TIMEOUT)
        page = BeautifulSoup(req.content, 'lxml')
        self.set_search_page_soup(page)
        self.url = req.url

    def get_events(self):
        print(f"[{CrawlerType.SYMPLA.value}] Buscando eventos do tipo {self.event_type.value.upper()}...")
        page = self.get_search_page_soup()
        data = json.loads(page.text)['data']
        for evento in data:
            event_instance = Event("", self.event_type, "", "", "", "", "", self.url)
            categories = ''
            if evento['location']['city'] not in ['Florianópolis', 'São José']:
                self.event_counter += 1
                if self.event_counter == 5:
                    return self.get_event_list()
            else:
                event_instance.set_name(evento['name'])
                if self.event_type is EventType.TODOS:
                    self.json_data = {'service': '/v4/search',
                                      'params': {'q': evento['url']}}
                    event_type_req = requests.post('https://www.sympla.com.br/api/v1/search', timeout=TIMEOUT,
                                                   headers=self.headers, cookies=self.cookies, json=self.json_data)
                    if 'softblock' not in event_type_req.text:
                        more_info_event = json.loads(event_type_req.text)['data']
                        element_desired = more_info_event[0]
                        if 'format_name' in element_desired:
                            categories = element_desired['format_name']
                        elif 'category_prim' in element_desired:
                            categories = element_desired['category_prim']['name']
                        elif 'theme_name' in element_desired:
                            categories = element_desired['theme_name']
                        else:
                            categories = None
                            event_instance.set_event_type(categories)
                        formated_event_type = None
                        match categories:
                            case 'Curso | Workshop | Oficinas | Treinamento':
                                formated_event_type = EventType.CURSO
                            case 'Congresso | Simpósio | Seminário':
                                formated_event_type = EventType.CONGRESSOS
                            case 'Festa':
                                formated_event_type = EventType.BALADA
                            case 'Show':
                                formated_event_type = EventType.SHOWS
                            case 'Apresentações e espetáculos':
                                formated_event_type = EventType.TEATRO
                            case 'Palestra | Conferência | Painel':
                                formated_event_type = EventType.CONGRESSOS
                            case 'Meetup | Networking':
                                formated_event_type = EventType.CONGRESSOS
                            case 'Festival':
                                formated_event_type = EventType.SHOWS
                        if formated_event_type is not None:
                            event_instance.set_event_type(formated_event_type.value.capitalize())
                        else:
                            event_instance.set_event_type(None)
                    else:
                        TypeError(f"[{CrawlerType.SYMPLA.value.upper()}] Não foi possível pegar o tipo de evento")
                event_instance.set_date(Utils().get_regular_date(evento['start_date'], CrawlerType.SYMPLA))
                event_instance.set_open_hour(Utils().get_open_hour(evento['start_date'], CrawlerType.SYMPLA))
                event_instance.set_location(evento['location']['name'])
                event_instance.set_rating_audience(None)
                event_instance.set_city(evento['location']['city'])
                self.event_list.append(event_instance)
        return self.get_event_list()
