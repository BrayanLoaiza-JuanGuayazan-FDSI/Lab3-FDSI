# Informes

Cada laboratorio tiene su propia carpeta, independiente y autocontenida (con su
`IEEEtran.cls` y sus imágenes), de modo que cada una se puede subir a Overleaf
como proyecto aparte. Todas parten de la misma plantilla IEEEtran del curso.

| Carpeta | Contenido | Formato |
|---|---|---|
| `lab3/` | Lab 3: HTTP, Red Team / Blue Team | LaTeX (`main.tex`) + PDF |
| `lab5/` | Lab 5: Seguridad de aplicaciones (AppSec) | LaTeX (`main.tex`); `INFORME_LAB5.md` es el borrador previo en Markdown |
| `lab6/` | Lab 6: bitácora de Ghidra, reto CODEBREAKERS | LaTeX (`main.tex`) + PDF |

## Compilar

```bash
cd report/lab3   # o la carpeta que corresponda
latexmk -pdf main.tex
```

## Convención para un informe nuevo

1. Crear `report/labN/` y copiar ahí `IEEEtran.cls` y un `main.tex` de otro informe como base.
2. Guardar las figuras en `report/labN/images/` y referenciarlas como `images/archivo`.
3. Subir `main.tex` y el PDF compilado; los auxiliares (`.aux`, `.log`, `.out`) ya los ignora `.gitignore`.
