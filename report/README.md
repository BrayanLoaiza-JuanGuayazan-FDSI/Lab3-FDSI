# Informes

Cada laboratorio tiene su propia carpeta, con la nomenclatura `FDSI_LabNN_Grupo4L_Guayazan_Loaiza`, independiente y autocontenida (con su
`IEEEtran.cls` y sus imágenes), de modo que cada una se puede subir a Overleaf
como proyecto aparte. Todas parten de la misma plantilla IEEEtran del curso.

| Carpeta | Contenido | Formato |
|---|---|---|
| `FDSI_Lab03_Grupo4L_Guayazan_Loaiza/` | Lab 3: HTTP, Red Team / Blue Team | LaTeX (`main.tex`) |
| `FDSI_Lab05_Grupo4L_Guayazan_Loaiza/` | Lab 5: Seguridad de aplicaciones (AppSec) | LaTeX (`main.tex`) |
| `FDSI_Lab06_Grupo4L_Guayazan_Loaiza/` | Lab 6: bitácora de Ghidra, reto CODEBREAKERS | LaTeX (`main.tex`) |

## Compilar

```bash
cd report/FDSI_Lab03_Grupo4L_Guayazan_Loaiza   # o la carpeta que corresponda
latexmk -pdf main.tex
```

## Convención para un informe nuevo

1. Crear `report/FDSI_LabNN_Grupo4L_Guayazan_Loaiza/` y copiar ahí `IEEEtran.cls` y un `main.tex` de otro informe como base.
2. Guardar las figuras en `images/` dentro de esa carpeta y referenciarlas como `images/archivo`.
3. Subir solo el código fuente (`main.tex`, `images/`, `IEEEtran.cls`); no subir PDFs ni auxiliares (`.aux`, `.log`, `.out`).

## Qué hay dentro de cada carpeta

Todo lo que pertenece a un informe vive en su carpeta; la raíz del repositorio queda solo para el código.

```
FDSI_LabNN_Grupo4L_Guayazan_Loaiza/
├── main.tex          informe (plantilla IEEEtran)
├── IEEEtran.cls
├── images/           figuras que usa el informe
└── anexos/           evidencias y material de apoyo citado por el informe
```

- **Lab 3** (`anexos/`): `red/`, `blue/`, `retest/`, `zap-passive/`, `diagrams/`, `threat-model/`, `risk-register.md`, línea de tiempo Purple Team, preguntas de análisis y uso de IA.
- **Lab 5** (`anexos/`): `antes/`, `despues/`, `dast/`, `github-controles/`, `capturas/`, `pipeline-run-28/`, `staging-local/`, línea base, validaciones, `ENTREGABLES_Y_CRONOLOGIA.md` y `presentacion/` (notas del orador).

Los archivos crudos de herramientas (Nmap, Semgrep, ZAP) se conservan tal como salieron, aunque mencionen rutas anteriores del repositorio.
