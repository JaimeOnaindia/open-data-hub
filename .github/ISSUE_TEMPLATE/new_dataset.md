---
name: Nuevo dataset
about: Añadir un dataset a un país que ya existe en el hub
title: "[dataset] <cc> · <tema>"
labels: ["new-dataset", "good first issue"]
---

## País

<!-- Código ISO + nombre. Debe estar ya registrado en `core/registry.py`. -->

## Dataset

- Tema (ej: educación, salud, energía):
- Slug propuesto (`kebab-case`, ej: `consumer-prices`):
- Descripción corta (1 frase):

## Fuente oficial

- Organismo:
- URL de la tabla:
- Identificador en la API (table id, dataset code, etc.):
- Licencia / atribución:

## Dimensiones esperadas

<!-- Qué columnas tidy va a producir el fetcher. -->

| Columna | Tipo | Ejemplo |
|---------|------|---------|
| year    | int  | 2024    |
| value   | float| 3.21    |
| territory | str | "Madrid" |

## Vistas propuestas

<!-- Las DatasetViewConfig que se expondrán al frontend. -->

1.
2.

## Notas
