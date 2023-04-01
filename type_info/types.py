
from datetime import date
from typing import TypedDict


class Voto(TypedDict):
    nombre: str
    sentido_voto: str

class ResultadosPorPartido(TypedDict):
    nombre_partido: str
    votos: list[Voto]

class InformacionVotacion(TypedDict):
    nombre: str
    fecha: str