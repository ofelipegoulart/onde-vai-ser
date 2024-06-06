import pandas as pd

from crawlers.blueticket import Blueticket
from crawlers.pensanoevento import PensaNoEvento
from crawlers.sympla import Sympla
from eventtype import EventType

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
                "Classificação Público": event.rating_audience,
                "Local": event.location,
                "Cidade": event.city,
                "URL Evento": event.url_event
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
    list_events = recursive_sympla_search(event_type, counter=1)
    return list_events


# Foi necessária a implementação desse método, pois a API do Sympla trabalha com paginação
def recursive_sympla_search(event_type, counter=1):
    s = Sympla(event_type, counter)
    s.start_connection()
    s.search_page()
    events = s.get_events()
    if s.check_if_more_events():
        more_events = recursive_sympla_search(event_type, counter + 1)
        events.extend(more_events)
    return events


def collect_data(event_type):
    blueticket_list = run_blueticket(event_type)
    # pensa_no_evento_list = run_pensa_no_evento(event_type)
    # sympla_list = run_sympla(event_type)
    save_to_csv(blueticket_list, [], [], 'output/result.csv')


if __name__ == '__main__':
    collect_data(EventType.TODOS)
