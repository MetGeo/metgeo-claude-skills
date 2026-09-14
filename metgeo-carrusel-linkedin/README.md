# Skill: metgeo-carrusel-linkedin

Genera carruseles PDF para LinkedIn con la plantilla definitiva de MetGeo Spa
(la misma de `MetGeo_carrusel_geofisica_biobio.pdf`): mismo fondo, misma
tipografía, mismos chips, misma paginación, misma página de contacto.

## Instalación

```bash
# Personal (disponible en todos tus proyectos en esta máquina)
cp -r metgeo-carrusel-linkedin ~/.claude/skills/

# De proyecto (se comparte con el equipo si el repo va a git)
cp -r metgeo-carrusel-linkedin .claude/skills/
```

Prueba escribiendo en el chat de Claude Code: *"genera el carrusel de LinkedIn
para [caso]"*, o invócala directo con `/metgeo-carrusel-linkedin`.

## Nota sobre `scripts/config_ejemplo.json`

Las rutas de imagen del ejemplo apuntan a archivos usados durante el desarrollo
de esta skill y no existen en tu máquina — es solo referencia del formato del
JSON y de los 4 tipos de slide disponibles. Para un caso nuevo, escribe un
config con las rutas a las imágenes de ese caso.

## Qué NO tocar entre publicaciones

`scripts/build_slide.py` tiene el formato fijo de marca (colores, degradado,
patrón de fondo, logo, tagline de contacto, correo, WhatsApp). Si el día de
mañana cambia el logo, el tagline o el contacto de MetGeo, se edita una sola
vez ahí — no en cada publicación.
