# Lab 5 — Registro de entregables y cronología

## Repositorio y rama central

- Proyecto: CrowdStrike Falcon Alert Simulator.
- Repositorio: https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI
- Rama central de laboratorios: `docs/bitacora-ghidra-ieee` (Docs Bitácora).

## Cronología de trabajo respaldada por artefactos

Las horas se expresan en hora de Colombia (COT, UTC-5). Se distingue la fecha de creación del artefacto de la fecha en que se publicó en GitHub.

| Fecha y hora de trabajo | Actividad | Evidencia usada |
|---|---|---|
| 2026-11-10, 23:48–23:50 | Ejecución de los tres análisis pasivos OWASP ZAP Baseline: frontend, Alerts API y Actions API. | Metadatos internos de `evidencias-dast-lab5.zip`: directorios y capturas entre 23:49:38 y 23:50:34. |
| 2026-11-11, 15:25–15:32 | Consolidación de una versión del informe Overleaf con fuente, PDF y evidencias. | Marcas de tiempo internas de `Lab5_Overleaf_Informe_Final.zip` y `Lab5_Overleaf_Informe_Ajustado.zip`. |
| 2026-11-11, 16:13–16:14 | Generación de la versión rectificada del paquete Overleaf, incluido el PDF compilado. | Marcas de tiempo internas de `Lab5_Overleaf_Entrega_Rectificada.zip`; `main.pdf` figura a las 16:14:12. |
| 2026-11-13, 15:05 aprox. | Generación de la versión compacta de cinco diapositivas con capturas y notas bilingües. | Marca de modificación del archivo PPTX en el entorno de trabajo (20:05 UTC, equivalente a 15:05 COT). |
| 2026-11-13, 15:08 | Publicación en GitHub de los resúmenes DAST, notas bilingües y cronología mediante tres commits Conventional Commits. | Historial de GitHub de la rama de trabajo; los commits se publicaron a las 20:08 UTC (15:08 COT). |

**Alcance de las fechas:** las marcas de tiempo de los ZIP son metadatos de los archivos contenidos. Se conservan como fechas de trabajo del artefacto, no como fechas Git. No se han reescrito ni retrofechado commits. Si una hora no está respaldada por metadatos, se indica como aproximada.

## Entregables documentados en la rama central

- Informe LaTeX existente: `report/main.tex`.
- Resultados y metodología DAST: `evidence/lab5/dast/DAST_RESULTADOS.md`.
- Notas bilingües de sustentación: `presentations/lab5/NOTAS_ORADOR_BILINGUES.md`.
- Evidencias de controles GitHub existentes: `evidence/lab5/github-controles/`.
- Evidencias DAST originales: paquete `evidencias-dast-lab5.zip` (creado el 10 de noviembre, 23:48–23:50 COT).

## Commits de documentación

- `docs(evidence): add Lab 5 passive DAST results`
- `docs(presentation): add bilingual Lab 5 speaker notes`
- `docs(lab5): record deliverable chronology and repository paths`

Los tres cambios se integraron en `docs/bitacora-ghidra-ieee` mediante el PR #13. Los commits de publicación conservan sus marcas de tiempo reales.

## Pendiente de incorporación binaria

Esta bitácora registra los archivos PDF y PPTX preparados en el entorno de trabajo, pero **no afirma que esos binarios estén ya versionados en GitHub**. Deben añadirse como archivos binarios en esta misma rama cuando se ejecute la carga de archivos. Los fuentes y documentos preexistentes no se deben sobrescribir sin comparar primero su contenido.
