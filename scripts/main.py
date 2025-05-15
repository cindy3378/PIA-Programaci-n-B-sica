from utils import obtener_datos_peliculas, generar_graficas, guardar_en_excel

def main():
    datos = obtener_datos_peliculas()
    if datos is not None:
        generar_graficas(datos)
        guardar_en_excel(datos)

if __name__ == "__main__":
    main()
