"""
PROYECTO OPENCV PARKING - Parte 2: DETECCIÓN DE PLAZAS OCUPADAS Y LIBRES

Lee las plazas marcadas con 1-marcar_plazas.py y, para cada fotograma:
  1) Pasa a blanco y negro y suaviza
  2) Aplica un umbral adaptativo para comprobar si la plaza está libre u ocupada.
  Se busca el contraste entre un coche y sus detalles, con el asfalto vacío.
  3) Limpia el ruido con erosión y dilatación 
  4) En cada plaza se calcula el % de píxeles blancos (porcentaje de posibilidad de que haya un coche)
  5) Si supera el límite la plaza está OCUPADA (rojo). 
        si no lo supera, se etiquta la plaza como LIBRE (verde)

    q -> salir
    g -> guardar el estado actual del aparcamiento en un JSON
"""

import cv2
import json
import numpy as np

# fuente_imagen - ruta al vídeo (.mp4...) o imagen (.jpg, .png)
# archivo_plazas - ruta al archivo JSON donde se guardarán las plazas creadas sobre la imagen/video
# archivo_estado - ruta al archivo JSON donde se guardará el estado del aparcamiento (si se pulsa "g")
fuente_imagen = './ejemplo_foto/parking.mp4' 
archivo_plazas = './ejemplo_foto/plazas-parking.json'  
archivo_estado = './estado_aparcamiento.json'

# colores de las plazas
color_libre = (0, 200, 0)       # plaza libre (verde)
color_ocupada = (0, 0, 255)     # plaza ocupada (rojo)
color_texto = (255, 255, 255)   # texto (blanco)
grosor = 2
fuente = cv2.FONT_HERSHEY_SIMPLEX
escala = 0.5

bloque = 25               # vecindario (umbral adaptativo)
constante = 20            # ajuste del umbral local; subirlo ignora más ruido/sombras
limite_ocupacion = 15     # % de píxeles blancos a partir del cual la plaza está ocupada
fotogramas_confirmar = 5  # fotogramas seguidos necesarios para cambiar el estado de una plaza
kernel = np.ones((3, 3), np.uint8)

def actualizar_bloque(valor):
    global bloque
    bloque = valor

    # El tamaño del bloque debe ser impar y como mínimo 3 
    if bloque < 3: bloque = 3
    elif bloque % 2 == 0: bloque += 1

def actualizar_constante(valor):
    global constante
    constante = valor

def actualizar_limite(valor):
    global limite_ocupacion
    limite_ocupacion = valor

def procesar(frame):
    img_byn = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_suavizada = cv2.blur(img_byn, (3, 3))
    img_umbral = cv2.adaptiveThreshold(img_suavizada, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, bloque, constante)

    # Erosion y dilatación para quitar el ruido de la imagen umbral, uniendo los trozos cercanos
    img_umbral = cv2.erode(img_umbral, kernel)
    img_umbral = cv2.dilate(img_umbral, kernel, iterations=2)
    return img_umbral

def es_imagen(ruta):
    return ruta.lower().endswith((".jpg", ".jpeg", ".png"))

# --- Se cargan las plazas marcadas ---
try:
    with open(archivo_plazas, 'r') as archivo:
        datos = json.load(archivo)
except FileNotFoundError:
    print("No existe", archivo_plazas, "- ejecuta antes 1-marcar_plazas.py")
    exit()

plazas = datos["plazas"]
ancho_ref, alto_ref = datos["resolucion"]
num_plazas = len(plazas)

# --- Se abre la fuente (imagen o vídeo) ---
modo_imagen = es_imagen(fuente_imagen)
fps = 30

if modo_imagen:
    img_fija = cv2.imread(fuente_imagen)

    if img_fija is None:
        print("No es posible abrir la imagen")
        exit()
else:
    video = cv2.VideoCapture(fuente_imagen)

    if not video.isOpened():
        print("No es posible abrir el archivo de vídeo")
        exit()

    if video.get(cv2.CAP_PROP_FPS) > 0: fps = video.get(cv2.CAP_PROP_FPS)

velocidad_reproduccion = int(1000 / fps)

cv2.namedWindow('Aparcamiento')
cv2.createTrackbar('Limite %', 'Aparcamiento', limite_ocupacion, 100, actualizar_limite)
cv2.createTrackbar('Bloque', 'Aparcamiento', bloque, 99, actualizar_bloque)
cv2.createTrackbar('Constante', 'Aparcamiento', constante, 50, actualizar_constante)

estado = [False] * num_plazas    # True = ocupada
contador = [0] * num_plazas      # fotogramas seguidos que cambian el estado de la plaza
porcentajes = [0.0] * num_plazas
primer_fotograma = True

while True:
    if modo_imagen:
        frame = img_fija.copy()
    else:
        ret, frame = video.read()

        if not ret:
            print("Reproducción finalizada")
            break

    # Si el vídeo no tiene la misma resolución que la imagen usada para marcar, se reescala
    if frame.shape[1] != ancho_ref or frame.shape[0] != alto_ref:
        frame = cv2.resize(frame, (ancho_ref, alto_ref))

    img_umbral = procesar(frame)

    for i, (x, y, ancho, alto) in enumerate(plazas):
        roi = img_umbral[y:y + alto, x:x + ancho]
        porcentajes[i] = cv2.countNonZero(roi) * 100 / (ancho * alto)
        ocupada = porcentajes[i] > limite_ocupacion

        # Para evitar parpadeos, el estado sólo cambia si el nuevo valor se repite varios fotogramas
        if primer_fotograma:
            estado[i] = ocupada
        elif ocupada != estado[i]:
            contador[i] += 1

            if contador[i] >= fotogramas_confirmar:
                estado[i] = ocupada
                contador[i] = 0
        else:
            contador[i] = 0

    primer_fotograma = False

    for i, (x, y, ancho, alto) in enumerate(plazas):
        if estado[i]: color = color_ocupada
        else: color = color_libre

        cv2.rectangle(frame, (x, y), (x + ancho, y + alto), color, grosor)
        cv2.putText(frame, str(int(porcentajes[i])) + "%", (x + 3, y + 15), fuente, escala, color, 1)

    num_ocupadas = sum(estado)
    num_libres = num_plazas - num_ocupadas

    # Panel con el contador, con fondo para que se lea bien sobre cualquier imagen
    cv2.rectangle(frame, (0, 0), (270, 35), (0, 0, 0), -1)
    cv2.putText(frame, "Libres: " + str(num_libres) + " / " + str(num_plazas), (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_texto, 2)

    cv2.imshow('Aparcamiento', frame)
    cv2.imshow('Umbral', img_umbral)

    tecla = cv2.waitKey(velocidad_reproduccion) & 0xFF

    if tecla == ord('q'):
        break

    elif tecla == ord('g'):
        # Estado en formato JSON, como lo enviaría un sensor a una plataforma de ciudad inteligente
        resumen = {"total": num_plazas, "libres": num_libres, "ocupadas": num_ocupadas,
                   "plazas": [{"id": i + 1, "ocupada": bool(estado[i])} for i in range(num_plazas)]}

        with open(archivo_estado, 'w') as archivo:
            json.dump(resumen, archivo, indent=2)

        print("Estado guardado en", archivo_estado)

if not modo_imagen:
    video.release()

cv2.destroyAllWindows()