import json
from pprint import pprint
import re
from typing import TypedDict
from bs4 import BeautifulSoup
import requests
import urllib.parse
from datetime import date, datetime
import argparse

from type_info.types import InformacionVotacion, ResultadosPorPartido, Voto


def analisis_periodos(periodos):
    resultado = {}
    for periodo in periodos:
        url_periodo = urllib.parse.urljoin(
            "http://sitl.diputados.gob.mx/LXV_leg/", periodo['href'])
        req_per = requests.get(url_periodo)
        soup_per = BeautifulSoup(req_per.text, "html.parser")

        votaciones_per = soup_per.find_all("a", href=re.compile(
            'estadistico_votacion'), class_="linkNegro")
        # agregar a objeto
        resultado[periodo.string] = analisis_votaciones_periodo(votaciones_per)

    return resultado


def analisis_votaciones_periodo(votaciones_per) -> list[InformacionVotacion]:
    resultado = []
    for votacion in votaciones_per:
        url_resultado_votacion = urllib.parse.urljoin(
            "http://sitl.diputados.gob.mx/LXV_leg/", votacion['href'])
        request_lista_votaciones = requests.get(url_resultado_votacion)
        soup_lista_votaciones = BeautifulSoup(
            request_lista_votaciones.text, "html.parser")

        resultado.append(analisis_resultados_votacion(soup_lista_votaciones))

    return resultado


def analisis_resultados_votacion(votacion) -> InformacionVotacion:
    # El titular verde
    # http://sitl.diputados.gob.mx/LXV_leg/estadistico_votacionnplxv.php?votaciont=3
    datos_votacion = votacion.find('td', class_="Estilo51", bgcolor="#595843")
    titulo = datos_votacion.text.split('\n')

    resultado = {
        'nombre': titulo[0],
        'votos': []
    }

    # Por alguna razon no funcionaba cuando tambien agregabamos la clase 'linkNegro' 🤷
    votos_diputados = votacion.find_all(
        "a", href=re.compile("listados_votaciones"))

    for lista_votos in votos_diputados:
        resultado['votos'].append({
            'nombre_partido': lista_votos.string,
            'resultados': analisis_pagina_votaciones_partido(lista_votos['href'])
        })

    return resultado


def analisis_pagina_votaciones_partido(url_votacion: str) -> ResultadosPorPartido:
    result = []
    # http://sitl.diputados.gob.mx/LXV_leg/listados_votacionesnplxv.php?partidot=14&votaciont=3

    req_vot_partido = requests.get(urllib.parse.urljoin(
        "http://sitl.diputados.gob.mx/LXV_leg/", url_votacion))
    soup_vot_partido = BeautifulSoup(req_vot_partido.text, "html.parser")

    votos_diputados = soup_vot_partido.find_all(
        'a', class_="linkVerde", href=re.compile('votaciones_por_per'))

    for voto_diputado in votos_diputados:
        nom_diputado = voto_diputado.string

        # Hasta el momento: Ausente, solo asistencia, a favor, en contra
        sentido_voto = voto_diputado.parent.parent.next_sibling.next_sibling.text
        result.append({'nombre': nom_diputado, 'sentido_voto': sentido_voto})

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=str, help="Lugar donde guardar output en JSON")
    parser.add_argument('--resultado_votacion', type=str, help="Procesa resultados de una votacion, ej: http://sitl.diputados.gob.mx/LXV_leg/estadistico_votacionnplxv.php?votaciont=3")
    parser.add_argument('--resultado_votaciones_por_partido', type=str,
                        help="Procesa resultados de una votacion, ej: http://sitl.diputados.gob.mx/LXV_leg/listados_votacionesnplxv.php?partidot=14&votaciont=3")
    args = parser.parse_args()

    # http://sitl.diputados.gob.mx/LXV_leg/votaciones_por_periodonplxv.php
    # Descubrimiento:
    # Todo es  una tabla
    # Los diputados tienen su nombre en un link,
    # podemos buscar su columna buscando la columna con un elemento a con la clase "linkVerde"
    # La siguiente columna tiene su sentido de voto

    if args.resultado_votacion != None:
        req = requests.get(args.resultado_votacion)
        soup = BeautifulSoup(req.text, "html.parser")

        pprint(analisis_resultados_votacion(soup))
    elif args.resultado_votaciones_por_partido != None:
        pprint(analisis_pagina_votaciones_partido(args.resultado_votaciones))
    else:
        print("PROCESANDO")
        req = requests.get(
            "http://sitl.diputados.gob.mx/LXV_leg/votaciones_por_periodonplxv.php")
        soup = BeautifulSoup(req.text, "html.parser")

        periodos_results = soup.find_all(
            "a", href=re.compile("votacionesxperiodonplxv.php"))

        with open(args.output, "w") as file:
            file.write(json.dumps(analisis_periodos(periodos_results)))
        
        print(f"Resultados guardados en {args.output}")
