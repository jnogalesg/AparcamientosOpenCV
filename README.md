# Detección de plazas de aparcamiento con OpenCV

Proyecto de OpenCV para la **detección de plazas de aparcamiento ocupadas**: buscando **aparcamientos vacíos** y **plazas disponibles** a partir de una imagen o vídeo, y muestra cuántas plazas quedan **disponibles**, aplicado a zonas inteligentes en ciudades. 

## Autoría

Proyecto de la asignatura de Imagen Digital, GIIIS EPCC UEx - curso 26/27. 
**Autor:** Jose Nogales Gallardo.

## Funcionamiento

1. Se marcan las plazas usando el botón izquierdo del ratón (`1-marcar_plazas.py`), guardando el resultado en un archivo JSON, editable en todo momento ejecutando de nuevo.
2. Para cada fotograma (`2-detectar_plazas.py`):
   1. Se pasa a escala de grises y se suaviza.
   2. Se aplica un **umbral adaptativo**. Se busca el contraste entre un coche y sus detalles, con el asfalto vacío.
   3. Se limpia el ruido con erosión y dilatación.
   4. En cada plaza se calcula el **% de píxeles blancos**. Si supera un límite, la plaza se considera ocupada.
   5. Se dibuja cada plaza en verde (libre) o rojo (ocupada) y se muestra el contador `Libres: X / Total`.
3. El estado de una plaza solo cambia si el nuevo valor se repite varios fotogramas seguidos (5 por defecto).

## Archivos

| Archivo | Qué hace |
|---|---|
| `1-marcar_plazas.py` | Marca las plazas con el ratón sobre una imagen (o el primer fotograma de un vídeo) y las guarda en `plazas.json`. |
| `2-detectar_plazas.py` | Lee `plazas.json`, procesa la imagen o el vídeo y muestra plazas libres y ocupadas. |
| `plazas.json` | Plazas marcadas (se genera pulsando 's' con `1-marcar_plazas.py`). |
| `estado_aparcamiento.json` | Estado actual del aparcamiento (se genera pulsando 'g' con `2-detectar_plazas.py`). |

## Requisitos e instalación

Requiere Python, OpenCV y NumPy. 

Se recomienda crear un entorno virtual: 

``` bash
# creacion del entorno virtual
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\Activate.ps1  # Windows (PowerShell)

# instalar dependencias
pip install -r requirements.txt
```

## Uso

1. Pon un vídeo o una imagen la carpeta raíz del proyecto (o una carpeta designada para ello) y escribe su ruta en `fuente_imagen` (al principio de los dos scripts).
2. Marca las plazas, ejecutando `1-marcar_plazas.py`:
   ```bash
   python 1-marcar_plazas.py
   ```
   - Botón izquierdo (arrastrar): dibujar una plaza
   - Botón derecho (clic): borrar la plaza pulsada
   - `z`: deshacer · `s`: guardar · `q`: salir
3. Detecta las plazas, ejecutando `2-detectar_plazas.py`:
   ```bash
   python 2-detectar_plazas.py
   ```
   - Controles deslizantes `Limite %`, `Bloque` y `Constante`: ajustan la detección en tiempo de ejecución.
   - `g`: guarda el estado actual en `estado_aparcamiento.json`
   - `q`: salir

**Nota:** Al cambiar de imagen o de vídeo, hay que volver a marcar las plazas y ajustar las barras.

### Ejemplos incluidos
 
Los valores por defecto del código corresponden a la **foto**, así que se puede ejecutar directamente (`python 2-detectar_plazas.py`). Para probar el **vídeo**, cambia las dos variables en `2-detectar_plazas.py` y ajusta las barras a los valores recomendados:
 
| Ejemplo | `fuente_imagen` | `archivo_plazas` | Bloque | Constante | Límite % |
|---|---|---|---|---|---|
| Foto | `./ejemplo_foto/aparcamiento.jpg` | `./ejemplo_foto/plazas.json` | 25 | 20 | 15 |
| Vídeo | `./ejemplo_parking/parking.mp4` | `./ejemplo_parking/plazas-parking.json` | 25 | 5 | 32 |
 
### Barras deslizantes
 
| Barra | Qué controla |
|---|---|
| `Limite %` | Porcentaje de píxeles blancos de una plaza a partir del cual se considera ocupada. |
| `Bloque` | Tamaño de la zona que usa el umbral adaptativo para calcular el umbral de cada píxel (siempre impar, mínimo 3). |
| `Constante` | Sensibilidad del umbral adaptativo: cuanto más alta, menos detalle (ruido, sombras) se marca en blanco. |

## Principales funciones de OpenCV utilizadas

| Función | Para qué se usa en el proyecto |
|---|---|
| `cv2.imread` | Leer una imagen del disco. |
| `cv2.VideoCapture` (`read`, `release`, `set`, `get`, `isOpened`) | Abrir un vídeo, leerlo fotograma a fotograma, obtener sus fps y volver al principio al terminar. |
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
 
- Hay que ajustar los parámetros para cada aparcamiento y para cada condición de luz: los valores de la foto no sirven para el vídeo, y viceversa.
- Las sombras, las líneas pintadas o las texturas del suelo pueden contarse como "detalle" y dar falsos ocupados.
- Los coches oscuros o con poca luz tienen poco contraste y pueden darse por libres, por ejemplo al anochecer en el vídeo.
- Se usa un único límite para todas las plazas, y los objetos que no son coches aparcados pueden confundir la detección.
- La cámara debe estar fija: si se mueve, las plazas marcadas dejan de coincidir.

## Posibles mejoras
 
- Usar un límite distinto para cada plaza, calibrado con una imagen de la plaza vacía.
- Restar una imagen de fondo (con el aparcamiento vacío) para detectar los cambios.
- Guardar los parámetros (bloque, constante y límite) junto a las plazas en el JSON, para que cada ejemplo arranque ya ajustado.
- Pasar la imagen o el vídeo y el JSON como argumentos al ejecutar, en lugar de editar los scripts.
- Corregir la perspectiva con `cv2.warpPerspective` para plazas vistas en ángulo.
- Detectar coches con un modelo de aprendizaje automático (por ejemplo, YOLO) en lugar de umbrales.
- Enviar el estado (`estado_aparcamiento.json`) a una plataforma de ciudad inteligente.

