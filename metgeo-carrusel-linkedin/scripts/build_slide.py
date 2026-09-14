"""
build_slide.py — Primitivas de diseño de la plantilla DEFINITIVA de MetGeo Spa.

Estos valores fueron extraídos por muestreo de píxeles del PDF de referencia
(MetGeo_carrusel_geofisica_biobio.pdf) — no son una aproximación a ojo.
No editar salvo que la plantilla de marca cambie oficialmente.
"""
import os
import random
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

# --- Lienzo ---
W, H = 1080, 1350
MARGEN = 80

# --- Paleta (muestreada del PDF definitivo) ---
NAVY_TOP = (12, 45, 87)        # #0C2D57 — arriba del degradado
NAVY_BOTTOM = (5, 26, 53)      # #051A35 — abajo del degradado
ACCENT = (36, 119, 184)        # #2477B8 — subrayados, barras, tarjetas, paginación activa
LABEL_BLUE = (159, 202, 236)   # #9FCAEC — kickers y labels en mayúscula
WHITE = (255, 255, 255)
BODY_TEXT = (225, 236, 247)    # blanco levemente azulado — párrafos de cuerpo
DOT_LINE = (61, 110, 158)      # patrón de puntos/constelación de fondo

# --- Datos fijos de MetGeo Spa ---
CONTACTO_EMAIL = "metgeo.spa@gmail.com"
CONTACTO_WHATSAPP = "+56 9 7922 6274"
TAGLINE_CONTACTO = "Ciencia de datos para decisiones que protegen el territorio"

_DIR_SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(_DIR_SKILL, "assets", "MetGeo_logo2.png")


# ---------------------------------------------------------------------------
# Fuentes
# ---------------------------------------------------------------------------
def _fuente(tamaño, bold=True):
    candidatos_bold = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
        "/usr/share/fonts/truetype/google-fonts/Montserrat-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidatos_regular = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
        "/usr/share/fonts/truetype/google-fonts/Montserrat-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    candidatos_semibold = [
        "/usr/share/fonts/truetype/google-fonts/Poppins-SemiBold.ttf",
        "/usr/share/fonts/truetype/google-fonts/Montserrat-SemiBold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    lista = candidatos_bold if bold else candidatos_regular
    for ruta in lista:
        if os.path.exists(ruta):
            return ImageFont.truetype(ruta, tamaño)
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Fondo: degradado navy + patrón de puntos/constelación
# ---------------------------------------------------------------------------
def slide_base(semilla=None):
    """Lienzo con el degradado vertical navy de la plantilla + patrón de puntos.
    semilla fija la posición de los puntos para que sea reproducible; si es None
    se usa un valor fijo (misma 'textura' en todas las slides de un mismo set)."""
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(NAVY_TOP[0] + (NAVY_BOTTOM[0] - NAVY_TOP[0]) * t)
        g = int(NAVY_TOP[1] + (NAVY_BOTTOM[1] - NAVY_TOP[1]) * t)
        b = int(NAVY_TOP[2] + (NAVY_BOTTOM[2] - NAVY_TOP[2]) * t)
        for x in range(0, W, 1):
            px[x, y] = (r, g, b)
    img = _patron_constelacion(img, semilla=semilla)
    return img


def _patron_constelacion(img, semilla=None, n_puntos=34, radio_conexion=190):
    rnd = random.Random(semilla if semilla is not None else 42)
    puntos = [(rnd.randint(0, W), rnd.randint(0, H)) for _ in range(n_puntos)]
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(capa)
    for i, p1 in enumerate(puntos):
        for p2 in puntos[i + 1:]:
            d = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5
            if d < radio_conexion:
                alpha = int(50 * (1 - d / radio_conexion))
                draw.line([p1, p2], fill=DOT_LINE + (alpha,), width=1)
    for p in puntos:
        draw.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=DOT_LINE + (110,))
    return Image.alpha_composite(img.convert("RGBA"), capa).convert("RGB")


def fondo_mapa(slide, img_path, alpha=130, recorte=(0.0, 0.0, 0.0, 0.0),
               fade_inicio=0.55, fade_fin=0.88):
    """Superpone una imagen (mapa/gráfico) semi-transparente a pantalla completa,
    con un desvanecimiento vertical hacia el navy en la parte baja (donde van los
    chips y el pie de página), igual que en la plantilla de referencia.

    recorte = (izq, arriba, der, abajo) como fracción 0-1 a recortar de la imagen
    ORIGINAL antes de encajarla — útil para descartar la barra de color o ejes
    de un gráfico técnico que no aportan a la portada.
    """
    mapa = Image.open(img_path).convert("RGB")
    w0, h0 = mapa.size
    l, t, r, b = recorte
    mapa = mapa.crop((int(w0 * l), int(h0 * t), int(w0 * (1 - r)), int(h0 * (1 - b))))
    mapa = ImageOps.fit(mapa, (W, H), method=Image.LANCZOS, centering=(0.5, 0.3))

    # máscara de desvanecimiento vertical: alpha llano arriba, cae a 0 hacia abajo
    mask = Image.new("L", (W, H), 0)
    mpx = mask.load()
    y_ini = int(H * fade_inicio)
    y_fin = int(H * fade_fin)
    for y in range(H):
        if y < y_ini:
            a = alpha
        elif y > y_fin:
            a = 0
        else:
            a = int(alpha * (1 - (y - y_ini) / (y_fin - y_ini)))
        for x in range(0, W, 1):
            mpx[x, y] = a

    mapa_rgba = mapa.convert("RGBA")
    mapa_rgba.putalpha(mask)
    return Image.alpha_composite(slide.convert("RGBA"), mapa_rgba).convert("RGB")


