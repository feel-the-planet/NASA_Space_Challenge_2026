"""
EARTH JUKEBOX - Mapa tactil inclusivo (version 2.3.8)
Detecta el dedo indice sobre el mapa fisico impreso en 3D, DICE EN VOZ ALTA el
lugar que se toca y SONIFICA datos reales de la NASA en ese punto.

Novedades 2.3.8 (basada en la 2.3.5)
  - 17 puntos de ajuste fino (nuevos: Los Angeles, Tres Fronteras
    Peru-Colombia-Brasil, norte de Groenlandia, Cabo Norte y Cabo Chelyuskin).
    Ver guia_puntos_calibracion.png.
  - Al calibrar ya no se dibuja el mapa guia encima de la camara: solo se ven
    las esquinas y los puntos (la guia se sigue usando por dentro; tecla m la muestra).
  - El mapa pequeno con el punto a marcar va en un margen a la derecha, fuera de
    la imagen de la camara (ya no tapa Oceania al calibrar).

Novedades 2.3.5
  - IDIOMA: el principal es el INGLES (voz e interfaz). Con la tecla L se cambia
    a ESPANOL y otra vez a ingles en cualquier momento. Para empezar en espanol
    pon IDIOMA = 'es' arriba en la configuracion.
      * Voz en ingles: en-US-JennyNeural, voz en espanol: es-MX-DaliaNeural
        (edge-tts; los audios en ingles se guardan en "voz" con prefijo en_).
      * Sin internet usa la voz de Windows del idioma elegido (si esta instalada).

Novedades 2.3.4
  - Variable 3 ahora es la ALTITUD del terreno sobre el nivel del mar (NASA ASTER
    GDEM), el relieve que esta impreso en 3D. Flauta: llano/costa = grave,
    montana = agudo (0 a 4500 m). En el mar no hay dato (suena bajito).
    La primera vez necesita internet para descargarla (queda en datos_nasa).
  - Interfaz nitida: el programa le avisa a Windows que dibuje a la resolucion
    real de la pantalla (sin el escalado que la hacia ver borrosa) y los textos
    se dibujan con la fuente Segoe UI de Windows (con acentos) si hay Pillow.
  - Carpeta limpia: todo lo necesario esta directo en esta carpeta.

Novedades 2.3.2
  - Sonido CONTINUO (prioridad): mientras el dedo esta en el mapa suena una nota
    sostenida que sube y baja en tiempo real con el dato (grave = valor bajo,
    agudo = valor alto). La voz dice el lugar ENCIMA del sonido, que solo baja
    un poco de volumen mientras habla, pero no se corta.
        1 = CO2            -> organo grave       (mas CO2 = mas agudo)
        2 = Temperatura    -> trompeta           (frio = grave, calor = agudo)
        3 = Altitud        -> flauta con oleaje  (bajo = grave, montana = agudo)
  - Al elegir variable suena un barrido de grave a agudo con su instrumento.
  - Camara: se abre como en el programa de la banda (MSMF/DSHOW), imagen
    horizontal que cubre el recuadro del mapa (ROTAR / LLENAR, tecla t).

Novedades 2.1
  - Voz: dice el nombre del continente / oceano al tocarlo.
      * Voz neuronal "es-MX-DaliaNeural" (edge-tts, necesita internet la 1a vez;
        los audios se guardan en la carpeta "voz" y despues funcionan sin internet).
      * Si no hay internet ni edge-tts, usa la voz en espanol de Windows (pyttsx3).
  - 3 variables de datos NASA (imagenes reales de NASA GIBS / Worldview):
        1 = CO2            (AIRS, Aqua)            -> sonido grave y denso
        2 = Temperatura    (MERRA-2, aire a 2 m)   -> sonido de campana
        3 = Nivel del mar  (JPL MEaSUREs, anomalia) -> sonido de ola
    Al pulsar la tecla, la voz dice la variable y suena su tono. Al tocar el
    mapa, la ALTURA de la nota depende del valor del dato en ese punto
    (escala pentatonica: grave = valor bajo, agudo = valor alto).
  - Interfaz con margen: el mapa (48 x 29 cm) queda centrado y toda la
    informacion se muestra en los margenes, sin taparlo.

Requisitos:   pip install opencv-python numpy mediapipe pygame edge-tts pyttsx3

PRIMER USO (calibracion, solo una vez o si mueves la camara / el mapa):
  1. Fija la camara de modo que vea TODO el mapa (lo ideal: desde arriba).
  2. Haz clic en las 4 esquinas del mapa en orden: sup-izq, sup-der, inf-der, inf-izq
     ("arriba" = el lado del Polo Norte).
  3. Aparece el mapa virtual encima como guia: arrastra las esquinas hasta que
     los continentes coincidan con los del mapa impreso.
  4. AJUSTE FINO (recomendado): pulsa p y marca los puntos que pide el programa
     (clic, o punta del dedo + ESPACIO).
  5. Pulsa ENTER para guardar.

Teclas (modo uso):
   1 / 2 / 3 = CO2 / Temperatura / Altitud            i = decir lugar y valor
   s = silencio (voz y tonos)     v = vista: camara / datos NASA / mezcla
   g = globo enfoca el dedo       d = ver regiones encima (depurar)
   c = calibrar                   q / ESC = salir
   L = cambiar idioma (English / Espanol)
   t = rotar camara 90 grados (despues recalibra con c)
  En calibracion: r = reiniciar, m = ver/ocultar guia, 1-4 = elegir esquina,
                  i/j/k/l = mover esquina 1 pixel, ENTER = guardar
                  p = ajuste fino por puntos (clic o ESPACIO = marcar,
                      n/b = siguiente/anterior, x = borrar punto, z = borrar todos)
"""

import os
import sys
import cv2
import numpy as np

import time
import urllib.request

# Pantalla nitida en Windows: sin esto, con el escalado de pantalla (125 %, 150 %)
# Windows estira la ventana de OpenCV y los textos se ven borrosos.
if sys.platform.startswith('win'):
    try:
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)      # por monitor
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

try:
    import mediapipe as mp
    MP_OK = True
except ImportError:
    MP_OK = False

MODELO_URL = ('https://storage.googleapis.com/mediapipe-models/hand_landmarker/'
              'hand_landmarker/float16/1/hand_landmarker.task')

# --- Idioma -------------------------------------------------------------------
IDIOMA = 'en'      # 'en' = English (principal)   'es' = Espanol   (tecla L cambia)
VOCES_EDGE = {'en': 'en-US-JennyNeural', 'es': 'es-MX-DaliaNeural'}


def T(es, en):
    """Texto segun el idioma actual."""
    return en if IDIOMA == 'en' else es


def cambiar_idioma():
    global IDIOMA
    IDIOMA = 'es' if IDIOMA == 'en' else 'en'
    print('Idioma / Language:', 'Espanol' if IDIOMA == 'es' else 'English')


ANCHO, ALTO = 1280, 720
REF_W, REF_H = 1500, 844          # tamano de mapa.jpg al que corresponden los poligonos

# ----------------------------------------------------------------------------
# REGIONES (poligonos en pixeles del mapa original 1500x844).
# Se evalua en orden: el primero que contiene al pixel gana.
# Para el mapa impreso en 3D solo tendras que recalibrar estos puntos.
# ----------------------------------------------------------------------------
TIERRA = [
    ('Groenlandia',       [(515,70),(680,70),(680,135),(615,138),(600,195),(515,195)]),
    ('Centroamerica y Caribe', [(305,395),(335,380),(440,376),(440,420),(385,448),(350,440),(325,420)]),
    ('Sudamerica',        [(340,428),(440,420),(570,490),(570,800),(380,800),(335,520)]),
    ('Norteamerica',      [(0,0),(660,0),(660,376),(440,376),(335,380),(305,395),(292,440),(0,440)]),
    ('Oceania',           [(1235,470),(1500,470),(1500,844),(1130,844),(1130,548),(1240,548)]),
    ('Europa',            [(630,0),(895,0),(895,170),(866,226),(840,252),(800,262),(790,300),(700,312),(630,312)]),
    ('Africa',            [(600,290),(838,290),(850,350),(880,425),(960,445),(960,844),(600,844)]),
    ('Asia',              [(0,0),(1500,0),(1500,844),(0,844)]),
]
AGUA = [
    ('Oceano Artico',        [(0,0),(1500,0),(1500,100),(1300,125),(1000,92),(790,95),(700,110),(560,62),(480,62),(380,95),(250,100),(150,135),(0,150)]),
    ('Bahia de Hudson',      [(380,155),(455,155),(455,225),(380,225)]),
    ('Grandes Lagos',        [(355,226),(445,226),(445,262),(355,262)]),
    ('Mar Negro',            [(795,228),(865,228),(865,280),(795,280)]),
    ('Mar Caspio',           [(866,225),(925,225),(925,300),(866,300)]),
    ('Golfo de Mexico',      [(285,325),(372,325),(372,372),(335,390),(290,390)]),
    ('Mar Caribe',           [(335,372),(440,372),(440,425),(385,450),(350,440),(325,415)]),
    ('Mar Mediterraneo',     [(670,285),(850,285),(850,345),(780,335),(700,318)]),
    ('Mar Rojo',             [(838,345),(870,345),(900,425),(885,432),(868,420)]),
    ('Golfo Persico',        [(885,335),(950,335),(950,385),(900,385)]),
    ('Golfo de Bengala',     [(1000,335),(1100,335),(1100,430),(1000,430)]),
    ('Mar de China Meridional', [(1150,330),(1195,330),(1195,455),(1150,455)]),
    ('Oceano Indico',        [(885,385),(1000,385),(1130,430),(1130,548),(1230,548),(1230,844),(775,844),(775,610)]),
    ('Oceano Atlantico Norte', [(380,105),(700,105),(700,300),(640,395),(440,430),(440,376),(372,376),(372,325),(440,200)]),
    ('Oceano Atlantico Sur', [(420,440),(790,430),(790,844),(455,844),(445,600)]),
    ('Oceano Pacifico',      [(0,100),(290,100),(290,440),(420,440),(445,600),(455,844),(0,844)]),
    ('Oceano Pacifico',      [(1130,100),(1500,100),(1500,844),(1130,844)]),
]

# Datos que se muestran (puedes ajustarlos / agregar CO2, lluvia, etc.)


# ----------------------------------------------------------------------------
# MAPA DE ETIQUETAS: cada pixel del mapa -> id de region (se calcula una sola vez)
# ----------------------------------------------------------------------------
def cargar_mapa():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    for ruta in (os.path.join(carpeta, 'mapa.jpg'), 'mapa.jpg',
                 r'C:\Users\janto\OneDrive\Desktop\Hackatec\mapa.jpg'):
        img = cv2.imread(ruta)
        if img is not None:
            return cv2.resize(img, (ANCHO, ALTO))
    print('Error: no se encontro mapa.jpg'); exit()


def construir_etiquetas(mapa):
    # 1) tierra vs agua a partir del color azul (se cierran las lineas blancas de fronteras)
    hsv = cv2.cvtColor(mapa, cv2.COLOR_BGR2HSV)
    tierra = cv2.inRange(hsv, np.array([90, 40, 40]), np.array([130, 255, 255]))
    tierra = cv2.morphologyEx(tierra, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)) > 0

    nombres = []
    def id_de(n):
        if n not in nombres: nombres.append(n)
        return nombres.index(n)

    sx, sy = ANCHO / REF_W, ALTO / REF_H
    def pintar(lista):
        out = np.full((ALTO, ANCHO), -1, np.int16)
        for nombre, pts in reversed(lista):            # al reves: el primero queda encima
            poly = np.array([(int(x*sx), int(y*sy)) for x, y in pts], np.int32)
            cv2.fillPoly(out, [poly], id_de(nombre))
        return out

    etq_tierra, etq_agua = pintar(TIERRA), pintar(AGUA)
    id_lagos = id_de('Aguas interiores / Mar')
    etq_agua[etq_agua < 0] = id_lagos
    etq_tierra[etq_tierra < 0] = id_de('Asia')
    etiquetas = np.where(tierra, etq_tierra, etq_agua).astype(np.int16)
    return etiquetas, nombres, tierra

