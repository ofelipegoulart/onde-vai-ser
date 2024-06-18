import datetime
import json
import re

import requests
from bs4 import BeautifulSoup

from enumerator.crawlertype import CrawlerType

TIMEOUT = 120


class Utils:

    def __init__(self):
        self.attr = None

    def get_regular_element_pensa_no_evento(self, attr: any) -> str:
        parsed_element = attr.find('b').parent.text.strip().split(':')[1]
        return parsed_element

    def get_open_hour(self, attr: any, brand_name: CrawlerType):
        match brand_name.value:
            case "Pensa no Evento":
                return attr.find('b').parent.contents[3]
            case "Blueticket":
                list_elements = attr.split()
                if list_elements[0] == 'Abertura:':
                    return list_elements[1]
            case "Sympla":
                return attr.split('T')[1][0:5]

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
        """
        :param url: url do evento, que tem o tipo de evento dentro da string da url
        :param brand_name: crawler executado
        :return: tipo do evento
        """
        if brand_name is CrawlerType.PENSA_NO_EVENTO:
            partes_url = url.split("/")
            if len(partes_url) >= 4:
                return partes_url[3].capitalize()
            else:
                return ""

    def get_regular_date(self, data_str: str, crawler: CrawlerType):
        """
        :param data_str: data a ser formatada
        :param crawler: crawler executado
        :return: data formatada
        """
        formated_date = ""
        if crawler.value == 'Blueticket':
            data_parts = data_str.split()
            months = {"Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5,
                      "Junho": 6, "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10,
                      "Novembro": 11, "Dezembro": 12}
            year = datetime.date.today().year
            if 'a' in data_parts:
                if 'Data' in data_parts:
                    return None
                else:
                    first_date_day = data_parts[0]
                    second_date_day = data_parts[2]
                    first_date_month = data_parts[4]
                    month_num = months[first_date_month]
                    first_date_obj = datetime.datetime(year=int(year), month=month_num, day=int(first_date_day))
                    second_date_obj = datetime.datetime(year=int(year), month=month_num, day=int(second_date_day))
                    first_date_formated_date = first_date_obj.strftime("%d/%m/%Y")
                    second_date_formated_date = second_date_obj.strftime("%d/%m/%Y")
                    formated_date = first_date_formated_date + ' a ' + second_date_formated_date
            else:
                day = data_parts[1]
                month = data_parts[3]
                month_num = months[month]
                date_obj = datetime.datetime(year=int(year), month=month_num, day=int(day))
                formated_date = date_obj.strftime("%d/%m/%Y")
        if crawler.value == 'Sympla':
            input_date = data_str.split('T')[0].replace("-", "/").split('/')
            year_s = input_date[0]
            month_s = input_date[1]
            day_s = input_date[2]
            date_obj = datetime.datetime(year=int(year_s), month=int(month_s), day=int(day_s))
            formated_date = date_obj.strftime("%d/%m/%Y")
        return formated_date

    def get_event_type_by_res(self, category):
        """
        :param category: categoria recebida
        :return: valor da categoria idêntico ao enumerador
        """
        match category:
            case "Baladas" | "Shows" | "Gastronomia" | "Stand Up":
                return category
            case "Cursos e Workshops":
                return "Cursos"
            case "Teatros":
                return "Teatro"
            case "Palestras":
                return "Congresso"
            case "Esportivos":
                return "Esportivo"
            case "Festivais":
                return "Shows"
            case "Reveillon":
                return "Baladas"
            case None:
                return None

    def get_rating_audience_blueticket(self, slug: str, id: str):
        """
        :param slug: slug para completar a url da requisição
        :param id: id para completar a url da requisição
        :param crawler: tipo de crawler, era usado quando esse método era usado para dois crawlers
        :return: classificação indicativa
        """
        req = requests.get(f'https://soulapi.blueticket.com.br/api/pdv/event/detail/{id}', timeout=TIMEOUT)
        if req.status_code == 200:
            json_response = json.loads(req.text)
            age = json_response['classificacao_etaria_obs']
            if age:
                soup_age = BeautifulSoup(age, 'lxml')
                if 'Livre' in soup_age.find('p').text:
                    return 'Livre'
                else:
                    if soup_age.find('span'):
                        return re.findall(r"\d+", soup_age.find('span').text)[0] + ' anos'
                    elif 'Crianças' and 'pagam ingresso' in soup_age.text:
                        return 'Livre'
                    else:
                        find_digits_age = re.findall(r"\d+", age)
                        if len(find_digits_age) != 1:
                            return None
                        else:
                            return find_digits_age[0] + ' anos'

        # def get_rating_audience(self, url: str, id: str, crawler: CrawlerType):
        # if crawler.value == 'Sympla':
        #     if 'bileto' in url:
        #         r = requests.get(f'https://bff-sales-api-cdn.bileto.sympla.com.br/api/v1/events/{id}', headers=headers,
        #                          timeout=TIMEOUT)
        #         if r.status_code == 200:
        #             json_sympla = json.loads(r.text)
        #             return json_sympla['data']['planner_information']['age_rating']['age_rating_name']
        #         else:
        #             TypeError(f"[{CrawlerType.SYMPLA.value}] Não foi possível completar a requisição")
        #     else:
        #         TypeError(f"[{CrawlerType.SYMPLA.value}] Não disponibilizado pela API")