# ---------------------------------------------------------------------------
# Texto con tracking (letter-spacing) para kickers/labels en mayúscula
# ---------------------------------------------------------------------------
def texto_tracking(draw, xy, texto, font, fill, tracking=3):
    x, y = xy
    for ch in texto:
        draw.text((x, y), ch, font=font, fill=fill)
        w = draw.textlength(ch, font=font)
        x += w + tracking
    return x


def _ancho_tracking(draw, texto, font, tracking=3):
    x = 0
    for ch in texto:
        x += draw.textlength(ch, font=font) + tracking
    return x - tracking


# ---------------------------------------------------------------------------
# Header: kicker numerado + subrayado, logo
# ---------------------------------------------------------------------------
def kicker(slide, texto, numero=None, y=76):
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(19, bold=True)
    texto_completo = f"{numero} — {texto}" if numero else texto
    texto_tracking(draw, (MARGEN, y), texto_completo.upper(), fuente, WHITE if False else LABEL_BLUE, tracking=2)
    draw.line([(MARGEN, y + 38), (MARGEN + 110, y + 38)], fill=ACCENT, width=3)
    return slide


def logo_esquina(slide, tamaño=84, logo_path=LOGO_PATH):
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((tamaño, tamaño), Image.LANCZOS)
    slide.paste(logo, (W - MARGEN - logo.width, MARGEN - 10), logo)
    return slide


def logo_centrado(slide, tamaño=300, y_top=280, logo_path=LOGO_PATH):
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((tamaño, tamaño), Image.LANCZOS)
    x = (W - logo.width) // 2
    slide.paste(logo, (x, y_top), logo)
    return slide, y_top + logo.height


# ---------------------------------------------------------------------------
# Título y párrafo (alineados a la izquierda, como en la plantilla)
# ---------------------------------------------------------------------------
def titulo(slide, texto, y, tamaño_fuente=52, color=WHITE, ancho_max=W - 2 * MARGEN, interlineado=1.16):
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(tamaño_fuente, bold=True)
    caracteres_por_linea = max(8, int(ancho_max / (tamaño_fuente * 0.56)))
    lineas = textwrap.wrap(texto, width=caracteres_por_linea)
    y_actual = y
    for linea in lineas:
        draw.text((MARGEN, y_actual), linea, font=fuente, fill=color)
        y_actual += int(tamaño_fuente * interlineado)
    return slide, y_actual


def parrafo(slide, texto, y, tamaño_fuente=25, color=BODY_TEXT, ancho_max=W - 2 * MARGEN, interlineado=1.4):
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(tamaño_fuente, bold=False)
    caracteres_por_linea = max(10, int(ancho_max / (tamaño_fuente * 0.52)))
    lineas = textwrap.wrap(texto, width=caracteres_por_linea)
    y_actual = y
    for linea in lineas:
        draw.text((MARGEN, y_actual), linea, font=fuente, fill=color)
        y_actual += int(tamaño_fuente * interlineado)
    return slide, y_actual


def etiqueta_mayuscula(slide, texto, y, tamaño_fuente=19, color=LABEL_BLUE, tracking=2):
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(tamaño_fuente, bold=True)
    texto_tracking(draw, (MARGEN, y), texto.upper(), fuente, color, tracking=tracking)
    return slide, y + int(tamaño_fuente * 1.5)


def cifra_con_barra(slide, cifra, y, tamaño_fuente=64, color=WHITE):
    """Cifra grande con una barra vertical de acento a la izquierda (no un badge)."""
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(tamaño_fuente, bold=True)
    bbox = draw.textbbox((0, 0), cifra, font=fuente)
    alto_texto = bbox[3] - bbox[1]
    x_texto = MARGEN + 26
    draw.rectangle([MARGEN, y, MARGEN + 6, y + alto_texto + 10], fill=ACCENT)
    draw.text((x_texto, y - bbox[1]), cifra, font=fuente, fill=color)
    return slide, y + alto_texto + 30


