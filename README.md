# Detección de plazas de aparcamiento con OpenCV

Proyecto de OpenCV para la **Detección de plazas de aparcamiento ocupadas**: buscando **aparcamientos vacíos** y **plazas disponibles** a partir de una imagen o video, y muestra cuántas plazas quedan **disponibles**, aplicado a zonas inteligentes en ciudades. 

## Autoría

Proyecto de la asignatura de Imagen Digital, GIIIS EPCC UEx - curso 26/27. 
**Autor:** Jose Nogales Gallardo.

## Cómo funciona

1. Se marcan las plazas una sola vez con el ratón (`marcar-plazas.py`).
2. Para cada fotograma (`detectar-plazas.py`):
   1. Se pasa a escala de grises y se suaviza.
   2. Se aplica un **umbral adaptativo**: un coche tiene mucho detalle (ventanas, ruedas, bordes) y el asfalto vacío es uniforme.
   3. Se limpia el ruido con erosión y dilatación.
   4. En cada plaza se calcula el **% de píxeles blancos**. Si supera un límite, la plaza está ocupada.
   5. Se dibuja cada plaza en verde (libre) o rojo (ocupada) y se muestra el contador `Libres: X / Total`.
3. Para evitar parpadeos, el estado de una plaza solo cambia si el nuevo valor se repite varios fotogramas seguidos.

## Archivos

| Archivo | Qué hace |
|---|---|
| `1-marcar_plazas.py` | Marca las plazas con el ratón sobre una imagen (o el primer fotograma de un vídeo) y las guarda en `plazas.json`. |
| `2-detectar_plazas.py` | Lee `plazas.json`, procesa la imagen o el vídeo y muestra plazas libres y ocupadas. |
| `plazas.json` | Plazas marcadas (se genera con `marcar_plazas.py`). |

## Requisitos e instalación

Python 3, OpenCV y NumPy. Se recomienda crear un entorno virtual: 

```
pip install -r requirements.txt
```

## Uso

1. Pon un vídeo o una imagen en `./videos/` y escribe su ruta en `fuente_imagen` (al principio de los dos scripts).
2. Marca las plazas:
   ```
   python marcar-plazas.py
   ```
   - Botón izquierdo (arrastrar): dibujar una plaza
   - Botón derecho (clic): borrar la plaza pulsada
   - `z`: deshacer · `s`: guardar · `q`: salir
   - Consejo: marca el interior de la plaza, sin incluir las líneas pintadas.
3. Detecta las plazas:
   ```
   python detectar-plazas.py
   ```
   - Barras `Limite %`, `Bloque` y `Constante`: ajustan la detección en directo
   - `g`: guarda el estado actual en `estado_aparcamiento.json`
   - `q`: salir

Si cambias de vídeo o de cámara, hay que volver a marcar las plazas y ajustar las barras.

## Principales funciones de OpenCV utilizadas

| Función | Para qué se usa en el proyecto |
|---|---|
| `cv2.imread` | Leer una imagen del disco. |
| `cv2.VideoCapture` (`read`, `release`, `get`, `isOpened`) | Abrir un vídeo, leerlo fotograma a fotograma y obtener sus fps. |
| `cv2.cvtColor(..., COLOR_BGR2GRAY)` | Pasar el fotograma a escala de grises. |
| `cv2.blur` | Suavizar la imagen para reducir el ruido. |
| `cv2.adaptiveThreshold` | Umbral que se calcula por zonas, para marcar los bordes y detalles de los coches aunque cambie la iluminación. |
| `cv2.erode` / `cv2.dilate` | Eliminar puntos sueltos y unir zonas cercanas tras el umbral. |
| `cv2.countNonZero` | Contar los píxeles blancos dentro de cada plaza. |
| `cv2.resize` | Reescalar el fotograma si no tiene el tamaño de la imagen usada para marcar las plazas. |
| `cv2.rectangle` / `cv2.putText` | Dibujar las plazas, los porcentajes y el contador sobre la imagen. |
| `cv2.setMouseCallback` | Controlar el ratón para dibujar y borrar las plazas. |
| `cv2.createTrackbar` | Barras para ajustar los parámetros de detección en directo. |
| `cv2.imshow` / `cv2.waitKey` / `cv2.namedWindow` / `cv2.destroyAllWindows` | Mostrar las ventanas y leer las teclas. |

Además se usa `numpy` (`np.ones`) para crear el kernel de la erosión y la dilatación.

## Limitaciones

- Hay que ajustar los parámetros para cada aparcamiento y para cada condición de luz.
- Las sombras, las líneas pintadas o las texturas del suelo (adoquines, hierba) pueden contarse como "detalle" y dar falsos ocupados.
- La cámara debe estar fija: si se mueve, las plazas marcadas dejan de coincidir.

## Posibles mejoras

- Corregir la perspectiva con `cv2.warpPerspective` para plazas vistas en ángulo.
- Detectar coches con un modelo de aprendizaje automático (por ejemplo, YOLO) en lugar de umbrales.
- Enviar el estado (`estado_aparcamiento.json`) a una plataforma de ciudad inteligente.


