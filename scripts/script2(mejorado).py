import os
import json
import re
import requests
import matplotlib.pyplot as plt
import numpy as np
import statistics
import pandas as pd
import openpyxl

# URL para la API TMDb (Movie Database)
API_KEY = "8672905b631a8a0b3a41a62affffec7f"  # Tu API key

# Expresiones regulares para validar fecha y título
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")  # Validar formato YYYY-MM-DD
RE_TITULO = re.compile(r"^[A-Za-z0-9\s]+$")  # Validar títulos solo con caracteres alfanuméricos y espacios

class TMDbAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def obtener_generos(self):
        """Obtiene la lista de géneros de películas disponibles."""
        url = f"{self.base_url}/genre/movie/list?api_key={self.api_key}&language=es"
        response = requests.get(url)
        return response.json()["genres"]

    def buscar_peliculas(self, genero, desde, hasta, top_n=10, orden="desc"):
        """Busca las mejores películas de un género dentro de un rango de fechas."""
        url = (
            f"{self.base_url}/discover/movie?api_key={self.api_key}&language=es"
            f"&sort_by=vote_average.{orden}&vote_count.gte=100"
            f"&with_genres={genero}"
            f"&primary_release_date.gte={desde}&primary_release_date.lte={hasta}" +
            f"&page=1"
        )
        response = requests.get(url)
        return response.json()["results"][:top_n]

    def obtener_mejores_peores(self, generos, desde, hasta, top_n=10, mejor=True):
        """Obtiene las mejores o peores películas de los géneros dados."""
        peliculas_totales = []
        for genero in generos:
            peliculas = self.buscar_peliculas(genero, desde, hasta, top_n=top_n*3)
            peliculas_totales.extend(peliculas)

        peliculas_unicas = {p['id']: p for p in peliculas_totales}.values()
        peliculas_ordenadas = sorted(peliculas_unicas, key=lambda x: x['vote_average'], reverse=mejor)
        return peliculas_ordenadas[:top_n]

    def graficar_peliculas(self, peliculas):
        """Genera una gráfica de barras horizontales con las puntuaciones de las películas."""
        nombres = [pelicula['title'] for pelicula in peliculas]
        puntuaciones = np.array([pelicula['vote_average'] for pelicula in peliculas])

        # Preguntamos si se quiere mostrar la gráfica
        mostrar_grafica = input("\n¿Quieres ver una gráfica de las puntuaciones? (si/no): ").strip().lower()

        if mostrar_grafica == "si":
            plt.figure(figsize=(10, 6))
            plt.barh(nombres, puntuaciones, color='lightgreen')
            plt.xlabel('Puntuación')
            plt.title('Puntuación de las Películas')
            plt.xlim(0, 10)

            # Añadir las puntuaciones sobre las barras
            for i, v in enumerate(puntuaciones):
                plt.text(v + 0.1, i, f'{v:.2f}', va='center', fontsize=10)

            plt.tight_layout()
            plt.show()

        # Calcular la media de las puntuaciones
        media = statistics.mean(puntuaciones)
        print(f"Media de las puntuaciones: {media:.2f}")

def cargar_json(path="peliculas_resultado.json"):
    """Carga y valida las películas desde un archivo JSON."""
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        datos = json.load(f)

    datos_validos = []
    for peli in datos:
        titulo = peli.get("title", "").strip()
        fecha = peli.get("release_date", "").strip()
        puntuacion = peli.get("vote_average", None)

        # Validación usando expresiones regulares
        if RE_FECHA.match(fecha) and RE_TITULO.match(titulo) and isinstance(puntuacion, (int, float)):
            datos_validos.append({
                "title": titulo,
                "release_date": fecha,
                "vote_average": float(puntuacion)
            })
        else:
            print(f" Dato inválido descartado: {peli}")

    print(f"\n {len(datos_validos)} películas válidas cargadas.")
    return datos_validos

# Transformar en DataFrame
def preparar_dataframe(peliculas):
    """Prepara los datos para análisis y visualización."""
    df = pd.DataFrame(peliculas)
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["release_date", "vote_average"])
    df["año"] = df["release_date"].dt.year
    return df

# Análisis estadístico
def analisis_estadistico(df):
    """Realiza un análisis estadístico sobre las puntuaciones de las películas."""
    puntuaciones = df["vote_average"].tolist()

    media = np.mean(puntuaciones)
    mediana = np.median(puntuaciones)
    try:
        moda = statistics.mode(puntuaciones)
    except statistics.StatisticsError:
        moda = "No única"

    std_dev = np.std(puntuaciones)

    print("\n Estadísticas de puntuaciones:")
    print(f"- Media: {media:.2f}")
    print(f"- Mediana: {mediana}")
    print(f"- Moda: {moda}")
    print(f"- Desviación estándar: {std_dev:.2f}")

    return {
        "media": media,
        "mediana": mediana,
        "moda": moda,
        "desviacion": std_dev
    }

def preparar_para_visualizacion(df):
    """Prepara los datos para visualización (top 5)."""
    df_viz = df[["title", "año", "vote_average"]].copy()
    df_viz.sort_values(by="vote_average", ascending=False, inplace=True)
    df_viz.reset_index(drop=True, inplace=True)
    print("\n Datos listos para graficar (top 5):")
    print(df_viz.head(5))
    return df_viz