# ---------------------------------------------------------------------------
# Tarjeta blanca con gráfico + barra de acento superior + línea "FUENTE"
# ---------------------------------------------------------------------------
def tarjeta_grafico(slide, img_path, y_top, alto_max, fuente_texto=None, ancho_max=W - 2 * MARGEN):
    img = Image.open(img_path).convert("RGB")
    img.thumbnail((ancho_max, alto_max), Image.LANCZOS)
    x = (W - img.width) // 2
    draw = ImageDraw.Draw(slide)
    pad = 20
    caja = [x - pad, y_top - pad, x + img.width + pad, y_top + img.height + pad]
    # barra de acento justo encima de la tarjeta
    draw.rounded_rectangle([caja[0], caja[1] - 8, caja[2], caja[1] + 10], radius=6, fill=ACCENT)
    draw.rounded_rectangle(caja, radius=20, fill=WHITE)
    slide.paste(img, (x, y_top))
    y_bottom = caja[3] + 22
    if fuente_texto:
        f_bold = _fuente(18, bold=True)
        f_reg = _fuente(18, bold=False)
        draw.text((MARGEN, y_bottom), "FUENTE", font=f_bold, fill=WHITE)
        ancho_fuente_label = draw.textlength("FUENTE  ", font=f_bold)
        draw.text((MARGEN + ancho_fuente_label, y_bottom), fuente_texto, font=f_reg, fill=BODY_TEXT)
        y_bottom += 30
    return slide, y_bottom


# ---------------------------------------------------------------------------
# Chips (estadística con barra de acento + valor + caption)
# ---------------------------------------------------------------------------
def chip(slide, x, y, ancho, alto, valor, caption, tamaño_valor=26, tamaño_caption=14):
    draw = ImageDraw.Draw(slide)
    draw.rounded_rectangle([x, y, x + ancho, y + alto], radius=10,
                            outline=(255, 255, 255, 60), width=1)
    # PIL no soporta outline con alpha directo sobre RGB -> usar color sólido tenue
    draw.rounded_rectangle([x, y, x + ancho, y + alto], radius=10, outline=(90, 130, 170), width=1)
    draw.rounded_rectangle([x, y, x + 5, y + alto], radius=3, fill=ACCENT)
    f_valor = _fuente(tamaño_valor, bold=True)
    f_caption = _fuente(tamaño_caption, bold=True)
    draw.text((x + 22, y + 12), valor, font=f_valor, fill=WHITE)
    texto_tracking(draw, (x + 22, y + 12 + tamaño_valor + 6), caption.upper(), f_caption, LABEL_BLUE, tracking=1)
    return slide


def fila_chips(slide, chips, y, ancho_total=W - 2 * MARGEN, alto=100, gap=18):
    n = len(chips)
    ancho_chip = (ancho_total - gap * (n - 1)) / n
    x = MARGEN
    for valor, caption in chips:
        chip(slide, x, y, ancho_chip, alto, valor, caption)
        x += ancho_chip + gap
    return slide, y + alto


def chip_contacto(slide, y, label, valor, tamaño_valor=30):
    draw = ImageDraw.Draw(slide)
    draw.rectangle([MARGEN, y, MARGEN + 5, y + 62], fill=ACCENT)
    f_label = _fuente(17, bold=True)
    f_valor = _fuente(tamaño_valor, bold=True)
    texto_tracking(draw, (MARGEN + 26, y), label.upper(), f_label, LABEL_BLUE, tracking=1)
    draw.text((MARGEN + 26, y + 26), valor, font=f_valor, fill=WHITE)
    return slide, y + 62 + 22


# ---------------------------------------------------------------------------
# Footer: paginación, wordmark, botón "Desliza"
# ---------------------------------------------------------------------------
def paginacion(slide, pagina_actual, total_paginas, y=None):
    """pagina_actual es 1-indexado."""
    if y is None:
        y = H - 60
    draw = ImageDraw.Draw(slide)
    x = MARGEN
    for i in range(1, total_paginas + 1):
        if i == pagina_actual:
            draw.rounded_rectangle([x, y, x + 26, y + 10], radius=5, fill=(180, 215, 245))
            x += 26 + 10
        else:
            draw.ellipse([x, y, x + 10, y + 10], fill=ACCENT + (0,) if False else ACCENT)
            x += 10 + 10
    return slide


def wordmark(slide, y=None):
    if y is None:
        y = H - 62
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(24, bold=True)
    texto = "MetGeo"
    ancho = draw.textlength(texto, font=fuente)
    draw.text((W - MARGEN - ancho, y), texto, font=fuente, fill=WHITE)
    return slide


def boton_desliza(slide, y=None):
    if y is None:
        y = H - 68
    draw = ImageDraw.Draw(slide)
    fuente = _fuente(24, bold=True)
    texto = "DESLIZA"
    ancho = draw.textlength(texto, font=fuente)
    x_texto = W - MARGEN - ancho - 26
    draw.text((x_texto, y), texto, font=fuente, fill=WHITE)
    # triángulo apuntando a la derecha
    tx = W - MARGEN - 16
    ty = y + 12
    draw.polygon([(tx - 14, ty - 11), (tx - 14, ty + 11), (tx + 6, ty)], fill=ACCENT)
    return slide


def linea_divisoria(slide, y, ancho=110, color=ACCENT):
    draw = ImageDraw.Draw(slide)
    draw.line([(MARGEN, y), (MARGEN + ancho, y)], fill=color, width=2)
    return slide, y + 30
