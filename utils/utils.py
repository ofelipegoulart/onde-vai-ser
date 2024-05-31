import datetime

import requests
from bs4 import BeautifulSoup

from enumerator.crawlertype import CrawlerType

TIMEOUT = 300


class Utils:

    def __init__(self):
        self.attr = None

    def get_regular_element_pensa_no_evento(self, attr: any) -> str:
        parsed_element = attr.find('b').parent.text.strip().split(':')[1]
        return parsed_element

    def get_open_hour(self, attr: any, brand_name: CrawlerType):
        hour = ""
        if brand_name == CrawlerType.PENSA_NO_EVENTO:
            hour = attr.find('b').parent.contents[3]
        if brand_name == CrawlerType.BLUETICKET:
            list_elements = attr.split()
            if list_elements[0] == 'Abertura:':
                hour = list_elements[1]
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
                return partes_url[3].capitalize()
            else:
                return ""

    def get_regular_date(self, data_str: str, crawler: CrawlerType):
        print("Data_STR: " + data_str)
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

#
# u = Utils()
# date = u.get_regular_date("Start Date: 2024-06-15T23:00:00+00:00", CrawlerType.SYMPLA)
# print(date)
