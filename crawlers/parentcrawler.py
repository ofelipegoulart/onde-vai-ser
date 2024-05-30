import abc


class ParentCrawler:

    def __init__(self):
        __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def start_connection(cls):
        pass

    @abc.abstractmethod
    def search_page(cls):
        pass
