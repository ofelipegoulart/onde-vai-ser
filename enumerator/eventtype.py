from enum import Enum


class EventType(Enum):
    TODOS = "todos"
    BALADA = "baladas" or "balada"
    SHOWS = "shows"
    GASTRONOMIA = "gastronomia"
    STANDUP = "standup" or "comédia"
    INFANTIL = "infantil"
    TEATRO = "teatro"
    CURSO = "cursos e workshops"
    CONGRESSOS = "congressos"
    ESPORTIVO = "esportivo"
