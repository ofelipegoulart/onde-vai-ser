class Event:

    def __init__(self, name, event_type, date, open_hour, rating_audience, location, city, url_event):
        self.name = name
        self.event_type = event_type
        self.date = date
        self.open_hour = open_hour
        self.rating_audience = rating_audience
        self.location = location
        self.city = city
        self.url_event = url_event

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def set_event_type(self, event_type):
        self.event_type = event_type

    def get_event_type(self):
        return self.event_type

    def set_date(self, date):
        self.date = date

    def get_date(self):
        return self.date

    def set_open_hour(self, open_hour):
        self.open_hour = open_hour

    def get_open_hour(self):
        return self.open_hour

    def set_rating_audience(self, rating_audience):
        self.rating_audience = rating_audience

    def get_rating_audience(self):
        return self.rating_audience

    def set_location(self, location):
        self.location = location

    def get_location(self):
        return self.location

    def set_city(self, city):
        self.city = city

    def get_city(self):
        return self.city

    def set_url_event(self, url_event):
        self.url_event = url_event

    def get_url_event(self):
        return self.url_event