# Guardar en CSV para herramientas externas
def exportar_csv(df, nombre="peliculas_preparadas.csv"):
    """Exporta los datos a un archivo CSV."""
    df.to_csv(nombre, index=False, encoding="utf-8")
    print(f"\n Datos exportados para visualización en: {nombre}")

# Función para exportar a Excel
def exportar_excel(df, estadisticas, nombre_archivo="peliculas_analisis.xlsx"):
    """Exporta los datos a un archivo Excel con dos hojas: datos y estadísticas."""
    with pd.ExcelWriter(nombre_archivo, engine="openpyxl") as writer:
        # Hoja 1: Datos preparados para visualización
        df.to_excel(writer, sheet_name="Películas", index=False)

        # Hoja 2: Estadísticas resumidas
        df_estadisticas = pd.DataFrame([estadisticas])
        df_estadisticas.to_excel(writer, sheet_name="Estadísticas", index=False)

    print(f"\n Archivo Excel exportado correctamente como: {nombre_archivo}")


def main():
    api_key = API_KEY  # Tu clave API
    api = TMDbAPI(api_key)

    generos = api.obtener_generos()

    print("Selecciona uno o más géneros (separados por coma) o elige la opción 20 para todos los géneros:")
    for i, genero in enumerate(generos, 1):
        print(f"{i}. {genero['name']}")
    print("20. Todos los géneros")

    try:
        opcion = input("\nElige géneros: ").strip()
        if opcion == "20":
            generos_seleccionados = [g['id'] for g in generos]
        else:
            opcion = [int(x) for x in opcion.split(",")]
            generos_seleccionados = [generos[i-1]['id'] for i in opcion]
    except ValueError:
        print("Opción no válida.")
        return

    # Solicitar fechas de inicio y fin
    fecha_desde = input("Introduce la fecha de inicio (YYYY-MM-DD): ").strip()
    fecha_hasta = input("Introduce la fecha de fin (YYYY-MM-DD): ").strip()

    if not RE_FECHA.match(fecha_desde) or not RE_FECHA.match(fecha_hasta):
        print("Fechas inválidas.")
        return

    opcion_orden = input("¿Quieres ver las mejores o las peores películas? (mejores/peores): ").strip().lower()


 # Pregunta cuántas películas mostrar antes de buscarlas
    try:
        num_peliculas = int(input("\n¿Cuántas películas quieres ver? (Por defecto son 10): ").strip())
    except ValueError:
        num_peliculas = 10

    if num_peliculas < 1:
        num_peliculas = 10

    # Ahora sí hacemos la búsqueda
    if opcion_orden == "mejores":
        peliculas = api.obtener_mejores_peores(generos_seleccionados, fecha_desde, fecha_hasta, top_n=num_peliculas, mejor=True)
        print("\nMejores Películas:")
    elif opcion_orden == "peores":
        peliculas = api.obtener_mejores_peores(generos_seleccionados, fecha_desde, fecha_hasta, top_n=num_peliculas, mejor=False)
        print("\nPeores Películas:")
    else:
        print("Opción inválida. Mostrando las mejores por defecto.")
        peliculas = api.obtener_mejores_peores(generos_seleccionados, fecha_desde, fecha_hasta, top_n=num_peliculas, mejor=True)


    # Pregunta el número de películas a mostrar
    try:
        num_peliculas = int(input("\n¿Cuántas películas quieres ver? (Por defecto son 10): ").strip())
    except ValueError:
        num_peliculas = 10

    if num_peliculas < 1:
        num_peliculas = 10

    peliculas = peliculas[:num_peliculas]

    # Mostrar el top de películas
    for i, pelicula in enumerate(peliculas, 1):
        print(f"{i}. {pelicula['title']} (Puntuación: {pelicula['vote_average']})")

    # Pregunta sobre la gráfica
    api.graficar_peliculas(peliculas)

    guardar = input("\n¿Quieres guardar los resultados en un archivo? (sí/no): ").strip().lower()
    if guardar == "sí" or guardar == "si":
        formatos = input("¿En qué formato deseas guardarlo? (txt/json/ambos): ").strip().lower()

        if formatos in ("txt", "ambos"):
            with open("resultados_peliculas.txt", "w", encoding="utf-8") as f:
                for peli in peliculas:
                    f.write(f"{peli['title']} - Puntuación: {peli['vote_average']}\n")
            print("Archivo guardado como 'resultados_peliculas.txt'.")

        if formatos in ("json", "ambos"):
            with open("resultados_peliculas.json", "w", encoding="utf-8") as f:
                json.dump(peliculas, f, ensure_ascii=False, indent=4)
            print("Archivo guardado como 'resultados_peliculas.json'.")

if __name__ == "__main__":
    main()
    
    # Cargar y validar datos del JSON (si ya se generó previamente)
    datos = cargar_json("resultados_peliculas.json")
    if datos:
        df = preparar_dataframe(datos)
        estadisticas = analisis_estadistico(df)
        df_viz = preparar_para_visualizacion(df)

        # Exportar a CSV
        exportar_csv(df_viz, nombre="peliculas_preparadas.csv")

        # Exportar a Excel
        exportar_excel(df_viz, estadisticas, nombre_archivo="peliculas_analisis.xlsx")
