import pandas as pd

from crawlers.blueticket import Blueticket
from crawlers.pensanoevento import PensaNoEvento
from crawlers.sympla import Sympla
from enumerator.eventtype import EventType

TIMEOUT = 120


def create_dataframe(blueticket_list, pensa_no_evento_list, sympla_list):
    event_data = []
    for event_list in [blueticket_list, pensa_no_evento_list, sympla_list]:
        for event in event_list:
            event_data.append({
                "Nome": event.name,
                "Tipo Evento": event.event_type,
                "Data": event.date,
                "Horário Abertura": event.open_hour,
                "Classificação": event.rating_audience,
                "Local": event.location,
                "Cidade": event.city,
                "URL Dados": event.url_event
            })

    df = pd.DataFrame(event_data)
    return df


def save_to_csv(blueticket_list, pensa_no_evento_list, sympla_list, filename):
    df = create_dataframe(blueticket_list, pensa_no_evento_list, sympla_list)
    df.to_csv(filename, index=False)


def run_blueticket(event_type):
    b = Blueticket(event_type)
    b.start_connection()
    b.search_page()
    list_events = b.get_events()
    return list_events


def run_pensa_no_evento(event_type):
    p = PensaNoEvento(event_type)
    p.start_connection()
    p.search_page()
    list_events = p.get_events()
    return list_events


def run_sympla(event_type):
    s = Sympla(event_type)
    s.start_connection()
    s.search_page()
    list_events = s.get_events()
    return list_events


def collect_data(event_type):
    blueticket_list = run_blueticket(event_type)
    # pensa_no_evento_list = run_pensa_no_evento(event_type)
    # sympla_list = run_sympla(event_type)
    # save_to_csv(blueticket_list, pensa_no_evento_list, sympla_list, 'output/result.csv')


if __name__ == '__main__':
    collect_data(EventType.TODOS)