# ----------------------------------------------------------------------------
# DETECCION DEL DEDO INDICE
# ----------------------------------------------------------------------------
class DetectorIndice:
    def __init__(self):
        self.modo = 'color'
        self.hands = None
        self.landmarker = None
        self.t0 = time.time()
        self.suave = {}
        if MP_OK:
            try:
                if hasattr(mp, 'solutions'):                      # API clasica
                    self.hands = mp.solutions.hands.Hands(
                        max_num_hands=2, model_complexity=0,
                        min_detection_confidence=0.6, min_tracking_confidence=0.5)
                    self.modo = 'mediapipe-solutions'
                else:                                             # API nueva (Tasks)
                    from mediapipe.tasks import python as mpp
                    from mediapipe.tasks.python import vision
                    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        'hand_landmarker.task')
                    if not os.path.exists(ruta):
                        print('Descargando modelo de manos (solo la primera vez)...')
                        urllib.request.urlretrieve(MODELO_URL, ruta)
                    opciones = vision.HandLandmarkerOptions(
                        base_options=mpp.BaseOptions(model_asset_path=ruta),
                        running_mode=vision.RunningMode.VIDEO, num_hands=2,
                        min_hand_detection_confidence=0.6,
                        min_tracking_confidence=0.5)
                    self.landmarker = vision.HandLandmarker.create_from_options(opciones)
                    self.modo = 'mediapipe-tasks'
            except Exception as e:
                print('No se pudo iniciar MediaPipe:', e)
                self.modo = 'color'
        # Respaldo por color (marcador verde en el dedo / guante)
        self.low, self.high = np.array([35, 100, 100]), np.array([85, 255, 255])

    def _suavizar(self, i, x, y):
        px, py = self.suave.get(i, (x, y))
        x, y = 0.6*px + 0.4*x, 0.6*py + 0.4*y
        self.suave[i] = (x, y)
        return int(x), int(y)

    def puntas(self, frame):
        """Devuelve lista de (x, y) de las puntas de dedo indice."""
        h, w = frame.shape[:2]
        res = []
        if self.modo == 'mediapipe-solutions':
            r = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            manos = [hl.landmark for hl in (r.multi_hand_landmarks or [])]
        elif self.modo == 'mediapipe-tasks':
            rgb = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            r = self.landmarker.detect_for_video(img, int((time.time()-self.t0)*1000))
            manos = r.hand_landmarks
        else:
            manos = None

        if manos is not None:
            if not manos:
                self.suave.clear()
            for i, lms in enumerate(manos):
                lm = lms[8]                                       # 8 = punta del indice
                res.append(self._suavizar(i, lm.x * w, lm.y * h))
        else:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            m = cv2.inRange(hsv, self.low, self.high)
            k = np.ones((5, 5), np.uint8)
            m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_OPEN, k), cv2.MORPH_CLOSE, k)
            cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if cs:
                c = max(cs, key=cv2.contourArea)
                if cv2.contourArea(c) > 400:
                    M = cv2.moments(c)
                    res.append((int(M['m10']/M['m00']), int(M['m01']/M['m00'])))
        return res

# ----------------------------------------------------------------------------
# GLOBO TERRAQUEO 3D GIRATORIO (se dibuja con OpenCV, sin librerias extra)
# ----------------------------------------------------------------------------
GLOBO_CX, GLOBO_CY, GLOBO_R = 170, 840, 135     # en el margen izquierdo del lienzo
GLOBO_VEL = 0.5                                  # velocidad de giro (rad/s)
GLOBO_ENFOQUE = 6.0          # rapidez con la que el globo gira hacia el dedo (mas = mas rapido)
GLOBO_ESPERA = 0.6           # segundos sin mano antes de volver a girar solo
INCLINACION = np.radians(23.5)                   # inclinacion del eje terrestre

# Calibracion mapa plano <-> longitud/latitud (en pixeles del mapa original 1500x844).
# Si el punto del globo no coincide con el del mapa, ajusta estos 4 numeros.
X_OESTE, X_ESTE = 20, 1388       # x donde estan -180 y +180 grados de longitud
LAT_ARRIBA, LAT_ABAJO = 96.0, -68.0   # latitud en el borde superior e inferior del mapa
U0, U1 = X_OESTE / REF_W, X_ESTE / REF_W


