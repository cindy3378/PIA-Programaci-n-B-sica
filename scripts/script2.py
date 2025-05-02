with open('../data/peliculas_resultado.json', encoding='utf-8') as f:
    peliculas = json.load(f)

import json
import re
import os
import numpy as np
import statistics as stats
import pandas as pd

# Ruta del archivo JSON generado por el primer script
INPUT_FILE = "data/peliculas_resultado.json"
OUTPUT_CSV = "data/peliculas_preparadas.csv"
OUTPUT_XLSX = "data/peliculas_analisis.xlsx"

# Validaciones con expresiones regulares
def validar_fecha(fecha):
    return re.match(r"^\d{4}-\d{2}-\d{2}$", fecha) is not None

def validar_titulo(titulo):
    return isinstance(titulo, str) and len(titulo.strip()) > 0

def validar_puntaje(puntaje):
    return isinstance(puntaje, (int, float)) and 0 <= puntaje <= 10

# Cargar datos desde JSON
with open(INPUT_FILE, encoding='utf-8') as f:
    peliculas = json.load(f)

# Validación y limpieza
peliculas_validas = []
for peli in peliculas:
    if all([
        validar_titulo(peli.get("title")),
        validar_fecha(peli.get("release_date", "")),
        validar_puntaje(peli.get("vote_average"))
    ]):
        peliculas_validas.append({
            "titulo": peli["title"],
            "fecha": peli["release_date"],
            "puntaje": peli["vote_average"]
        })

# Análisis estadístico
puntajes = [p["puntaje"] for p in peliculas_validas]

media = np.mean(puntajes)
mediana = np.median(puntajes)
try:
    moda = stats.mode(puntajes)
except stats.StatisticsError:
    moda = "No hay moda única"
desviacion = np.std(puntajes)

# Mostrar resultados
print("=== Estadísticas ===")
print(f"Películas válidas: {len(peliculas_validas)}")
print(f"Media: {media:.2f}")
print(f"Mediana: {mediana:.2f}")
print(f"Moda: {moda}")
print(f"Desviación estándar: {desviacion:.2f}")

# Exportar CSV para visualización posterior
df = pd.DataFrame(peliculas_validas)
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

# Exportar a Excel con hoja de resumen
with pd.ExcelWriter(OUTPUT_XLSX) as writer:
    df.to_excel(writer, sheet_name="Películas", index=False)
    resumen = pd.DataFrame({
        "Métrica": ["Media", "Mediana", "Moda", "Desviación"],
        "Valor": [media, mediana, moda, desviacion]
    })
    resumen.to_excel(writer, sheet_name="Estadísticas", index=False)

print(f"\nDatos exportados a:\n- {OUTPUT_CSV}\n- {OUTPUT_XLSX}")
