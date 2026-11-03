"""
PROYECTO OPENCV PARKING - Parte 1: MARCAR LAS PLAZAS DE APARCAMIENTO

Se muestra una imagen (o el primer fotograma de un vídeo) del aparcamiento.
Cada plaza se dibuja arrastrando con el botón izquierdo del ratón.

    Botón izquierdo (arrastrar) -> dibujar una plaza
    Botón derecho (clic)        -> borrar la plaza sobre la que se hace clic
    z -> deshacer la última plaza
    s -> guardar las plazas en el archivo
    q -> salir
"""

import cv2
import json
import os

# fuente_imagen - ruta al vídeo (.mp4...) o imagen (.jpg, .png)
# archivo_plazas - ruta al archivo JSON donde se guardarán las plazas creadas sobre la imagen/video
fuente_imagen = './ejemplo_foto/parking.mp4' 
archivo_plazas = './ejemplo_foto/plazas-parking.json'  

color_plaza = (0, 255, 0)   # color de las plazas (verde)
color_nueva = (0, 255, 255) # color de la plaza mientras se dibuja el contorno (amarillo)
color_texto = (255, 255, 255)   # color del texto (rojo)
grosor = 2
fuente = cv2.FONT_HERSHEY_SIMPLEX
escala = 0.5

ancho_min = 15  # tamaño mínimo de una plaza 
alto_min = 15   

plazas = []  # cada plaza es una lista [x, y, ancho, alto]
x1 = y1 = 0
dibujando = False


def cargar_imagen(ruta):
    # Si es una imagen se lee directamente
    if ruta.lower().endswith((".jpg", ".jpeg", ".png")):
        return cv2.imread(ruta)
    
    # Si es un vídeo, se coge el primer fotograma
    video = cv2.VideoCapture(ruta)
    ret, frame = video.read()
    video.release()

    if ret: 
        return frame
    else:
        return None


def dibujarPlazas(nueva=None):
    img = img_original.copy()

    for i, (x, y, ancho, alto) in enumerate(plazas):
        cv2.rectangle(img, (x, y), (x + ancho, y + alto), color_plaza, grosor)
        cv2.putText(img, str(i + 1), (x + 3, y + 15), fuente, escala, color_plaza, 1)

    if nueva is not None:
        cv2.rectangle(img, nueva[0], nueva[1], color_nueva, grosor)

    cv2.putText(img, "Plazas: " + str(len(plazas)), (10, 25), fuente, 0.8, color_texto, 2)
    cv2.imshow('Marcar plazas', img)


def eventos_raton(evento, x, y, flags, parametros):
    global x1, y1, dibujando

    # Se dibuja un rectángulo mientras se arrastra el ratón con el botón izquierdo pulsado
    if evento == cv2.EVENT_LBUTTONDOWN:
        x1, y1 = x, y
        dibujando = True

    elif evento == cv2.EVENT_MOUSEMOVE and dibujando:
        dibujarPlazas(((x1, y1), (x, y)))  # vista previa del rectángulo mientras se arrastra

    elif evento == cv2.EVENT_LBUTTONUP:
        dibujando = False

        # Se ordenan las coordenadas por si se ha arrastrado hacia arriba o hacia la izquierda
        x_ini, x_fin = min(x1, x), max(x1, x)
        y_ini, y_fin = min(y1, y), max(y1, y)

        if x_fin - x_ini >= ancho_min and y_fin - y_ini >= alto_min:
            plazas.append([x_ini, y_ini, x_fin - x_ini, y_fin - y_ini])

        dibujarPlazas()

    elif evento == cv2.EVENT_RBUTTONDOWN:
        # Se borra la última plaza (la más reciente) que contenga el punto pulsado
        for i in range(len(plazas) - 1, -1, -1):
            px, py, pancho, palto = plazas[i]

            if px <= x <= px + pancho and py <= y <= py + palto:
                plazas.pop(i)
                break

        dibujarPlazas()


img_original = cargar_imagen(fuente_imagen)

if img_original is None:
    print("No es posible abrir", fuente_imagen)
    exit()

alto_img, ancho_img = img_original.shape[:2]

# Si ya existe un archivo de plazas se carga para poder seguir editándolo
if os.path.exists(archivo_plazas):
    with open(archivo_plazas, 'r') as archivo:
        plazas = json.load(archivo)["plazas"]

    print("Se han cargado", len(plazas), "plazas de", archivo_plazas)

cv2.namedWindow('Marcar plazas')
cv2.setMouseCallback('Marcar plazas', eventos_raton)
dibujarPlazas()

while True:
    tecla = cv2.waitKey(0) & 0xFF

    if tecla == ord('z') and len(plazas) > 0:
        plazas.pop()
        dibujarPlazas()

    elif tecla == ord('s'): # guardar las plazas en un archivo json y cerrar la aplicación
        # Se guarda también la resolución para poder reescalar si el vídeo cambia de tamaño
        datos = {"resolucion": [ancho_img, alto_img], "plazas": plazas}

        with open(archivo_plazas, 'w') as archivo:
            json.dump(datos, archivo)

        print("Guardadas", len(plazas), "plazas en", archivo_plazas)

    elif tecla == ord('q'): # salir pulsando la letra "q" en cualquier momento
        break

cv2.destroyAllWindows()