class Globo:
    def __init__(self, tierra, etiquetas, cx, cy, r):
        self.tex = np.zeros((ALTO, ANCHO, 3), np.uint8)
        self.tex[:] = (120, 55, 15)                  # oceano (BGR)
        self.tex[tierra] = (75, 165, 85)             # tierra
        self.etq, self.cx, self.cy, self.r = etiquetas, cx, cy, r
        n = 2 * r
        ys, xs = np.mgrid[0:n, 0:n]
        sx = (xs - r + 0.5) / r
        sy = -(ys - r + 0.5) / r
        d2 = sx**2 + sy**2
        self.mask = d2 <= 1
        sz = np.sqrt(np.clip(1 - d2, 0, 1))
        self.sx, self.sy, self.sz = sx, sy, sz
        self.shade = (0.35 + 0.65 * sz)[..., None]   # sombreado de esfera
        self.theta, self.t_ant = 0.0, time.time()
        self.seguir = True           # True = el globo se detiene y enfoca el punto senalado
        self.incl = INCLINACION      # inclinacion actual (cambia al enfocar una latitud)
        self.ult_lonlat, self.t_ult = None, 0.0
        self._calcular_esfera()

    def _calcular_esfera(self):
        c, s = np.cos(self.incl), np.sin(self.incl)
        wy = self.sy*c - self.sz*s                   # inclinar el eje
        wz = self.sy*s + self.sz*c
        self.lat = np.arcsin(np.clip(wy, -1, 1))
        self.lon0 = np.arctan2(self.sx, wz)

    @staticmethod
    def _envolver(a):
        return (a + np.pi) % (2*np.pi) - np.pi

    def _punto_a_lonlat(self, x, y):
        u, v = x / ANCHO, y / ALTO
        lon = self._envolver(((u - U0) / (U1 - U0) - 0.5) * 2*np.pi)
        lat = np.radians(LAT_ARRIBA - (LAT_ARRIBA - LAT_ABAJO) * v)
        return lon, float(np.clip(lat, -np.pi/2, np.pi/2))

    def dibujar(self, vis, punto, rid):
        ahora = time.time(); dt, self.t_ant = ahora - self.t_ant, ahora
        lonm = latm = None
        if punto is not None:
            lonm, latm = self._punto_a_lonlat(*punto)
        # Si la mano desaparece un instante, se mantiene el ultimo punto un momento
        if lonm is not None:
            self.ult_lonlat, self.t_ult = (lonm, latm), ahora
        elif self.ult_lonlat is not None and ahora - self.t_ult < GLOBO_ESPERA:
            lonm, latm = self.ult_lonlat

        k = 1 - np.exp(-GLOBO_ENFOQUE * dt)          # suavizado independiente de los FPS
        if self.seguir and lonm is not None:
            # se detiene y gira (longitud y latitud) hasta dejar el punto de frente
            self.theta += self._envolver(lonm - self.theta) * k
            obj_incl = -latm
        else:                                        # sin mano: giro continuo normal
            self.theta = self._envolver(self.theta + GLOBO_VEL * dt)
            obj_incl = INCLINACION
        if abs(obj_incl - self.incl) > 1e-3:
            self.incl += (obj_incl - self.incl) * k
            self._calcular_esfera()

        # textura -> esfera (cada pixel del globo busca su color en el mapa plano)
        lon = self.lon0 + self.theta
        frac = (lon / (2*np.pi) + 0.5) % 1.0
        mx = ((U0 + frac * (U1 - U0)) * ANCHO).astype(np.float32)
        v = np.clip((LAT_ARRIBA - np.degrees(self.lat)) / (LAT_ARRIBA - LAT_ABAJO), 0, 1)
        my = (v * (ALTO - 1)).astype(np.float32)
        img = cv2.remap(self.tex, mx, my, cv2.INTER_LINEAR).astype(np.float32)
        if rid is not None:                          # resaltar la region tocada
            lab = self.etq[np.clip(my.astype(int), 0, ALTO-1), np.clip(mx.astype(int), 0, ANCHO-1)]
            hl = (lab == rid)[..., None]
            img = np.where(hl, img*0.5 + 255*0.5, img)
        img = np.clip(img * self.shade, 0, 255).astype(np.uint8)

        r, cx, cy = self.r, self.cx, self.cy
        cv2.circle(vis, (cx, cy), r + 8, (25, 25, 25), -1, cv2.LINE_AA)
        roi = vis[cy-r:cy+r, cx-r:cx+r]
        roi[self.mask] = img[self.mask]
        cv2.circle(vis, (cx, cy), r, (230, 230, 230), 2, cv2.LINE_AA)

        # marcador del dedo sobre el globo
        if lonm is not None:
            lr = lonm - self.theta
            wx, wy, wz = np.cos(latm)*np.sin(lr), np.sin(latm), np.cos(latm)*np.cos(lr)
            c, s = np.cos(self.incl), np.sin(self.incl)
            sx_, sy_, sz_ = wx, wy*c + wz*s, -wy*s + wz*c
            if sz_ > 0:                              # solo si esta del lado visible
                px, py = int(cx + sx_*r), int(cy - sy_*r)
                pulso = int(3 * np.sin(ahora * 6))
                cv2.circle(vis, (px, py), 7, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(vis, (px, py), 13 + pulso, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.putText(vis, T('punto al otro lado', 'point on the other side'), (cx-70, cy+r+28),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        cv2.putText(vis, T('GLOBO TERRAQUEO', 'GLOBE'), (cx-70, cy-r-16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)



# ----------------------------------------------------------------------------
# CONFIGURACION GENERAL
# ----------------------------------------------------------------------------
import re
import json
import queue
import asyncio
import threading
import unicodedata

# --- Camara -----------------------------------------------------------------
# CAMARA: numero = camara conectada a la PC (0 = laptop, 1/2 = DroidCam por USB / webcam)
#         texto  = URL de la camara del telefono por Wi-Fi (ej. "http://192.168.1.50:8080/video")
CAMARA = 1
CAPTURA = (1280, 720)   # resolucion que se le PIDE a la camara; si no la acepta se usa la suya
ROTAR = 90              # 0, 90, 180 o 270 grados (tambien con la tecla t). 90 = telefono vertical -> imagen horizontal
LLENAR = True           # True = la camara cubre TODO el recuadro del mapa (recorta un poco las orillas)
                        # False = se ve completa con franjas negras a los lados
QUITAR_FRANJAS = True   # recorta las franjas negras que pone DroidCam con el telefono en vertical
# La imagen siempre se acomoda HORIZONTAL (1280x720) sin deformarse.
TIEMPO_ESTABLE = 0.25      # segundos que el dedo debe estar en un lugar antes de decirlo
PERIODO_NOTA = 0.55        # cada cuanto se repite la nota del dato si el dedo no se mueve
CARPETA = os.path.dirname(os.path.abspath(__file__))

# Pantalla: lienzo con margen; el mapa (48 x 29 cm) queda centrado
CANVAS_W, CANVAS_H = 1920, 1080
MAPA_CM = (48.0, 29.0)
MAP_W = 1240
MAP_H = int(round(MAP_W * MAPA_CM[1] / MAPA_CM[0]))          # 749
MAP_X = (CANVAS_W - MAP_W) // 2                               # margen izq/der = 340
MAP_Y = (CANVAS_H - MAP_H) // 2                               # margen sup/inf ~ 165

try:
    import pygame
    PG_OK = True
except ImportError:
    PG_OK = False

# Nombres con acentos para la voz (en pantalla se usan sin acentos)
VOZ_PALABRAS = {
    'Norteamerica': 'Norteamérica', 'Centroamerica': 'Centroamérica',
    'Sudamerica': 'Sudamérica', 'Africa': 'África', 'Oceania': 'Oceanía',
    'Oceano': 'Océano', 'Atlantico': 'Atlántico', 'Pacifico': 'Pacífico',
    'Indico': 'Índico', 'Artico': 'Ártico', 'Mexico': 'México',
    'Mediterraneo': 'Mediterráneo', 'Persico': 'Pérsico', 'Bahia': 'Bahía',
    'Caribe': 'Caribe',
}


REGION_EN = {
    'Groenlandia': 'Greenland', 'Centroamerica y Caribe': 'Central America and the Caribbean',
    'Sudamerica': 'South America', 'Norteamerica': 'North America', 'Oceania': 'Oceania',
    'Europa': 'Europe', 'Africa': 'Africa', 'Asia': 'Asia',
    'Oceano Artico': 'Arctic Ocean', 'Bahia de Hudson': 'Hudson Bay', 'Grandes Lagos': 'Great Lakes',
    'Mar Negro': 'Black Sea', 'Mar Caspio': 'Caspian Sea', 'Golfo de Mexico': 'Gulf of Mexico',
    'Mar Caribe': 'Caribbean Sea', 'Mar Mediterraneo': 'Mediterranean Sea', 'Mar Rojo': 'Red Sea',
    'Golfo Persico': 'Persian Gulf', 'Golfo de Bengala': 'Bay of Bengal',
    'Mar de China Meridional': 'South China Sea', 'Oceano Indico': 'Indian Ocean',
    'Oceano Atlantico Norte': 'North Atlantic Ocean', 'Oceano Atlantico Sur': 'South Atlantic Ocean',
    'Oceano Pacifico': 'Pacific Ocean', 'Aguas interiores / Mar': 'Inland waters / Sea',
}


def nombre_mostrar(nombre):
    """Nombre de la region para la pantalla (los nombres internos estan en espanol)."""
    return REGION_EN.get(nombre, nombre) if IDIOMA == 'en' else nombre


def nombre_voz(nombre):
    if IDIOMA == 'en':
        if nombre == 'Aguas interiores / Mar':
            return 'Inland waters'
        return REGION_EN.get(nombre, nombre)
    if nombre == 'Aguas interiores / Mar':
        return 'Aguas interiores'
    return ' '.join(VOZ_PALABRAS.get(p, p) for p in nombre.split(' '))


# ----------------------------------------------------------------------------
# GEORREFERENCIA DE mapa.jpg: pixel (1500x844) -> longitud / latitud
# Ajuste polinomial con 12 puntos conocidos (error ~1-2 grados).
# ----------------------------------------------------------------------------
GEO_PUNTOS = [   # (lon, lat, x, y en mapa.jpg)
    (-168.0, 65.6, 160, 165), (-80.4, 25.1, 364, 355), (-5.6, 36.0, 672, 300),
    (-34.8, -7.2, 546, 525), (-67.3, -55.98, 459, 782), (20.0, -34.8, 772, 674),
    (51.3, 11.8, 905, 428), (77.5, 8.1, 1016, 445), (156.7, 51.2, 1265, 219),
    (142.5, -10.7, 1287, 548), (115.0, -34.4, 1152, 669), (-43.5, 59.8, 555, 181),
]


def _base_geo(x, y):
    x, y = np.asarray(x, np.float64) / REF_W, np.asarray(y, np.float64) / REF_H
    return np.stack([np.ones_like(x), x, y, x*y, y*y, x*y*y], -1)


_g = np.array(GEO_PUNTOS, np.float64)
COEF_LON = np.linalg.lstsq(_base_geo(_g[:, 2], _g[:, 3]), _g[:, 0], rcond=None)[0]
COEF_LAT = np.linalg.lstsq(_base_geo(_g[:, 2], _g[:, 3]), _g[:, 1], rcond=None)[0]


def ref_a_lonlat(xr, yr):
    """Punto(s) de mapa.jpg en pixeles ANCHO x ALTO -> (lon, lat) en grados."""
    b = _base_geo(np.asarray(xr) * REF_W / ANCHO, np.asarray(yr) * REF_H / ALTO)
    lon = (b @ COEF_LON + 180.0) % 360.0 - 180.0
    lat = np.clip(b @ COEF_LAT, -90.0, 90.0)
    return lon, lat


# ----------------------------------------------------------------------------
# DATOS NASA (imagenes reales de NASA GIBS, las mismas capas de NASA Worldview)
# Se descarga la imagen global de cada variable y su tabla de colores
# (colormap). Asi cada color de la imagen se convierte en su valor real.
# Los archivos quedan en la carpeta "datos_nasa" (funciona sin internet).
# ----------------------------------------------------------------------------
GIBS_WMS = 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi'
GIBS_CMAP = 'https://gibs.earthdata.nasa.gov/colormaps/v1.3/'
DATA_W, DATA_H = 720, 360          # 0.5 grados por pixel
CARPETA_DATOS = os.path.join(CARPETA, 'datos_nasa')

VARIABLES = [
    dict(clave='co2', tecla='1', nombre='CO2', voz='Dióxido de carbono',
         capa='AIRS_L3_Carbon_Dioxide_IR_Monthly', cmap='AIRS_Carbon_Dioxide_IR_Monthly',
         fecha='2017-02-01', conv=lambda v: v, rango=None, suavizar=2.5,
         fuente=['NASA AIRS (satelite Aqua)', 'CO2 troposfera media'],
         nombre_en='CO2', voz_en='Carbon dioxide',
         fuente_en=['NASA AIRS (Aqua satellite)', 'mid-troposphere CO2'],
         decir_en=lambda v: f'{v:.0f} parts per million',
         fmt=lambda v: f'{v:.1f} ppm',
         decir=lambda v: f'{v:.0f} partes por millón',
         timbre='organo', base=65.41, color=(60, 60, 230)),
    dict(clave='temp', tecla='2', nombre='Temperatura', voz='Temperatura',
         capa='MERRA2_2m_Air_Temperature_Monthly', cmap='MERRA2_2m_Air_Temperature_Monthly',
         fecha='2026-08-01', conv=lambda k: k - 273.15, rango=(-40.0, 40.0), suavizar=0,
         fuente=['NASA MERRA-2 (GMAO)', 'aire a 2 m, promedio mensual'],
         nombre_en='Temperature', voz_en='Temperature',
         fuente_en=['NASA MERRA-2 (GMAO)', 'air at 2 m, monthly mean'],
         decir_en=lambda v: f'{v:.0f} degrees Celsius',
         fmt=lambda v: f'{v:.1f} C',
         decir=lambda v: f'{v:.0f} grados',
         timbre='trompeta', base=174.61, color=(40, 160, 255)),
    # Altura del terreno sobre el nivel del mar (el relieve impreso en 3D).
    # Capa fija (no cambia con el tiempo): sin fecha. En el mar no hay dato.
    dict(clave='alt', tecla='3', nombre='Altitud', voz='Altura sobre el nivel del mar',
         capa='ASTER_GDEM_Color_Index', cmap='ASTER_GDEM_Color_Index',
         fecha=None, conv=lambda m: m, rango=(0.0, 4500.0), suavizar=1.2,
         fuente=['NASA ASTER GDEM (satelite Terra)', 'altura del terreno (m)'],
         nombre_en='Elevation', voz_en='Elevation above sea level',
         fuente_en=['NASA ASTER GDEM (Terra satellite)', 'terrain height (m)'],
         decir_en=lambda v: f'{max(v, 0):.0f} meters above sea level',
         fmt=lambda v: f'{v:.0f} m',
         decir=lambda v: f'{max(v, 0):.0f} metros sobre el nivel del mar',
         timbre='flauta', base=261.63, color=(60, 150, 210)),
]



def vt(v, clave):
    """Campo de una variable en el idioma actual (nombre, voz, fuente, decir)."""
    return v.get(clave + '_en', v[clave]) if IDIOMA == 'en' else v[clave]


TIMBRE_EN = {'organo': 'organ', 'trompeta': 'trumpet', 'flauta': 'flute'}
ESTADO_EN = {'cargando': 'loading', 'descargando': 'downloading', 'listo': 'ready',
             'sin datos': 'no data'}
VISTA_EN = {'camara': 'camera', 'datos NASA': 'NASA data', 'mezcla': 'blend'}


def tr_dic(texto, dic):
    return dic.get(texto, texto) if IDIOMA == 'en' else texto


def leer_colormap(ruta):
    """Lee el XML de colores de GIBS -> (colores RGB (N,3), valores (N,))."""
    txt = open(ruta, encoding='utf-8').read()
    cols, vals = [], []
    for m in re.finditer(r'<ColorMapEntry\s([^>]*?)/?>', txt):
        at = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        if at.get('nodata') == 'true' or 'value' not in at:
            continue
        partes = at['value'].strip('[]()').split(',')
        try:
            a, b = float(partes[0]), float(partes[-1])
        except ValueError:
            continue
        if np.isinf(a) and np.isinf(b):
            continue
        v = b if np.isinf(a) else a if np.isinf(b) else (a + b) / 2
        cols.append([int(c) for c in at['rgb'].split(',')])
        vals.append(v)
    return np.array(cols, np.float32), np.array(vals, np.float64)


def _suavizar_nan(v, sigma):
    m = np.isfinite(v).astype(np.float32)
    v0 = np.where(m > 0, v, 0).astype(np.float32)
    num = cv2.GaussianBlur(v0, (0, 0), sigma)
    den = cv2.GaussianBlur(m, (0, 0), sigma)
    out = np.where(den > 0.25, num / np.maximum(den, 1e-6), np.nan)
    return out.astype(np.float32)


class DatosNASA:
    def __init__(self):
        os.makedirs(CARPETA_DATOS, exist_ok=True)
        n = len(VARIABLES)
        self.valores = [None] * n      # grilla (360x720) de valores ya convertidos (ppm, C, cm)
        self.imagen = [None] * n       # imagen en colores NASA (BGR) para mostrar
        self.rango = [None] * n
        self.barra = [None] * n        # 256 colores NASA de bajo a alto (leyenda)
        self.estado = ['cargando'] * n
        self.version = 0               # cambia cuando una variable termina de cargar
        threading.Thread(target=self._cargar_todo, daemon=True).start()

    def _rutas(self, v):
        return (os.path.join(CARPETA_DATOS, v['capa'] + '.png'),
                os.path.join(CARPETA_DATOS, v['cmap'] + '.xml'))

    def _descargar(self, v):
        png, xml = self._rutas(v)
        if not os.path.exists(xml):
            urllib.request.urlretrieve(GIBS_CMAP + v['cmap'] + '.xml', xml + '.tmp')
            os.replace(xml + '.tmp', xml)
        if not os.path.exists(png):
            url = (f"{GIBS_WMS}?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS={v['capa']}"
                   f"&STYLES=&CRS=EPSG:4326&BBOX=-90,-180,90,180&WIDTH={DATA_W}&HEIGHT={DATA_H}"
                   f"&FORMAT=image/png&TRANSPARENT=TRUE" +
                   (f"&TIME={v['fecha']}" if v['fecha'] else ''))
            with urllib.request.urlopen(url, timeout=180) as r, open(png + '.tmp', 'wb') as f:
                f.write(r.read())
            os.replace(png + '.tmp', png)

    def _cargar_todo(self):
        for i, v in enumerate(VARIABLES):
            try:
                png, xml = self._rutas(v)
                if not (os.path.exists(png) and os.path.exists(xml)):
                    self.estado[i] = 'descargando'
                    print('Descargando datos NASA:', v['capa'], '(puede tardar 1 min)...')
                    self._descargar(v)
                self._procesar(i, v)
                self.estado[i] = 'listo'
                print(f"Datos NASA listos: {v['nombre']}  {self.rango[i]}")
            except Exception as e:
                self.estado[i] = 'sin datos'
                print('No se pudieron cargar los datos de', v['nombre'], ':', e)
            self.version += 1

    def _procesar(self, i, v):
        png, xml = self._rutas(v)
        cols, vals = leer_colormap(xml)
        img = cv2.imread(png, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise IOError('imagen danada: ' + png)
        img = cv2.resize(img, (DATA_W, DATA_H), interpolation=cv2.INTER_NEAREST)
        alfa = img[..., 3] if img.shape[2] == 4 else np.full(img.shape[:2], 255, np.uint8)
        rgb = img[..., 2::-1].reshape(-1, 3).astype(np.int64)
        clave = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
        uni, inv = np.unique(clave, return_inverse=True)
        uc = np.stack([(uni >> 16) & 255, (uni >> 8) & 255, uni & 255], 1).astype(np.float32)
        d = ((uc[:, None, :] - cols[None]) ** 2).sum(-1)
        cerca = d.argmin(1)
        val_u = np.where(d.min(1) <= 30 ** 2, vals[cerca], np.nan)
        valores = val_u[inv.ravel()].reshape(DATA_H, DATA_W)
        valores[alfa < 128] = np.nan
        valores = v['conv'](valores).astype(np.float32)
        if v['suavizar']:
            valores = _suavizar_nan(valores, v['suavizar'])
        ok = np.isfinite(valores)
        if v['rango'] is None:
            lo, hi = np.percentile(valores[ok], [2, 98])
        else:
            lo, hi = v['rango']
        # imagen para mostrar: colores oficiales NASA del valor (gris oscuro = sin dato)
        orden = np.argsort(vals)
        vs, cs = v['conv'](vals[orden]), cols[orden]
        idx = np.clip(np.searchsorted(vs, np.where(ok, valores, vs[0])), 0, len(vs) - 1)
        vis = cs[idx][..., ::-1].astype(np.uint8)
        vis[~ok] = (45, 45, 45)
        ib = np.clip(np.searchsorted(vs, np.linspace(lo, hi, 256)), 0, len(vs) - 1)
        self.barra[i] = cs[ib][:, ::-1].astype(np.uint8)
        self.valores[i], self.imagen[i], self.rango[i] = valores, vis, (float(lo), float(hi))

    def listo(self, i):
        return self.valores[i] is not None

    def valor(self, i, lon, lat):
        """Valor (promedio 3x3 ignorando huecos) en lon/lat, o None si no hay dato."""
        if not self.listo(i):
            return None
        c = int(((lon + 180.0) % 360.0) * DATA_W / 360.0) % DATA_W
        f = int(np.clip((90.0 - lat) * DATA_H / 180.0, 0, DATA_H - 1))
        cs = [(c + k) % DATA_W for k in (-1, 0, 1)]
        bloque = self.valores[i][max(f-1, 0):f+2][:, cs]
        bloque = bloque[np.isfinite(bloque)]
        return float(bloque.mean()) if bloque.size else None

    def normalizar(self, i, val):
        lo, hi = self.rango[i]
        return float(np.clip((val - lo) / (hi - lo), 0, 1))


# ----------------------------------------------------------------------------
# VOZ: dice los lugares y las variables en voz alta
# ----------------------------------------------------------------------------
# Voces: ver VOCES_EDGE arriba (otras: en-US-GuyNeural, es-MX-JorgeNeural)


class Voz:
    def __init__(self, audio_ok):
        self.dir = os.path.join(CARPETA, 'voz')
        os.makedirs(self.dir, exist_ok=True)
        self.audio_ok = audio_ok
        self.q = queue.Queue()
        self.hablando = False
        self.mudo = False
        self.lock = threading.Lock()
        try:
            import edge_tts
            self.edge = edge_tts
        except ImportError:
            self.edge = None
        try:
            import pyttsx3
            self.pyttsx3 = pyttsx3
        except ImportError:
            self.pyttsx3 = None
        self.sapis = {}
        print('Voz:', self.motor)
        threading.Thread(target=self._trabajador, daemon=True).start()

    @property
    def motor(self):
        if self.edge and self.audio_ok:
            return 'edge-tts ' + VOCES_EDGE[IDIOMA]
        if self.pyttsx3:
            return T('voz de Windows', 'Windows voice')
        return T('sin voz (pip install edge-tts pyttsx3)', 'no voice (pip install edge-tts pyttsx3)')

    def _ruta(self, texto, idioma):
        s = unicodedata.normalize('NFKD', texto.lower()).encode('ascii', 'ignore').decode()
        pre = 'en_' if idioma == 'en' else ''      # espanol sin prefijo (audios de versiones previas)
        return os.path.join(self.dir, pre + re.sub(r'[^a-z0-9]+', '_', s).strip('_')[:90] + '.mp3')

    def _generar(self, texto, idioma):
        """Crea el mp3 con edge-tts (si hay internet). True si existe al final."""
        ruta = self._ruta(texto, idioma)
        if os.path.exists(ruta):
            return True
        if not (self.edge and self.audio_ok):
            return False
        with self.lock:
            if os.path.exists(ruta):
                return True
            tmp = ruta[:-4] + '_tmp.mp3'
            try:
                async def crear():
                    await self.edge.Communicate(texto, VOCES_EDGE[idioma]).save(tmp)
                asyncio.run(crear())
                os.replace(tmp, ruta)
                return True
            except Exception as e:
                print('edge-tts no disponible (sin internet?), uso la voz de Windows:', e)
                self.edge = None
                return False

    def pregenerar(self, textos):
        idioma = IDIOMA
        def tarea():
            for t in textos:
                if not self._generar(t, idioma):
                    break
        threading.Thread(target=tarea, daemon=True).start()

    def decir(self, texto, interrumpir=True):
        print('Voz:', texto)
        if self.mudo:
            return
        if interrumpir:
            while not self.q.empty():
                try:
                    self.q.get_nowait()
                except queue.Empty:
                    break
            if self.audio_ok:
                pygame.mixer.music.stop()
        self.q.put((texto, IDIOMA))

    def ocupada(self):
        return (self.hablando or not self.q.empty() or
                (self.audio_ok and pygame.mixer.music.get_busy()))

    def _iniciar_sapi(self, idioma):
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass
        motor = self.pyttsx3.init()
        for v in motor.getProperty('voices'):
            desc = (str(v.name) + ' ' + str(v.id) + ' ' + str(getattr(v, 'languages', ''))).lower()
            claves = (('english', 'en-us', 'en_us', 'en-gb', 'zira', 'david', 'hazel', 'mark') if idioma == 'en'
                      else ('spanish', 'espa', 'es-mx', 'es_mx', 'es-es', 'sabina', 'helena', 'raul', 'laura', 'pablo'))
            if any(k in desc for k in claves):
                motor.setProperty('voice', v.id)
                break
        motor.setProperty('rate', 175)
        return motor

    def _trabajador(self):
        while True:
            texto, idioma = self.q.get()
            self.hablando = True
            try:
                if self._generar(texto, idioma) and self.audio_ok:
                    pygame.mixer.music.load(self._ruta(texto, idioma))
                    pygame.mixer.music.play()
                    time.sleep(0.05)
                    while pygame.mixer.music.get_busy() and self.q.empty():
                        time.sleep(0.02)
                elif self.pyttsx3:
                    if idioma not in self.sapis:
                        self.sapis[idioma] = self._iniciar_sapi(idioma)
                    sapi = self.sapis[idioma]
                    sapi.say(texto)
                    sapi.runAndWait()
            except Exception as e:
                print('Error de voz:', e)
            finally:
                self.hablando = False


# ----------------------------------------------------------------------------
# SONIFICACION CONTINUA: cada variable es un instrumento que suena SOSTENIDO
# mientras el dedo esta en el mapa. La altura sigue al dato en tiempo real:
# valor bajo = grave, valor alto = agudo (2 octavas). La voz habla encima.
# ----------------------------------------------------------------------------
SR = 44100
RANGO_SEMITONOS = 24       # 2 octavas entre el valor minimo y el maximo
PASOS_SEMITONO = 2         # resolucion de la altura (medio semitono)
N_PASOS = RANGO_SEMITONOS * PASOS_SEMITONO + 1
LOOP_S = 2.0               # duracion de cada bucle sostenido (se repite sin cortes)
FUNDIDO_MS = 70            # cruce suave al cambiar de altura
SUAVIZADO = 0.30           # 0-1: que tan rapido "se desliza" la altura hacia el dato
VOL_CON_VOZ = 0.45         # volumen del instrumento mientras la voz habla
VOL_SIN_DATO = 0.25        # volumen si el dedo esta donde esa variable no tiene dato
GRACIA_DEDO = 0.35         # s que sigue sonando si la camara pierde el dedo un instante


def sintetizar(timbre, fase, t, f_ref, circular=False):
    """Genera el instrumento a partir de la fase de la fundamental (radianes)."""
    n = len(t)
    if timbre == 'trompeta':
        # metal: muchos armonicos con un "formante" brillante cerca de 1.3 kHz
        y = np.zeros(n)
        for k in range(1, 16):
            if k * f_ref > 9000:
                break
            a = (1.0 / k ** 0.6) * (1 + 1.6 * np.exp(-((k * f_ref - 1300) / 750) ** 2))
            y += a * np.sin(k * fase)
        y = np.tanh(1.8 * y / (np.abs(y).max() + 1e-9))      # aspereza de metal
    elif timbre == 'organo':
        # organo grave y denso: armonicos de tubo + una copia desafinada (pulsaciones)
        y = np.zeros(n)
        for k, a in ((1, 1.0), (2, 0.75), (3, 0.5), (4, 0.4), (6, 0.25), (8, 0.18)):
            y += a * np.sin(k * fase)
            y += 0.45 * a * np.sin(k * fase * (1 + 0.5 / max(f_ref * LOOP_S, 1)) if not circular
                                   else k * (fase + 2 * np.pi * 0.5 * t))
    else:
        # flauta: casi pura, con soplido y un vaiven lento como olas
        y = np.sin(fase) + 0.22 * np.sin(2 * fase) + 0.07 * np.sin(3 * fase)
        ruido = np.random.RandomState(3).randn(n)
        if circular:                                   # ruido que se repite sin corte
            F = np.fft.rfft(ruido)
            fr = np.fft.rfftfreq(n, 1 / SR)
            F *= np.exp(-((fr - 2.5 * f_ref) / (1.2 * f_ref)) ** 2)
            ruido = np.fft.irfft(F, n)
        else:
            ruido = np.convolve(ruido, np.ones(25) / 25, 'same')
        y += 0.35 * ruido / (np.abs(ruido).max() + 1e-9)
        y *= 0.62 + 0.38 * np.sin(2 * np.pi * (1.0 / LOOP_S) * t)   # oleaje (1 ola por bucle)
    return y


def bucle_sostenido(timbre, f):
    """Nota sostenida de LOOP_S segundos que se puede repetir sin clics."""
    n = int(SR * LOOP_S)
    t = np.arange(n) / SR
    f = max(1, round(f * LOOP_S)) / LOOP_S          # numero entero de ciclos en el bucle
    vib_f = 5.5 if timbre == 'trompeta' else 5.0    # vibrato (tambien entero en el bucle)
    prof = {'trompeta': 0.005, 'organo': 0.0, 'flauta': 0.004}.get(timbre, 0.0)
    fase = 2 * np.pi * f * t - (prof * f / vib_f) * np.cos(2 * np.pi * vib_f * t)
    fase -= fase[0]
    y = sintetizar(timbre, fase, t, f, circular=True)
    y = y / (np.abs(y).max() + 1e-9) * 0.42
    return (y * 32767).astype(np.int16)


def barrido(timbre, f0, dur=1.4):
    """Barrido de grave a agudo: indica la direccion del sonido de la variable."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    f = f0 * 2 ** (RANGO_SEMITONOS / 12 * t / dur)
    fase = 2 * np.pi * np.cumsum(f) / SR
    y = sintetizar(timbre, fase, t, f0 * 2)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.25)
    y = y * env
    y = y / (np.abs(y).max() + 1e-9) * 0.45
    return (y * 32767).astype(np.int16)


def iniciar_audio():
    if not PG_OK:
        print('pygame no esta instalado: sin sonido')
        return False
    try:
        pygame.mixer.pre_init(SR, -16, 1, 512)
        pygame.mixer.init()
        return True
    except Exception as e:
        print('No se pudo iniciar el audio:', e)
        return False


class Sonificador:
    def __init__(self, voz):
        self.voz = voz
        self.ok = PG_OK and voz.audio_ok
        self.var = 1                   # empieza en Temperatura
        self.mudo = False
        self.arrays = {}               # (var, paso) -> int16 (se calculan en otro hilo)
        self.sonidos = {}
        self.actual = self.cand = None
        self.t_cand = 0.0
        self.firma_pend = False
        self.t_dedo = 0.0
        self._reiniciar_tono()
        if self.ok:
            pygame.mixer.set_num_channels(8)
            self.canales = [pygame.mixer.Channel(1), pygame.mixer.Channel(2)]
            self.canal_firma = pygame.mixer.Channel(3)
            threading.Thread(target=self._pregenerar, daemon=True).start()

    # ---- generacion de sonidos ----
    def _pregenerar(self):
        orden = [self.var] + [i for i in range(len(VARIABLES)) if i != self.var]
        for var in orden:
            for paso in range(N_PASOS):
                self._array(var, paso)

    def _array(self, var, paso):
        clave = (var, paso)
        if clave not in self.arrays:
            v = VARIABLES[var]
            f = v['base'] * 2 ** (paso / PASOS_SEMITONO / 12)
            self.arrays[clave] = bucle_sostenido(v['timbre'], f)
        return self.arrays[clave]

    def _sound(self, a):
        if pygame.mixer.get_init()[2] == 2:
            a = np.column_stack([a, a])
        return pygame.sndarray.make_sound(np.ascontiguousarray(a))

    def _bucle(self, var, paso):
        clave = (var, paso)
        if clave not in self.sonidos:
            self.sonidos[clave] = self._sound(self._array(var, paso))
        return self.sonidos[clave]

    def _firma(self, var):
        clave = ('firma', var)
        if clave not in self.sonidos:
            v = VARIABLES[var]
            self.sonidos[clave] = self._sound(barrido(v['timbre'], v['base']))
        return self.sonidos[clave]

    # ---- control ----
    def _reiniciar_tono(self):
        self.paso = None
        self.norm_obj = None
        self.norm_suave = None
        self.vol = 0.0
        self.snd = None
        self.activo = 0
        self.t_cambio = 0.0

    def _apagar(self, ms=250):
        if self.ok and self.paso is not None:
            for c in self.canales:
                c.fadeout(ms)
        self._reiniciar_tono()

    def seleccionar(self, i):
        self.var = i
        self._apagar(120)              # cambia de instrumento
        self.voz.decir(vt(VARIABLES[i], 'voz'))
        self.firma_pend = True

    def actualizar(self, region, norm, hay_dedo):
        """region: lugar bajo el dedo (o None); norm: dato 0-1 (None = sin dato)."""
        ahora = time.time()
        # 1) decir el lugar cuando el dedo se queda un momento en el (sin cortar el sonido)
        if region != self.cand:
            self.cand, self.t_cand = region, ahora
        elif region != self.actual and ahora - self.t_cand >= TIEMPO_ESTABLE:
            self.actual = region
            if region is not None:
                self.voz.decir(nombre_voz(region))
        if not self.ok:
            return
        if self.mudo:
            self._apagar(0)
            return
        # 2) barrido de la variable recien elegida, cuando la voz termina de nombrarla
        if self.firma_pend and not self.voz.ocupada():
            self.canal_firma.play(self._firma(self.var))
            self.firma_pend = False
        # 3) instrumento sostenido mientras el dedo esta en el mapa
        if hay_dedo:
            self.t_dedo = ahora
        if ahora - self.t_dedo > GRACIA_DEDO:
            self._apagar()
            return
        if norm is not None:
            self.norm_obj = norm
            vol_obj = 1.0
        else:
            vol_obj = VOL_SIN_DATO     # se queda en la ultima altura, mas bajito
            if self.norm_obj is None:
                self.norm_obj = 0.5
        if self.norm_suave is None:
            self.norm_suave = self.norm_obj
        else:
            self.norm_suave += (self.norm_obj - self.norm_suave) * SUAVIZADO
        paso = int(round(self.norm_suave * (N_PASOS - 1)))
        if paso != self.paso and (self.paso is None or ahora - self.t_cambio >= 0.045):
            nuevo = 1 - self.activo
            snd = self._bucle(self.var, paso)
            snd.set_volume(max(self.vol, 0.05))
            self.canales[nuevo].play(snd, loops=-1, fade_ms=FUNDIDO_MS)
            if self.paso is not None:
                self.canales[self.activo].fadeout(FUNDIDO_MS)
            self.activo, self.paso, self.snd, self.t_cambio = nuevo, paso, snd, ahora
        # 4) volumen: baja un poco mientras la voz habla, pero nunca se corta
        if self.voz.ocupada():
            vol_obj *= VOL_CON_VOZ
        self.vol += (vol_obj - self.vol) * 0.25
        if self.snd is not None:
            self.snd.set_volume(self.vol)


# ----------------------------------------------------------------------------
# CALIBRACION CAMARA <-> MAPA IMPRESO
# Se marcan en la imagen de la camara las 4 esquinas del mapa (en este orden:
# 1 sup-izq, 2 sup-der, 3 inf-der, 4 inf-izq). Con eso se calcula una
# homografia que convierte cualquier punto de la camara a un punto del mapa.
# No hace falta acomodar la camara "perfecto": basta con que vea todo el mapa.
# Las esquinas se guardan en calibracion_mapa.json y se cargan al iniciar.
# ----------------------------------------------------------------------------
import json

ESPEJO = False   # True = ver la camara como espejo (no afecta la precision)
ARCHIVO_CALIB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'calibracion_mapa.json')
NOMBRES_ESQ = ['1 Sup-Izq', '2 Sup-Der', '3 Inf-Der', '4 Inf-Izq']
NOMBRES_ESQ_EN = ['1 Top-Left', '2 Top-Right', '3 Bottom-Right', '4 Bottom-Left']


def nombre_esq(i):
    return (NOMBRES_ESQ_EN if IDIOMA == 'en' else NOMBRES_ESQ)[i]
DESTINO = np.float32([[0, 0], [ANCHO-1, 0], [ANCHO-1, ALTO-1], [0, ALTO-1]])

# ----------------------------------------------------------------------------
# AJUSTE FINO POR PUNTOS DE CONTROL
# Las 4 esquinas solo "enderezan" el mapa impreso. Pero mapa.jpg tiene margenes
# blancos y otra proporcion/proyeccion que el mapa 3D, asi que estirar mapa.jpg
# de esquina a esquina NO hace coincidir los continentes. Por eso se marcan
# puntos reconocibles: con ellos se calcula una deformacion suave (thin-plate
# spline) que lleva cada punto del mapa impreso a su punto en mapa.jpg.
# Coordenadas en pixeles de mapa.jpg (1500x844).
# ----------------------------------------------------------------------------
PUNTOS_REF = [
    ('Punta oeste de Alaska',              (160, 165)),
    ('Punta sur de Groenlandia',           (555, 181)),
    ('Punta de Florida',                   (364, 355)),
    ('Estrecho de Gibraltar',              (672, 300)),
    ('Punta este de Brasil',               (546, 525)),
    ('Cabo de Hornos (sur de Sudamerica)', (459, 782)),
    ('Punta sur de Africa',                (772, 674)),
    ('Cuerno de Africa (Somalia)',         (905, 428)),
    ('Punta sur de la India',              (1016, 445)),
    ('Punta sur de Kamchatka',             (1265, 219)),
    ('Cabo York (norte de Australia)',     (1287, 548)),
    ('Esquina suroeste de Australia',      (1152, 669)),
    ('Los Angeles',                        (226, 312)),
    ('Tres Fronteras (Peru-Colombia-Brasil)', (396, 508)),
    ('Norte de Groenlandia',               (625, 83)),
    ('Cabo Norte (Noruega)',               (793, 115)),
    ('Cabo Chelyuskin (norte de Asia)',    (990, 92)),
]
PUNTOS_EN = {
    'Punta oeste de Alaska': 'Western tip of Alaska', 'Punta sur de Groenlandia': 'Southern tip of Greenland',
    'Punta de Florida': 'Tip of Florida', 'Estrecho de Gibraltar': 'Strait of Gibraltar',
    'Punta este de Brasil': 'Eastern tip of Brazil',
    'Cabo de Hornos (sur de Sudamerica)': 'Cape Horn (southern South America)',
    'Punta sur de Africa': 'Southern tip of Africa', 'Cuerno de Africa (Somalia)': 'Horn of Africa (Somalia)',
    'Punta sur de la India': 'Southern tip of India', 'Punta sur de Kamchatka': 'Southern tip of Kamchatka',
    'Cabo York (norte de Australia)': 'Cape York (northern Australia)',
    'Esquina suroeste de Australia': 'Southwest corner of Australia',
    'Los Angeles': 'Los Angeles',
    'Tres Fronteras (Peru-Colombia-Brasil)': 'Tri-border Peru-Colombia-Brazil',
    'Norte de Groenlandia': 'Northern Greenland',
    'Cabo Norte (Noruega)': 'North Cape (Norway)',
    'Cabo Chelyuskin (norte de Asia)': 'Cape Chelyuskin (northern Asia)',
}
SUAVIDAD = 1e-3   # mas alto = deformacion mas suave (tolera clics imprecisos)


def ref_a_pantalla(x, y):
    return x * ANCHO / REF_W, y * ALTO / REF_H


def crear_ajuste(pares):
    """pares: lista de (px, py, rx, ry). P = mapa impreso enderezado, R = mapa.jpg
    (ambos en pixeles ANCHO x ALTO). Devuelve f(pts Nx2 en P) -> pts Nx2 en R."""
    n = len(pares)
    if n == 0:
        return lambda pts: pts
    a = np.array(pares, np.float64)
    P, R = a[:, :2], a[:, 2:]
    if n < 3:                                   # solo desplazar
        d = (R - P).mean(0)
        return lambda pts: pts + d
    if n < 6:                                   # afin (3) u homografia (4-5)
        if n == 3:
            M = cv2.getAffineTransform(P.astype(np.float32), R.astype(np.float32))
            H = np.vstack([M, [0, 0, 1]])
        else:
            H, _ = cv2.findHomography(P, R, 0)
            if H is None:
                d = (R - P).mean(0)
                return lambda pts: pts + d
        def f(pts):
            q = np.c_[pts, np.ones(len(pts))] @ H.T
            return q[:, :2] / q[:, 2:3]
        return f
    # thin-plate spline (6 o mas puntos)
    s = float(ANCHO)
    Pn = P / s
    def U(d2):
        return 0.5 * d2 * np.log(np.maximum(d2, 1e-12))
    K = U(((Pn[:, None] - Pn[None]) ** 2).sum(-1)) + SUAVIDAD * np.eye(n)
    A = np.c_[np.ones(n), Pn]
    L = np.zeros((n + 3, n + 3))
    L[:n, :n], L[:n, n:], L[n:, :n] = K, A, A.T
    Y = np.zeros((n + 3, 2))
    Y[:n] = (R - P) / s
    coef = np.linalg.lstsq(L, Y, rcond=None)[0]
    def f(pts):
        out = np.empty_like(pts, dtype=np.float64)
        for i in range(0, len(pts), 100000):
            q = pts[i:i+100000] / s
            d2 = ((q[:, None] - Pn[None]) ** 2).sum(-1)
            disp = U(d2) @ coef[:n] + np.c_[np.ones(len(q)), q] @ coef[n:]
            out[i:i+100000] = pts[i:i+100000] + disp * s
        return out
    return f


class Calibracion:
    def __init__(self):
        self.esq = []            # esquinas marcadas (en pixeles de la camara)
        self.H = self.Hinv = None
        self.arrastrando = None
        self.sel = 0             # esquina seleccionada para ajuste fino con teclado
        self.puntos = {}         # nombre de PUNTOS_REF -> [px, py] en el mapa enderezado
        self.k = 0               # punto de control que se esta pidiendo
        self.modo_puntos = False
        self.version = 0         # cambia cada vez que cambia el ajuste
        self.cargar()
        self._ajustar()

    @property
    def lista(self):
        return self.H is not None

    def _calcular(self):
        if len(self.esq) == 4:
            src = np.float32(self.esq)
            self.H = cv2.getPerspectiveTransform(src, DESTINO)
            self.Hinv = cv2.getPerspectiveTransform(DESTINO, src)
        else:
            self.H = self.Hinv = None

    def cargar(self):
        try:
            with open(ARCHIVO_CALIB) as f:
                d = json.load(f)
            if d.get('ancho') == ANCHO and d.get('alto') == ALTO and len(d['esquinas']) == 4:
                self.esq = [[float(x), float(y)] for x, y in d['esquinas']]
                self._calcular()
                nombres = [nm for nm, _ in PUNTOS_REF]
                self.puntos = {nm: [float(x), float(y)]
                               for nm, (x, y) in d.get('puntos', {}).items() if nm in nombres}
                print('Calibracion cargada:', ARCHIVO_CALIB)
        except FileNotFoundError:
            pass
        except Exception as e:
            print('No se pudo leer la calibracion:', e)

    def guardar(self):
        if not self.lista:
            return False
        with open(ARCHIVO_CALIB, 'w') as f:
            json.dump({'ancho': ANCHO, 'alto': ALTO, 'esquinas': self.esq,
                       'puntos': self.puntos}, f, indent=2)
        print('Calibracion guardada en', ARCHIVO_CALIB)
        return True

    def reiniciar(self):
        self.esq, self.sel = [], 0
        self._calcular()

    # ---- ajuste fino por puntos ----
    def _ajustar(self):
        pares = []
        for nm, (rx, ry) in PUNTOS_REF:
            if nm in self.puntos:
                pares.append((*self.puntos[nm], *ref_a_pantalla(rx, ry)))
        f = crear_ajuste(pares)
        gx, gy = np.meshgrid(np.arange(ANCHO, dtype=np.float64), np.arange(ALTO, dtype=np.float64))
        q = f(np.stack([gx.ravel(), gy.ravel()], 1))
        self.mapx = q[:, 0].reshape(ALTO, ANCHO).astype(np.float32)
        self.mapy = q[:, 1].reshape(ALTO, ANCHO).astype(np.float32)
        self.version += 1
        self._objetivo = None

    def agregar_punto(self, x, y):
        """Marca el punto de control actual en (x, y) de la camara."""
        if self.H is None:
            return
        p = cv2.perspectiveTransform(np.float32([[[x, y]]]), self.H)[0, 0]
        if not (-50 <= p[0] < ANCHO + 50 and -50 <= p[1] < ALTO + 50):
            print('Ese punto esta fuera del mapa'); return
        nm = PUNTOS_REF[self.k][0]
        self.puntos[nm] = [float(p[0]), float(p[1])]
        print(f'Punto "{nm}" marcado ({len(self.puntos)} en total)')
        self.k = (self.k + 1) % len(PUNTOS_REF)
        self._ajustar()

    def borrar_punto(self, todos=False):
        if todos:
            self.puntos = {}
        else:
            self.puntos.pop(PUNTOS_REF[self.k][0], None)
        self._ajustar()

    def objetivo_en_camara(self):
        """Donde la guia cree que esta el punto actual (en la camara)."""
        if self.H is None:
            return None
        if self._objetivo is None or self._objetivo[0] != self.k:
            rx, ry = ref_a_pantalla(*PUNTOS_REF[self.k][1])
            d = (self.mapx - rx) ** 2 + (self.mapy - ry) ** 2
            py, px = np.unravel_index(int(np.argmin(d)), d.shape)
            self._objetivo = (self.k, float(px), float(py))
        _, px, py = self._objetivo
        c = cv2.perspectiveTransform(np.float32([[[px, py]]]), self.Hinv)[0, 0]
        return int(c[0]), int(c[1])

    def a_ref(self, p):
        """Punto del mapa enderezado -> punto en mapa.jpg (para el globo)."""
        x, y = p
        return (int(np.clip(self.mapx[y, x], 0, ANCHO - 1)),
                int(np.clip(self.mapy[y, x], 0, ALTO - 1)))

    def a_mapa(self, x, y):
        """Punto de la camara -> punto del mapa (None si cae fuera del mapa)."""
        if self.H is None:
            return None
        p = cv2.perspectiveTransform(np.float32([[[x, y]]]), self.H)[0, 0]
        mx, my = int(round(p[0])), int(round(p[1]))
        if 0 <= mx < ANCHO and 0 <= my < ALTO:
            return mx, my
        return None

    def raton(self, evento, x, y):
        if self.modo_puntos and self.lista:
            if evento == cv2.EVENT_LBUTTONDOWN:
                self.agregar_punto(x, y)
            return
        if evento == cv2.EVENT_LBUTTONDOWN:
            if len(self.esq) < 4:                         # marcar la siguiente esquina
                self.esq.append([float(x), float(y)])
                self.sel = len(self.esq) - 1
                self._calcular()
                return
            d = [np.hypot(x - px, y - py) for px, py in self.esq]
            i = int(np.argmin(d))
            if d[i] < 45:                                 # agarrar la esquina mas cercana
                self.arrastrando = self.sel = i
        elif evento == cv2.EVENT_MOUSEMOVE and self.arrastrando is not None:
            self.esq[self.arrastrando] = [float(x), float(y)]
            self._calcular()
        elif evento == cv2.EVENT_LBUTTONUP:
            self.arrastrando = None

    def mover(self, dx, dy):
        if self.sel < len(self.esq):
            self.esq[self.sel][0] += dx
            self.esq[self.sel][1] += dy
            self._calcular()


def dibujar_calibracion(frame, calib, mapa_guia, ver_guia, mini):
    vis = frame.copy()
    # Mapa virtual "proyectado" sobre la camara para comprobar que coincide
    if calib.lista and ver_guia:
        sup = cv2.warpPerspective(mapa_guia, calib.Hinv, (ANCHO, ALTO))
        m = cv2.warpPerspective(np.full((ALTO, ANCHO), 255, np.uint8),
                                calib.Hinv, (ANCHO, ALTO)) > 0
        vis[m] = cv2.addWeighted(vis, 0.5, sup, 0.5, 0)[m]

    pts = [(int(x), int(y)) for x, y in calib.esq]
    if len(pts) > 1:
        cv2.polylines(vis, [np.int32(pts)], len(pts) == 4, (0, 255, 255), 2, cv2.LINE_AA)
    for i, p in enumerate(pts):
        color = (0, 0, 255) if i == calib.sel else (0, 255, 255)
        cv2.circle(vis, p, 10, color, -1, cv2.LINE_AA)
        cv2.circle(vis, p, 14, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(vis, nombre_esq(i), (p[0] + 14, p[1] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)
        cv2.putText(vis, nombre_esq(i), (p[0] + 14, p[1] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    puntos_on = calib.modo_puntos and calib.lista
    if puntos_on:
        # puntos ya marcados (verde) y donde la guia cree que esta el actual (amarillo)
        for nm, (px, py) in calib.puntos.items():
            c = cv2.perspectiveTransform(np.float32([[[px, py]]]), calib.Hinv)[0, 0]
            cv2.circle(vis, (int(c[0]), int(c[1])), 7, (0, 200, 0), -1, cv2.LINE_AA)
            cv2.circle(vis, (int(c[0]), int(c[1])), 9, (0, 0, 0), 1, cv2.LINE_AA)
        o = calib.objetivo_en_camara()
        if o is not None:
            cv2.drawMarker(vis, o, (0, 255, 255), cv2.MARKER_CROSS, 30, 2, cv2.LINE_AA)
        nm = PUNTOS_REF[calib.k][0]
        nmt = tr_dic(nm, PUNTOS_EN)
        hecho = T(' (ya marcado)', ' (already marked)') if nm in calib.puntos else ''
        n = len(calib.puntos)
        lineas = [T(f'AJUSTE FINO {calib.k+1}/{len(PUNTOS_REF)}: marca "{nmt}"{hecho} en el mapa impreso',
                    f'FINE ADJUST {calib.k+1}/{len(PUNTOS_REF)}: mark "{nmt}"{hecho} on the printed map'),
                  T('clic = marcar   ESPACIO = usar punta del dedo   n/b = sig./ant.   x = borrar   z = borrar todos',
                    'click = mark   SPACE = use fingertip   n/b = next/prev   x = delete   z = delete all'),
                  T(f'{n} puntos (min. 4, ideal todos)   + amarillo = donde cree la guia   p = esquinas   ENTER = guardar',
                    f'{n} points (min. 4, ideally all)   yellow + = where the guide thinks it is   p = corners   ENTER = save')]
    elif len(pts) < 4:
        lineas = [T(f'CALIBRACION: haz clic en la esquina {nombre_esq(len(pts))} del mapa',
                    f'CALIBRATION: click the {nombre_esq(len(pts))} corner of the map'),
                  T('(orden: sup-izq, sup-der, inf-der, inf-izq; arriba = Polo Norte)',
                    '(order: top-left, top-right, bottom-right, bottom-left; top = North Pole)'),
                  T('r = reiniciar    q / ESC = salir', 'r = restart    q / ESC = quit')]
    else:
        lineas = [T('CALIBRACION: arrastra las esquinas a las orillas del mapa impreso',
                    'CALIBRATION: drag the corners to the edges of the printed map'),
                  T('1-4 = elegir esquina   i/j/k/l = mover 1 px   m = ver/ocultar guia   r = reiniciar',
                    '1-4 = pick corner   i/j/k/l = move 1 px   m = show/hide guide   r = restart'),
                  T('p = AJUSTE FINO por puntos (si la guia no coincide)   ENTER = guardar y usar   q/ESC = salir',
                    'p = FINE ADJUST by points (if the guide does not match)   ENTER = save and use   q/ESC = quit')]
    y0 = 0
    ov = vis.copy()
    cv2.rectangle(ov, (0, 0), (ANCHO, 30 * len(lineas) + 20), (0, 0, 0), -1)
    vis = cv2.addWeighted(ov, 0.65, vis, 0.35, 0)
    for k, t in enumerate(lineas):
        texto(vis, t, (20, y0 + 26 + 30 * k), 0.6, (255, 255, 255), 1)

    # margen derecho (fuera de la camara) con el mapa pequeno del punto a marcar
    lienzo = np.full((ALTO, ANCHO + MARGEN_CALIB, 3), FONDO, np.uint8)
    lienzo[:, :ANCHO] = vis
    mw = MARGEN_CALIB - 30
    mh = int(round(mw * REF_H / REF_W))
    m = cv2.resize(mini, (mw, mh), interpolation=cv2.INTER_AREA)
    x0, y0 = ANCHO + 15, 140
    if puntos_on:
        rx, ry = PUNTOS_REF[calib.k][1]
        q = (int(rx * mw / REF_W), int(ry * mh / REF_H))
        cv2.circle(m, q, 6, (0, 0, 255), -1, cv2.LINE_AA)
        cv2.circle(m, q, 10, (0, 0, 0), 2, cv2.LINE_AA)
        texto(lienzo, T('PUNTO A MARCAR', 'POINT TO MARK'), (x0, y0 - 15), 0.6, GRIS, 1)
        nm = PUNTOS_REF[calib.k][0]
        texto_ajustado(lienzo, f'{calib.k + 1}. {tr_dic(nm, PUNTOS_EN)}', (x0, y0 + mh + 35),
                       mw, 0.65, (0, 165, 255), 2, 28)
    else:
        texto(lienzo, T('MAPA DE REFERENCIA', 'REFERENCE MAP'), (x0, y0 - 15), 0.6, GRIS, 1)
    lienzo[y0:y0 + mh, x0:x0 + mw] = m
    cv2.rectangle(lienzo, (x0 - 1, y0 - 1), (x0 + mw, y0 + mh), (255, 255, 255), 2)
    return lienzo


MARGEN_CALIB = 340    # ancho del margen derecho en la pantalla de calibracion

# ----------------------------------------------------------------------------
# INTERFAZ: lienzo con margen, mapa centrado y la informacion en los margenes
# ----------------------------------------------------------------------------
FUENTE = cv2.FONT_HERSHEY_SIMPLEX
FONDO = (32, 24, 18)
GRIS = (170, 170, 170)
BLANCO = (245, 245, 245)
VISTAS = ['camara', 'datos NASA', 'mezcla']


# Textos nitidos con la fuente de Windows (Segoe UI) usando Pillow. Si no hay
# Pillow o la fuente, se usa la letra de OpenCV como antes.
ESCALA_LETRA = 31          # px de letra por cada 1.0 de "esc" (equivale a OpenCV)
try:
    from PIL import Image, ImageDraw, ImageFont
    _RUTAS_LETRA = {False: [r'C:\Windows\Fonts\segoeui.ttf', r'C:\Windows\Fonts\arial.ttf',
                            'DejaVuSans.ttf'],
                    True: [r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\arialbd.ttf',
                           'DejaVuSans-Bold.ttf']}
    ImageFont.truetype(_RUTAS_LETRA[False][0] if os.path.exists(_RUTAS_LETRA[False][0])
                       else _RUTAS_LETRA[False][-1], 20)
    PIL_OK = True
except Exception:
    PIL_OK = False
_LETRAS, _SPRITES = {}, {}


def _letra(px, negrita):
    clave = (px, negrita)
    if clave not in _LETRAS:
        for ruta in _RUTAS_LETRA[negrita]:
            try:
                _LETRAS[clave] = ImageFont.truetype(ruta, px)
                break
            except Exception:
                continue
    return _LETRAS[clave]


def _sprite(s, esc, grosor):
    """Mascara (alfa) del texto ya dibujado; se guarda para no redibujarlo cada cuadro."""
    clave = (s, esc, grosor)
    sp = _SPRITES.get(clave)
    if sp is None:
        if len(_SPRITES) > 3000:
            _SPRITES.clear()
        f = _letra(max(8, int(round(ESCALA_LETRA * esc))), grosor >= 2)
        l, t, r, b = f.getbbox(s or ' ', anchor='ls')
        w, h = max(1, r - l + 2), max(1, b - t + 2)
        im = Image.new('L', (w, h), 0)
        ImageDraw.Draw(im).text((1 - l, 1 - t), s, font=f, fill=255, anchor='ls')
        alfa = np.asarray(im, np.float32)[..., None] / 255.0
        avance = int(round(f.getlength(s)))
        sp = (alfa, l - 1, t - 1, avance)
        _SPRITES[clave] = sp
    return sp


def medir(s, esc, grosor=1):
    if PIL_OK:
        return _sprite(s, esc, grosor)[3]
    return cv2.getTextSize(s, FUENTE, esc, grosor)[0][0]


def texto(img, s, org, esc=0.6, color=BLANCO, grosor=1, centro=False, derecha=False):
    if not PIL_OK:
        (w, h), _ = cv2.getTextSize(s, FUENTE, esc, grosor)
        x, y = org
        if centro:
            x -= w // 2
        elif derecha:
            x -= w
        cv2.putText(img, s, (int(x), int(y)), FUENTE, esc, color, grosor, cv2.LINE_AA)
        return w
    alfa, ox, oy, w = _sprite(s, esc, grosor)
    x, y = int(org[0]), int(org[1])
    if centro:
        x -= w // 2
    elif derecha:
        x -= w
    x0, y0 = x + ox, y + oy
    h, ww = alfa.shape[:2]
    H, W = img.shape[:2]
    ax0, ay0 = max(0, -x0), max(0, -y0)
    ax1, ay1 = min(ww, W - x0), min(h, H - y0)
    if ax1 <= ax0 or ay1 <= ay0:
        return w
    a = alfa[ay0:ay1, ax0:ax1]
    zona = img[y0 + ay0:y0 + ay1, x0 + ax0:x0 + ax1]
    zona[:] = (zona * (1 - a) + np.array(color, np.float32) * a).astype(np.uint8)
    return w


def texto_ajustado(img, s, org, ancho_max, esc=0.8, color=BLANCO, grosor=2, salto=36):
    """Escribe s partiendo en renglones para que quepa en ancho_max."""
    renglon, y = '', org[1]
    for palabra in s.split(' '):
        prueba = (renglon + ' ' + palabra).strip()
        if medir(prueba, esc, grosor) > ancho_max and renglon:
            texto(img, renglon, (org[0], y), esc, color, grosor)
            renglon, y = palabra, y + salto
        else:
            renglon = prueba
    texto(img, renglon, (org[0], y), esc, color, grosor)
    return y


def a_lienzo(p):
    """Punto del mapa enderezado (ANCHO x ALTO) -> punto del lienzo."""
    return (int(MAP_X + p[0] * MAP_W / ANCHO), int(MAP_Y + p[1] * MAP_H / ALTO))


def dibujar_margenes(lienzo, var, datos, son, voz, region, valor, vista, en_mapa):
    v = VARIABLES[var]
    # ---------------- margen superior ----------------
    texto(lienzo, T('EARTH JUKEBOX  -  Mapa tactil inclusivo', 'EARTH JUKEBOX  -  Inclusive tactile map'),
          (CANVAS_W // 2, 62), 1.25, BLANCO, 2, centro=True)
    texto(lienzo, f'{T("Escuchando", "Listening")}: {vt(v, "nombre")}   |   {vt(v, "fuente")[0]}' +
          (f'   |   {T("dato del", "data from")} {v["fecha"]}' if v['fecha'] else ''),
          (CANVAS_W // 2, 112), 0.7, v['color'], 2, centro=True)

    # ---------------- margen izquierdo: variables ----------------
    x0 = 25
    texto(lienzo, T('VARIABLES NASA', 'NASA VARIABLES'), (x0, MAP_Y + 30), 0.75, GRIS, 2)
    for i, w in enumerate(VARIABLES):
        y = MAP_Y + 55 + i * 82
        sel = (i == var)
        if sel:
            cv2.rectangle(lienzo, (x0 - 5, y), (MAP_X - 25, y + 68), w['color'], -1)
        cv2.rectangle(lienzo, (x0 - 5, y), (MAP_X - 25, y + 68), w['color'], 2)
        c = (20, 20, 20) if sel else BLANCO
        cv2.rectangle(lienzo, (x0 + 5, y + 12), (x0 + 49, y + 56), c, 2)
        texto(lienzo, w['tecla'], (x0 + 17, y + 47), 1.0, c, 2)
        texto(lienzo, vt(w, 'nombre'), (x0 + 65, y + 32), 0.75, c, 2)
        est = datos.estado[i]
        texto(lienzo, f'{T("timbre", "sound")}: {tr_dic(w["timbre"], TIMBRE_EN)}' +
              ('' if est == 'listo' else f'  ({tr_dic(est, ESTADO_EN)})'),
              (x0 + 65, y + 56), 0.48, c, 1)

    # ---------------- margen derecho: panel de informacion ----------------
    xd, ancho = MAP_X + MAP_W + 25, CANVAS_W - (MAP_X + MAP_W) - 45
    y = MAP_Y + 30
    texto(lienzo, T('LUGAR', 'PLACE'), (xd, y), 0.6, GRIS, 1)
    y = texto_ajustado(lienzo, nombre_mostrar(region), (xd, y + 38), ancho, 0.85, BLANCO, 2, 34)
    y += 55
    texto(lienzo, 'VARIABLE', (xd, y), 0.6, GRIS, 1)
    texto(lienzo, vt(v, 'nombre'), (xd, y + 36), 0.85, v['color'], 2)
    y += 85
    texto(lienzo, T('VALOR EN EL PUNTO', 'VALUE AT THIS POINT'), (xd, y), 0.6, GRIS, 1)
    if not datos.listo(var):
        val_txt = tr_dic(datos.estado[var], ESTADO_EN) + '...'
    elif en_mapa is None:
        val_txt = '--'
    elif valor is None:
        val_txt = T('sin dato aqui', 'no data here')
    else:
        val_txt = v['fmt'](valor)
    texto(lienzo, val_txt, (xd, y + 48), 1.15, BLANCO, 2)
    y += 80
    # barra de colores NASA con la marca del valor
    if datos.listo(var):
        lo, hi = datos.rango[var]
        barra = np.repeat(datos.barra[var][None], 26, 0)
        barra = cv2.resize(barra, (ancho, 26), interpolation=cv2.INTER_NEAREST)
        lienzo[y:y+26, xd:xd+ancho] = barra
        cv2.rectangle(lienzo, (xd, y), (xd + ancho, y + 26), GRIS, 1)
        if valor is not None:
            px = xd + int(datos.normalizar(var, valor) * (ancho - 1))
            cv2.drawMarker(lienzo, (px, y - 4), BLANCO, cv2.MARKER_TRIANGLE_DOWN, 16, 2)
            cv2.line(lienzo, (px, y), (px, y + 26), BLANCO, 2)
        texto(lienzo, v['fmt'](lo) + T(' (grave)', ' (low pitch)'), (xd, y + 50), 0.45, GRIS, 1)
        texto(lienzo, v['fmt'](hi) + T(' (agudo)', ' (high pitch)'), (xd + ancho, y + 50), 0.45, GRIS, 1, derecha=True)
    y += 95
    texto(lienzo, T('FUENTE', 'SOURCE'), (xd, y), 0.6, GRIS, 1)
    for k, linea in enumerate(vt(v, 'fuente') + ([f'{T("fecha", "date")}: {v["fecha"]}'] if v['fecha'] else [T('relieve (dato fijo)', 'terrain (static data)')]) + ['via NASA GIBS / Worldview']):
        texto(lienzo, linea, (xd, y + 30 + 26 * k), 0.5, BLANCO, 1)
    y += 150
    texto(lienzo, 'AUDIO', (xd, y), 0.6, GRIS, 1)
    texto(lienzo, T('SILENCIO', 'MUTED') if son.mudo else (T('hablando...', 'speaking...') if voz.ocupada() else T('activo', 'active')),
          (xd, y + 30), 0.55, BLANCO, 1)
    texto(lienzo, voz.motor[:34], (xd, y + 56), 0.45, GRIS, 1)

    # ---------------- margen inferior ----------------
    texto(lienzo, nombre_mostrar(region), (CANVAS_W // 2, MAP_Y + MAP_H + 70), 1.4, BLANCO, 3, centro=True)
    vista_t = tr_dic(vista, VISTA_EN)
    texto(lienzo, T(f'1 CO2   2 Temperatura   3 Altitud   i = decir valor   s = silencio   v = vista ({vista_t})   '
                    f'g = globo   d = regiones   t = rotar   c = calibrar   L = English   q = salir',
                    f'1 CO2   2 Temperature   3 Elevation   i = say value   s = mute   v = view ({vista_t})   '
                    f'g = globe   d = regions   t = rotate   c = calibrate   L = Espanol   q = quit'),
          (CANVAS_W // 2, CANVAS_H - 25), 0.55, GRIS, 1, centro=True)


def texto_valor_voz(var, region, valor):
    v = VARIABLES[var]
    if valor is None:
        return f'{nombre_voz(region)}. {vt(v, "voz")}: {T("sin datos aquí", "no data here")}'
    return f'{nombre_voz(region)}. {vt(v, "voz")}: {vt(v, "decir")(valor)}'


# ----------------------------------------------------------------------------
class Camara:
    """Abre la camara igual que el programa de la banda: prueba MSMF, DSHOW y AUTO,
    primero pidiendo CAPTURA y, si asi no da imagen, con la resolucion propia de la
    camara. Lee en un hilo aparte y entrega siempre el cuadro mas reciente.
    Tambien acepta una URL (telefono por Wi-Fi) y se reconecta si se corta."""

    def __init__(self, fuente, resolucion=None):
        self.fuente = fuente
        self.resolucion = resolucion
        self.es_ip = isinstance(fuente, str)
        self.cap = None
        self.frame = None
        self.activo = True
        self.lock = threading.Lock()
        self.cap = self._abrir()
        if self.cap is None:
            print(f'No se pudo abrir la camara {fuente}. Cierra la app Camara de Windows / '
                  'la vista previa de DroidCam y revisa el numero en CAMARA.')
            return
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass
        threading.Thread(target=self._leer_continuo, daemon=True).start()

    def _probar(self, api, nombre, resolucion):
        cap = cv2.VideoCapture(self.fuente, api)
        if not cap.isOpened():
            cap.release()
            return None
        if resolucion:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolucion[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucion[1])
        for _ in range(30):                      # hasta ~3 s esperando imagen
            ok, f = cap.read()
            if ok and f is not None:
                txt = f'{resolucion[0]}x{resolucion[1]} pedida' if resolucion else 'resolucion propia'
                print(f'[OK] Camara {self.fuente} con {nombre}: {f.shape[1]}x{f.shape[0]} ({txt})')
                self.frame = f
                return cap
            time.sleep(0.1)
        print(f'   {nombre}' + (f' a {resolucion[0]}x{resolucion[1]}' if resolucion else '') +
              ': abre pero no da imagen, pruebo otra forma...')
        cap.release()
        return None

    def _abrir(self):
        if self.es_ip:
            return self._probar(cv2.CAP_ANY, 'URL', None)
        if sys.platform.startswith('win'):
            backends = [('MSMF', cv2.CAP_MSMF), ('DSHOW', cv2.CAP_DSHOW), ('AUTO', cv2.CAP_ANY)]
        else:
            backends = [('AUTO', cv2.CAP_ANY)]
        for nombre, api in backends:
            for res in ([self.resolucion, None] if self.resolucion else [None]):
                cap = self._probar(api, nombre, res)
                if cap is not None:
                    return cap
        return None

    def _leer_continuo(self):
        fallos = 0
        while self.activo:
            ok, f = self.cap.read()
            if ok and f is not None:
                fallos = 0
                with self.lock:
                    self.frame = f
                continue
            fallos += 1
            time.sleep(0.05)
            if fallos > 40:                      # ~2 s sin imagen: reconectar
                print('Camara sin imagen, reconectando...')
                self.cap.release()
                time.sleep(1)
                nueva = self._abrir()
                if nueva is not None:
                    self.cap = nueva
                fallos = 0

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return True, self.frame.copy()

    def release(self):
        self.activo = False
        time.sleep(0.1)
        if self.cap is not None:
            self.cap.release()


def rotar_cuadro(img, grados):
    codigos = {90: cv2.ROTATE_90_CLOCKWISE, 180: cv2.ROTATE_180, 270: cv2.ROTATE_90_COUNTERCLOCKWISE}
    return cv2.rotate(img, codigos[grados]) if grados in codigos else img


def detectar_franjas(img):
    """Zona util sin las franjas negras de DroidCam (x, y, w, h), o None si no hay."""
    gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cols = np.where(gris.max(axis=0) > 25)[0]
    filas = np.where(gris.max(axis=1) > 25)[0]
    if len(cols) == 0 or len(filas) == 0:
        return None
    x0, x1, y0, y1 = cols[0], cols[-1] + 1, filas[0], filas[-1] + 1
    H, W = gris.shape
    if (x1 - x0) > 0.95 * W and (y1 - y0) > 0.95 * H:
        return None
    m = 2
    return (x0 + m, y0 + m, max(10, x1 - x0 - 2 * m), max(10, y1 - y0 - 2 * m))


def acomodar_horizontal(img, grados, recorte):
    """Rota, quita franjas y mete la imagen en ANCHO x ALTO (horizontal) sin deformarla."""
    img = rotar_cuadro(img, grados)
    if recorte:
        x, y, w, h = recorte
        img = img[y:y + h, x:x + w]
    h, w = img.shape[:2]
    if (w, h) == (ANCHO, ALTO):
        return img
    if LLENAR:                                   # cubrir todo: recorte centrado
        if w / h > ANCHO / ALTO:
            nw = int(round(h * ANCHO / ALTO)); x0 = (w - nw) // 2
            img = img[:, x0:x0 + nw]
        else:
            nh = int(round(w * ALTO / ANCHO)); y0 = (h - nh) // 2
            img = img[y0:y0 + nh, :]
        h, w = img.shape[:2]
        interp = cv2.INTER_AREA if w > ANCHO else cv2.INTER_LINEAR
        return cv2.resize(img, (ANCHO, ALTO), interpolation=interp)
    esc = min(ANCHO / w, ALTO / h)
    nw, nh = max(1, int(round(w * esc))), max(1, int(round(h * esc)))
    interp = cv2.INTER_AREA if esc < 1 else cv2.INTER_LINEAR
    chico = cv2.resize(img, (nw, nh), interpolation=interp)
    lienzo = np.zeros((ALTO, ANCHO, 3), np.uint8)
    x0, y0 = (ANCHO - nw) // 2, (ALTO - nh) // 2
    lienzo[y0:y0 + nh, x0:x0 + nw] = chico
    return lienzo


def main():
    cap = Camara(CAMARA, CAPTURA)
    rotacion = ROTAR
    recorte = None                 # franjas negras: se miden una vez al arrancar
    t_cam = time.time()

    mapa = cargar_mapa()
    etiquetas, nombres, tierra = construir_etiquetas(mapa)
    rng = np.random.RandomState(7)
    colores = rng.randint(60, 255, (len(nombres), 3)).astype(np.uint8)
    capa_color = colores[etiquetas]
    e8 = etiquetas.astype(np.uint8)
    bordes = (cv2.Canny(e8, 0, 1) > 0)
    bordes = cv2.dilate(bordes.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0
    mapa_guia = capa_color.copy()
    mapa_guia[~tierra] = (90, 40, 10)
    mapa_guia[bordes] = (0, 0, 0)
    mini = cv2.resize(mapa, (320, 180))

    globo = Globo(tierra, etiquetas, GLOBO_CX, GLOBO_CY, GLOBO_R)
    detector = DetectorIndice()
    print('Deteccion:', detector.modo)
    datos = DatosNASA()
    audio_ok = iniciar_audio()
    voz = Voz(audio_ok)
    son = Sonificador(voz)
    voz.pregenerar([nombre_voz(n) for n in nombres] + [vt(v, 'voz') for v in VARIABLES])
    calib = Calibracion()

    win = 'Earth Jukebox - Mapa Tactil 3D'
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    estado = {'calibrando': not calib.lista}
    def raton(ev, x, y, flags, param):
        if estado['calibrando']:
            if ev == cv2.EVENT_LBUTTONDOWN and x >= ANCHO:
                return
            calib.raton(ev, x, y)
    cv2.setMouseCallback(win, raton)

    ver_colores = False
    ver_guia = False
    vista = 0
    ver_ajuste = ver_datos = -1
    voz.decir(T('Mapa táctil listo. Variable: ', 'Tactile map ready. Variable: ') + vt(VARIABLES[son.var], 'voz'))

    while True:
        ok, cam = cap.read()
        if not ok:
            print('No se pudo acceder a la webcam.'); break
        if recorte is None and QUITAR_FRANJAS and time.time() - t_cam > 0.8:
            recorte = detectar_franjas(rotar_cuadro(cam, rotacion)) or False
        frame = acomodar_horizontal(cam, rotacion, recorte or None)
        if ESPEJO:
            frame = cv2.flip(frame, 1)

        # Capas deformadas para coincidir con el mapa impreso (se recalculan solo si cambia algo)
        if calib.version != ver_ajuste:
            ver_ajuste = calib.version
            mx, my = calib.mapx, calib.mapy
            rep = cv2.BORDER_REPLICATE
            etq_P = cv2.remap(etiquetas, mx, my, cv2.INTER_NEAREST, borderMode=rep)
            capa_P = cv2.remap(capa_color, mx, my, cv2.INTER_NEAREST, borderMode=rep)
            guia_P = cv2.remap(mapa_guia, mx, my, cv2.INTER_NEAREST, borderMode=rep)
            bordes_P = cv2.remap(bordes.astype(np.uint8), mx, my, cv2.INTER_NEAREST, borderMode=rep) > 0
            lon_P, lat_P = ref_a_lonlat(mx, my)
            etq_M = cv2.resize(etq_P, (MAP_W, MAP_H), interpolation=cv2.INTER_NEAREST)
            capa_M = cv2.resize(capa_P, (MAP_W, MAP_H), interpolation=cv2.INTER_NEAREST)
            bordes_M = cv2.resize(bordes_P.astype(np.uint8), (MAP_W, MAP_H), interpolation=cv2.INTER_NEAREST) > 0
            ver_datos = -1
        if datos.version != ver_datos:            # imagenes NASA llevadas al mapa impreso
            ver_datos = datos.version
            lon_M = cv2.resize(lon_P.astype(np.float32), (MAP_W, MAP_H))
            lat_M = cv2.resize(lat_P.astype(np.float32), (MAP_W, MAP_H))
            dx = (((lon_M + 180.0) % 360.0) * DATA_W / 360.0).astype(np.float32)
            dy = np.clip((90.0 - lat_M) * DATA_H / 180.0, 0, DATA_H - 1).astype(np.float32)
            datos_M = [cv2.remap(datos.imagen[i], dx, dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
                       if datos.listo(i) else None for i in range(len(VARIABLES))]

        # 1) dedo en la camara -> 2) punto en el mapa -> 3) lugar y dato NASA
        puntas = detector.puntas(frame)
        en_mapa = None
        for (px, py) in puntas:
            en_mapa = calib.a_mapa(px, py)
            if en_mapa is not None:
                break

        rid = en_ref = valor = norm = None
        if en_mapa is not None:
            x, y = en_mapa
            rid = int(etq_P[y, x])
            region = nombres[rid]
            en_ref = calib.a_ref(en_mapa)
            valor = datos.valor(son.var, float(lon_P[y, x]), float(lat_P[y, x]))
            if valor is not None:
                norm = datos.normalizar(son.var, valor)
        elif puntas and calib.lista:
            region = T('Fuera del mapa', 'Off the map')
        elif not calib.lista:
            region = T('Falta calibrar', 'Calibration needed')
        else:
            region = T('Toca el mapa...', 'Touch the map...')

        son.actualizar(region if en_mapa is not None else None, norm, en_mapa is not None)

        # ------------------------- MODO CALIBRACION -------------------------
        if estado['calibrando']:
            vis = dibujar_calibracion(frame, calib, guia_P, ver_guia, mini)
            for (px, py) in puntas:
                cv2.circle(vis, (px, py), 10, (0, 0, 255), -1)
                cv2.circle(vis, (px, py), 16, (255, 255, 255), 2)
            texto(vis, f'{T("Lugar", "Place")}: {nombre_mostrar(region)}', (20, ALTO - 25), 0.8, (0, 0, 0), 5)
            texto(vis, f'{T("Lugar", "Place")}: {nombre_mostrar(region)}', (20, ALTO - 25), 0.8, BLANCO, 2)
        # ---------------------------- MODO USO ------------------------------
        else:
            vis = np.full((CANVAS_H, CANVAS_W, 3), FONDO, np.uint8)
            esc = np.array([[MAP_W / ANCHO, 0, 0], [0, MAP_H / ALTO, 0], [0, 0, 1]])
            cam_M = cv2.warpPerspective(frame, esc @ calib.H, (MAP_W, MAP_H))
            dat_M = datos_M[son.var]
            if VISTAS[vista] == 'camara' or dat_M is None:
                zona = cam_M
            elif VISTAS[vista] == 'datos NASA':
                zona = dat_M.copy()
            else:
                zona = cv2.addWeighted(cam_M, 0.5, dat_M, 0.5, 0)
            if ver_colores:
                zona = cv2.addWeighted(zona, 0.55, capa_M, 0.45, 0)
                zona[bordes_M] = (0, 0, 0)
                if rid is not None:
                    resalta = etq_M == rid
                    zona[resalta] = cv2.addWeighted(zona, 0.6, np.full_like(zona, 255), 0.4, 0)[resalta]
            vis[MAP_Y:MAP_Y+MAP_H, MAP_X:MAP_X+MAP_W] = zona
            cv2.rectangle(vis, (MAP_X - 2, MAP_Y - 2), (MAP_X + MAP_W + 1, MAP_Y + MAP_H + 1), GRIS, 2)
            if en_mapa is not None:
                p = a_lienzo(en_mapa)
                cv2.circle(vis, p, 12, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(vis, p, 18, BLANCO, 2, cv2.LINE_AA)
            dibujar_margenes(vis, son.var, datos, son, voz, region, valor, VISTAS[vista], en_mapa)
            globo.dibujar(vis, en_ref, rid)

        cv2.imshow(win, vis)
        t = cv2.waitKey(1) & 0xFF
        if t in (ord('q'), 27): break
        if t == ord('c'):
            estado['calibrando'] = not estado['calibrando'] or not calib.lista
            continue
        if estado['calibrando']:
            if t == ord('p') and calib.lista:
                calib.modo_puntos = not calib.modo_puntos
            if calib.modo_puntos and calib.lista:
                if t == 32 and puntas: calib.agregar_punto(*puntas[0])   # ESPACIO = dedo
                if t == ord('n'): calib.k = (calib.k + 1) % len(PUNTOS_REF)
                if t == ord('b'): calib.k = (calib.k - 1) % len(PUNTOS_REF)
                if t == ord('x'): calib.borrar_punto()
                if t == ord('z'): calib.borrar_punto(todos=True)
            if t == ord('r'): calib.reiniciar()
            if t == ord('m'): ver_guia = not ver_guia
            if t in (ord('1'), ord('2'), ord('3'), ord('4')): calib.sel = t - ord('1')
            if t == ord('i'): calib.mover(0, -1)
            if t == ord('k'): calib.mover(0, 1)
            if t == ord('j'): calib.mover(-1, 0)
            if t == ord('l'): calib.mover(1, 0)
            if t in (13, 10) and calib.guardar():      # ENTER
                estado['calibrando'] = False
                calib.modo_puntos = False
        else:
            for i, v in enumerate(VARIABLES):
                if t == ord(v['tecla']):
                    son.seleccionar(i)
            if t == ord('i'):
                if en_mapa is not None:
                    voz.decir(texto_valor_voz(son.var, region, valor))
                else:
                    voz.decir(f'{vt(VARIABLES[son.var], "voz")}. ' +
                              T('Toca el mapa para escuchar el dato', 'Touch the map to hear the value'))
            if t == ord('s'):
                son.mudo = voz.mudo = not son.mudo
                if son.mudo:
                    if audio_ok:
                        pygame.mixer.stop(); pygame.mixer.music.stop()
                print('Sonido', 'apagado' if son.mudo else 'encendido')
            if t == ord('g'): globo.seguir = not globo.seguir
            if t == ord('d'): ver_colores = not ver_colores
            if t == ord('v'): vista = (vista + 1) % len(VISTAS)
            if t in (ord('l'), ord('L')):
                cambiar_idioma()
                voz.pregenerar([nombre_voz(n) for n in nombres] + [vt(v, 'voz') for v in VARIABLES])
                voz.decir(T('Español', 'English'))
            if t == ord('t'):
                rotacion = (rotacion + 90) % 360
                recorte, t_cam = None, time.time()
                print(f'Rotacion de camara: {rotacion} grados (recalibra con c si cambiaste)')

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
