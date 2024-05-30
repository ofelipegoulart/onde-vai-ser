import bs4.element
import requests
from bs4 import BeautifulSoup

from crawlers.parentcrawler import ParentCrawler
from enumerator.cralwertype import CrawlerType
from enumerator.eventtype import EventType
from event.event import Event
from utils.utils import Utils

TIMEOUT = 120


class PensaNoEvento(ParentCrawler):

    def __init__(self, event_type):
        super().__init__()
        self.url = 'https://www.pensanoevento.com.br/'
        self.params = {
            'q': 'florianópolis'
        }
        self.event_type = event_type
        self.cookies = None
        self.headers_connection = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=1',
        }
        self.headers_search = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://www.pensanoevento.com.br/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=1',
        }
        self.csrf_token = None
        self.search_page_soup = None
        self.event_list = list()

    def set_url(self, url):
        self.url = url

    def get_url(self):
        return self.url

    def set_params(self, params):
        self.params = params

    def get_params(self):
        return self.params

    def set_event_type(self, event_type):
        self.event_type = event_type

    def get_event_type(self):
        return self.event_type

    def set_cookies(self, cookies):
        self.cookies = cookies

    def get_cookies(self):
        return self.cookies

    def set_headers_connection(self, headers_connection):
        self.headers_connection = headers_connection

    def get_headers_connection(self):
        return self.headers_connection

    def set_headers_search(self, headers_search):
        self.headers_search = headers_search

    def get_headers_search(self):
        return self.headers_search

    def set_csrf_token(self, csrf_token):
        self.csrf_token = csrf_token

    def get_csrf_token(self):
        return self.csrf_token

    def set_search_page_soup(self, search_page_soup):
        self.search_page_soup = search_page_soup

    def get_search_page_soup(self):
        return self.search_page_soup

    def set_event_list(self, event_list: list):
        self.event_list = event_list

    def get_event_list(self):
        return self.event_list

    def start_connection(self):
        print(f"[{CrawlerType.PENSA_NO_EVENTO.value}] Iniciando conexão...")
        req = requests.get(url=self.url, headers=self.headers_connection, timeout=300)
        self.set_cookies(req.cookies)
        if req.status_code == 200:
            soup = BeautifulSoup(req.content, 'lxml')
            csrf_token_tag = soup.find('input', {'name': 'csrf_token', 'type': 'hidden'})['value']
            if csrf_token_tag:
                self.set_csrf_token(csrf_token_tag)
            else:
                return TypeError("Não foi possível obter o CSRF token")
        else:
            return TypeError("Erro na requisição")

    def search_page(self):
        print(f"[{CrawlerType.PENSA_NO_EVENTO.value}] Entrando na página de busca...")
        search_url = self.url + 'buscar/'
        self.params['csrf_token'] = self.get_csrf_token()
        req = requests.get(url=search_url, params=self.params, cookies=self.get_cookies(),
                           headers=self.headers_search, json={}, timeout=TIMEOUT)
        if req.status_code == 200:
            soup = BeautifulSoup(req.content, "lxml")
            self.set_search_page_soup(soup)

    def get_events(self):
        print(f"[{CrawlerType.PENSA_NO_EVENTO.value}] Buscando eventos do tipo {self.event_type.value}...")
        divs_events = self.get_search_page_soup().find_all('h3')
        titles = [title for title in divs_events if len(title.attrs.keys()) == 0 and
                  not isinstance(title, bs4.element.NavigableString)]
        for element in titles:
            self.headers_search[
                'Referer'] = f'https://www.pensanoevento.com.br/buscar/?q=Florian%C3%B3polis&csrf_token={self.csrf_token}'
            if self.event_type.value in element.next.attrs['href']:
                instance_events = self.get_info_event(element.next.attrs['href'])
                self.event_list.append(instance_events)
            else:
                if self.event_type == EventType.TODOS:
                    instance_events = self.get_info_event(element.next.attrs['href'])
                    self.event_list.append(instance_events)
                else:
                    continue

    def get_info_event(self, url_event: str):
        req = requests.get(url=url_event, cookies=self.cookies, headers=self.headers_search,
                           timeout=TIMEOUT)
        soup = BeautifulSoup(req.content, "lxml")
        event_instance = Event("", "", "", "", "", "", "", "")
        events = soup.find('ul', attrs={'class': 'list'})
        if events:
            events = events.find_all('li')
            tags = [event for event in events if not isinstance(event, bs4.element.NavigableString)]
            for event in tags:
                if not event.attrs:
                    if 'Cardápio' in soup.text:
                        event_instance.set_event_type('gastronomia')
                    if event.find('b').text == "Nome do Evento:":
                        event_name = Utils().get_regular_element_pensa_no_evento(event)
                        event_instance.set_name(event_name)
                    if event.find('b').text == "Data:":
                        event_date = Utils().get_regular_element_pensa_no_evento(event)
                        event_instance.set_date(event_date)
                    if event.find('b').text == "Horário de Abertura:":
                        # Verificar horário
                        open_hour = Utils().get_open_hour_pensa_no_evento(event)
                        event_instance.set_open_hour(open_hour)
                    if event.find('b').text == "Classificação:":
                        rating_audience = Utils().get_regular_element_pensa_no_evento(event)
                        event_instance.set_rating_audience(rating_audience)
                    if event.find('b').text == "Local:":
                        location = Utils().get_location_element_pensa_no_evento(event)
                        event_instance.set_location(location)
                        city = Utils().get_city_element_pensa_no_evento(event)
                        event_instance.set_city(city)
                    event_type_url = Utils().get_event_type_by_url(url_event, CrawlerType.PENSA_NO_EVENTO)
                    if 'Cardápio' not in soup.text:
                        event_instance.set_event_type(event_type_url)
                    event_instance.set_url_event(url_event)
                else:
                    continue
        else:
            print(f"[{CrawlerType.PENSA_NO_EVENTO.value}] Busca encerrada.")
        return event_instance
