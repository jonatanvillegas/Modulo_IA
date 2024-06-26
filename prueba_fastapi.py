from g4f.client import AsyncClient
import json
from fastapi import FastAPI

app = FastAPI()
client = AsyncClient()

model = "gpt-3.5-turbo"


# Mensaje inicial que describe la tarea
mensaje_inicial = {
    "role": "system",
    "content": "Eres una IA capaz de seleccionar el contenido del curso, crear títulos de capitulos relevantes y encontrar videos de YouTube relevantes para cada capítulo generaras como minimo 5 unidades, mas las unidades extra que el usuario proporciones y generaras sus capitulos, si el usuario no proporciona unidades extra no importara."
}


async def generar_json(respuesta):
    unidades = []
    unidad_actual = None
    capitulos = []

    lineas = respuesta.split("\n")

    for linea in lineas:
        if "Unidad" in linea:
            if unidad_actual:
                unidad_actual["capitulos"] = capitulos
                unidades.append(unidad_actual)
                capitulos = []

            unidad_actual = {"unidad": linea.split(
                ":")[1].strip(), "capitulos": []}
        elif "Capítulo" in linea:
            capitulo = {
                "capitulo": linea.split(":")[1].strip(),
                "youtube_search_query": ""
            }
            capitulos.append(capitulo)
        elif "youtube_search_query" in linea:
            capitulos[-1]["youtube_search_query"] = linea.split(":")[1].strip()

    # Agregar la última unidad
    if unidad_actual:
        unidad_actual["capitulos"] = capitulos
        unidades.append(unidad_actual)

    return unidades


@app.post("/create")
async def prueba(title: str):  # Modificamos la firma de la función para aceptar el parámetro curso
    mensaje_usuario = {
        "role": "user",
        "content": f"""Genera un índice para un curso sobre {title} genera las unidades y el nombre de la busqueda para youtube, no generes descripcion :

        Para cada unidad, incluye un máximo de 4 capitulos con una breve descripción de su contenido.

        **Formato de salida:**

        * Lista de unidades con sus capítulos.
        * Descripción de cada capítulo en una sola línea.

        **Ejemplo de salida:**

        **Unidad 1: nombre de la unidad**

        * **Capitulo 1:** nombre del capitulo resumido
        * **youtube_search_query:** nombre del video
        * **Capitulo 2:** nombre del capitulo resumido
        * **youtube_search_query:** nombre del video
        * **Capitulo 3:** Enombre del capitulo resumido
        * **youtube_search_query:** nombre del video

        **Unidad 2: nombre de la unidad**

        * **Capitulo 4:**  nombre del capitulo resumido
        * **youtube_search_query:** nombre del video
        * **Capitulo 5:**  nombre del capitulo resumido
        * **youtube_search_query:** nombre del video

        **...**

        **Nota:**

        No incluyas ejemplos específicos ni consultas de búsqueda en YouTube en la descripción de los capitulos.""",
    }

    respuesta =  client.chat.completions.create(
        model=model,
        messages=[
            mensaje_inicial,
            mensaje_usuario
        ]
    )

     

    return respuesta.choices[0].message.content