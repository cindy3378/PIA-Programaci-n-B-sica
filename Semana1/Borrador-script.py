#borrador del codigo

import requests
import re

API_KEY = '8672905b631a8a0b3a41a62affffec7f'

def validar_fecha(fecha):
    return re.match(r"^\d{4}-\d{2}-\d{2}$", fecha) is not None

def obtener_generos():
    url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={API_KEY}&language=es"
    response = requests.get(url)
    return response.json()["genres"]

def buscar_peliculas(generos, desde, hasta, top_n=10):
    ids_generos = ",".join(str(g["id"]) for g in generos)
    url = (
        f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&language=es"
        f"&sort_by=vote_average.desc&vote_count.gte=100"
        f"&with_genres={ids_generos}"
        f"&primary_release_date.gte={desde}&primary_release_date.lte={hasta}"
        f"&page=1" )

    response = requests.get(url)
    return response.json()["results"][:top_n]

# Ejemplo de uso

generos_disponibles = obtener_generos()
generos_filtrados = [g for g in generos_disponibles if g["name"] in ["Acción", "Aventura"]]
peliculas = buscar_peliculas(generos_filtrados, "1990-01-01", "2000-12-31", 10)

for i, peli in enumerate(peliculas, 1):

    print(f"{i}. {peli['title']} ({peli['release_date']}) - {peli['vote_average']}")
