---
name: metgeo-carrusel-linkedin
description: Genera un PDF tipo carrusel para la página de LinkedIn de MetGeo Spa (formato "documento"), siguiendo la plantilla de marca DEFINITIVA (fondo degradado navy con patrón de constelación, kickers numerados, chips de cifras, barra de acento junto a cifras grandes, tarjetas blancas para gráficos con línea "FUENTE", paginación, página de contacto). Usar cuando el usuario pida armar un carrusel, publicación o documento de LinkedIn para MetGeo a partir de un informe/peritaje y sus figuras.
allowed-tools: Bash(python3 *)
---

# Carrusel de LinkedIn — MetGeo Spa (plantilla definitiva)

Esta skill reproduce exactamente la plantilla usada en
`MetGeo_carrusel_geofisica_biobio.pdf` (fondo, tipografía, colores, chips,
paginación, página de contacto), extraída por muestreo directo de píxeles de
ese PDF — no es una aproximación.

**Lo que NO cambia entre publicaciones** (fijo en `scripts/build_slide.py`):
dimensiones (1080×1350 px), degradado navy de fondo, patrón de puntos/constelación,
paleta de colores, tipografía, logo, y en la página de contacto: el tagline
("Ciencia de datos para decisiones que protegen el territorio"), correo y WhatsApp.

**Lo que SÍ cambia en cada publicación:** portada, kickers, títulos, párrafos,
cifras, qué imágenes se usan, y cuántas páginas tiene el carrusel — todo eso vive
en un `config.json` nuevo por caso. Nunca hay que tocar el código para un caso
nuevo.

## Cómo usarla

1. Reunir las imágenes del caso (mapas, gráficos) con sus rutas.
2. Escribir un `config.json` con la lista de `slides` (ver tipos abajo y
   `scripts/config_ejemplo.json`, que reproduce el caso Biobío con los 4 tipos).
3. Ejecutar:
   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/generar_carrusel.py config.json salida.pdf
   ```
   Genera `salida.pdf` y además cada página como PNG suelto en `slides_png/`
   (junto a `salida.pdf`) para revisar antes de publicar.
4. **Revisar los PNG antes de dar por bueno el PDF**: que ninguna cifra/texto
   se corte, que el gráfico se lea bien dentro de la tarjeta blanca, que la
   paginación (puntos abajo a la izquierda) sea correcta.
5. Subir el PDF a LinkedIn como publicación tipo **"Documento"**. El texto del
   post (caption) va aparte, no dentro del PDF.

## Tipos de slide (campo `"tipo"`)

| tipo | Campos principales | Uso |
|---|---|---|
| `portada` | `kicker`, `imagen_fondo`, `titulo`, `subtitulo`, `chips` (lista de `{valor, caption}`, normalmente 3) | Página 1 — mapa/gráfico de fondo semi-transparente con desvanecimiento hacia abajo, 3 chips de cifras clave, botón "Desliza" |
| `contexto` | `kicker`, `numero`, `titulo`, `texto`, `imagen`, `fuente` | Sección explicativa con gráfico, SIN cifra grande (ej. marco sinóptico) |
| `hallazgo` | `kicker`, `numero`, `label`, `cifra`, `texto`, `imagen`, `fuente` | Cifra grande con barra de acento a la izquierda + gráfico de respaldo |
| `contacto` | `tagline` (opcional, usa el fijo si se omite), `correo`, `whatsapp`, `cierre` | Última página: logo grande centrado, tagline, chips de correo/WhatsApp |

Notas:
- `imagen`/`imagen_fondo`: rutas relativas al propio `config.json`, o absolutas.
- `imagen_fondo` de portada por defecto recorta 16% arriba (título/ejes propios
  del gráfico) y 14% a la derecha (barra de color), vía `recorte_fondo:
  [izq, arriba, der, abajo]` si algún gráfico necesita otro recorte.
- La paginación y el conteo de páginas son automáticos: el script arma primero
  todas las slides definidas y luego calcula cuántos puntos van en cada una.
  **El largo del carrusel es libre** — el config puede tener 3 páginas o 12.

## Archivos

- `scripts/build_slide.py` — primitivas de la plantilla (fijo, no editar caso a caso)
- `scripts/generar_carrusel.py` — arma las slides desde el JSON y exporta el PDF
- `scripts/config_ejemplo.json` — ejemplo funcional (caso Biobío, 4 páginas)
- `assets/MetGeo_logo2.png` — logo oficial
