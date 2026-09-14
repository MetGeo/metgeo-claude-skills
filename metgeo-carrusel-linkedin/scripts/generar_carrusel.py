#!/usr/bin/env python3
"""
generar_carrusel.py — Arma el carrusel PDF de LinkedIn de MetGeo Spa, siguiendo
la plantilla DEFINITIVA (extraída de MetGeo_carrusel_geofisica_biobio.pdf).

El FORMATO (dimensiones, fondo degradado + constelación, tipografía, chips,
paginación, franja de contacto) vive en build_slide.py y es fijo.
El CONTENIDO de cada publicación (títulos, cifras, párrafos, qué imágenes usar,
y cuántas páginas tiene) se describe en un config.json distinto por caso.

Uso:
    python3 generar_carrusel.py config.json salida.pdf
"""
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_slide as bs

FOOTER_Y = bs.H - 70  # techo de la franja de paginación/wordmark/desliza


def _resolver_ruta(base_dir, ruta):
    if ruta and not os.path.isabs(ruta):
        return os.path.join(base_dir, ruta)
    return ruta


def armar_portada(cfg, base_dir, pagina, total):
    slide = bs.slide_base()
    img_fondo = _resolver_ruta(base_dir, cfg.get("imagen_fondo"))
    if img_fondo:
        recorte = tuple(cfg.get("recorte_fondo", (0.0, 0.16, 0.14, 0.0)))  # por defecto descarta título propio del gráfico + fila de ejes (arriba) y la barra de color (derecha)
        slide = bs.fondo_mapa(slide, img_fondo, alpha=cfg.get("alpha_fondo", 95), recorte=recorte, fade_inicio=0.42)
    slide = bs.kicker(slide, cfg.get("kicker", ""), numero=None)
    slide = bs.logo_esquina(slide)
    _, y = bs.titulo(slide, cfg.get("titulo", ""), y=250, tamaño_fuente=52)
    if cfg.get("subtitulo"):
        _, y = bs.parrafo(slide, cfg["subtitulo"], y=y + 14, tamaño_fuente=25, color=bs.LABEL_BLUE)
    if cfg.get("chips"):
        chips = [(c["valor"], c["caption"]) for c in cfg["chips"]]
        y_chips = max(y + 60, bs.H - 260)
        bs.fila_chips(slide, chips, y=y_chips)
    slide = bs.paginacion(slide, pagina, total)
    slide = bs.boton_desliza(slide)
    return slide


def armar_contexto(cfg, base_dir, pagina, total):
    """Headline + párrafo + gráfico, SIN cifra grande (ej. marco sinóptico)."""
    slide = bs.slide_base()
    slide = bs.kicker(slide, cfg.get("kicker", ""), numero=cfg.get("numero"))
    slide = bs.logo_esquina(slide)
    y = 150
    _, y = bs.titulo(slide, cfg.get("titulo", ""), y=y, tamaño_fuente=40)
    y += 6
    if cfg.get("texto"):
        _, y = bs.parrafo(slide, cfg["texto"], y=y, tamaño_fuente=24)
    y += 45
    img = _resolver_ruta(base_dir, cfg.get("imagen"))
    if img:
        alto_max = FOOTER_Y - y - 60
        slide, y = bs.tarjeta_grafico(slide, img, y_top=y, alto_max=alto_max,
                                       fuente_texto=cfg.get("fuente"))
    slide = bs.paginacion(slide, pagina, total)
    slide = bs.wordmark(slide)
    return slide


def armar_hallazgo(cfg, base_dir, pagina, total):
    """Label + cifra grande con barra de acento + párrafo + gráfico + fuente."""
    slide = bs.slide_base()
    slide = bs.kicker(slide, cfg.get("kicker", ""), numero=cfg.get("numero"))
    slide = bs.logo_esquina(slide)
    y = 150
    if cfg.get("label"):
        _, y = bs.etiqueta_mayuscula(slide, cfg["label"], y=y)
        y += 6
    if cfg.get("cifra"):
        _, y = bs.cifra_con_barra(slide, cfg["cifra"], y=y, tamaño_fuente=60)
    y += 6
    if cfg.get("texto"):
        _, y = bs.parrafo(slide, cfg["texto"], y=y, tamaño_fuente=24)
    y += 45
    img = _resolver_ruta(base_dir, cfg.get("imagen"))
    if img:
        alto_max = FOOTER_Y - y - 60
        slide, y = bs.tarjeta_grafico(slide, img, y_top=y, alto_max=alto_max,
                                       fuente_texto=cfg.get("fuente"))
    slide = bs.paginacion(slide, pagina, total)
    slide = bs.wordmark(slide)
    return slide


def armar_contacto(cfg, base_dir, pagina, total):
    slide = bs.slide_base()
    slide = bs.kicker(slide, "CONTACTO", numero=None)
    _, y = bs.logo_centrado(slide, tamaño=300, y_top=270)
    y += 60
    tagline = cfg.get("tagline", bs.TAGLINE_CONTACTO)
    _, y = bs.titulo(slide, tagline, y=y, tamaño_fuente=32, ancho_max=bs.W - 2 * bs.MARGEN)
    y += 30
    slide, y = bs.chip_contacto(slide, y, "Correo", cfg.get("correo", bs.CONTACTO_EMAIL))
    slide, y = bs.chip_contacto(slide, y, "WhatsApp", cfg.get("whatsapp", bs.CONTACTO_WHATSAPP))
    y += 10
    slide, y = bs.linea_divisoria(slide, y)
    if cfg.get("cierre"):
        bs.parrafo(slide, cfg["cierre"], y=y, tamaño_fuente=22, color=bs.LABEL_BLUE)
    slide = bs.paginacion(slide, pagina, total)
    return slide


DISPATCH = {
    "portada": armar_portada,
    "contexto": armar_contexto,
    "hallazgo": armar_hallazgo,
    "contacto": armar_contacto,
}


def generar(config_path, salida_pdf):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    base_dir = os.path.dirname(os.path.abspath(config_path))
    slides_cfg = config["slides"]
    total = len(slides_cfg)
    if total == 0:
        raise ValueError("El config no define ninguna slide en 'slides'.")

    slides = []
    for i, cfg in enumerate(slides_cfg, start=1):
        tipo = cfg.get("tipo")
        if tipo not in DISPATCH:
            raise ValueError(f"Tipo de slide desconocido: {tipo!r} (usar: {list(DISPATCH)})")
        slides.append(DISPATCH[tipo](cfg, base_dir, i, total))

    slides_rgb = [s.convert("RGB") for s in slides]
    slides_rgb[0].save(salida_pdf, save_all=True, append_images=slides_rgb[1:], resolution=150.0)
    print(f"Generado {salida_pdf} ({total} páginas)")

    carpeta_png = os.path.join(os.path.dirname(os.path.abspath(salida_pdf)) or ".", "slides_png")
    os.makedirs(carpeta_png, exist_ok=True)
    for i, s in enumerate(slides_rgb, start=1):
        s.save(os.path.join(carpeta_png, f"slide_{i}.png"))
    print(f"Vistas previas guardadas en {carpeta_png}/")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 generar_carrusel.py config.json salida.pdf")
        sys.exit(1)
    generar(sys.argv[1], sys.argv[2])
