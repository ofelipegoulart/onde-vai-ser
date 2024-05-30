from crawlers.pensanoevento import PensaNoEvento
from enumerator.eventtype import EventType

if __name__ == '__main__':
    p = PensaNoEvento(EventType.TODOS)
    p.start_connection()
    p.search_page()
    p.get_events()
