# Seguridad del proyecto — Lab 5 (AppSec)

## 1. Alcance y autorización

- **Proyecto:** CrowdStrike Falcon Alert Simulator.
- **Repositorio:** https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI
- **Rama de remediación de F-15:** `fix/log-injection-cwe117`.
- **Commit de corrección de validación:** `326e488c334cbdbdf4daeada3f8e23caa250d281`.
- **Entorno de pruebas:** staging local aislado con Docker, Nginx y las dos APIs Flask; datos ficticios y servicios limitados a `127.0.0.1`.
- **Fuera de alcance:** producción, sistemas de terceros, datos reales, pruebas destructivas y cualquier activo sin autorización explícita.

## 2. Herramientas y controles

| Control | Herramienta / configuración | Alcance y evidencia |
|---|---|---|
| SAST | Semgrep, reglas `p/owasp-top-ten` y `p/secrets` | Workflow `.github/workflows/security.yml`; publica el resultado como artefacto de GitHub Actions. |
| Pruebas de regresión | pytest | El mismo workflow ejecuta `python -m pytest tests -v`. |
| Detección de secretos en CI | Gitleaks | Workflow `.github/workflows/security.yml`; publica el reporte como artefacto. |
| SCA | Dependabot | `.github/dependabot.yml`: actualizaciones semanales para pip (ambas APIs) y GitHub Actions, con periodo de espera de 7 días. |
| DAST pasivo | OWASP ZAP Baseline | Evidencia y configuración en `evidence/lab5/`; ejecutado contra staging local. |
| Code scanning | CodeQL Default setup | **Activo** desde 2026-11-10: Python, JavaScript/TypeScript y Actions. Análisis completado sin alertas. Evidencia: [configuración](../evidence/lab5/github-controles/03-codeql-settings.png), [Actions](../evidence/lab5/github-controles/05-codeql-actions.png), [JavaScript](../evidence/lab5/github-controles/06-codeql-javascript.png), [Python](../evidence/lab5/github-controles/07-codeql-python.png), [alertas](../evidence/lab5/github-controles/08-alertas-code-scanning.png). |
| Alertas de dependencias | Dependabot alerts | **Activo** desde 2026-11-10, con 0 alertas abiertas. Evidencia: [grafo de dependencias](../evidence/lab5/github-controles/01-dependency-graph.png), [configuración](../evidence/lab5/github-controles/02-dependabot-settings.png), [alertas](../evidence/lab5/github-controles/09-alertas-dependabot.png). |
| Secret scanning | GitHub secret scanning y push protection | **Activo** desde 2026-11-10, con 0 alertas abiertas. Evidencia: [configuración](../evidence/lab5/github-controles/04-secret-protection.png), [alertas](../evidence/lab5/github-controles/10-alertas-secret-scanning.png). |

**Limitación de CodeQL:** el análisis capturado corresponde al commit `01389df` de `main`, anterior a la corrección de Log Injection (PR #8). Con la suite por defecto reportó 0 alertas aunque ese commit aún tenía F-15, por lo que un resultado limpio no demuestra ausencia de vulnerabilidades.

**Nota:** los workflows de Semgrep y Gitleaks no sustituyen las funciones nativas de GitHub Dependabot alerts, CodeQL ni secret scanning. La existencia de `.github/dependabot.yml` configura actualizaciones, pero no demuestra por sí sola que Dependabot alerts esté habilitado.

## 3. Hallazgos y remediación

Los hallazgos se documentan en [REPORTE_HALLAZGOS.md](REPORTE_HALLAZGOS.md). La remediación de Log Injection (CWE-117, F-15) se implementa en las dos APIs:

- Se neutralizan los caracteres CR y LF antes de escribir valores controlados por el usuario en los logs.
- En Actions API, `analyst` y `alert_id` deben ser cadenas. Los valores de otro tipo se rechazan con HTTP 400 antes de modificar `ACTIONS`.
- Las pruebas de regresión verifican valores no textuales, neutralización de saltos de línea y el registro de solicitudes con una ruta que contiene `%0a`.

Pull request de la corrección: [#8 — Log Injection CWE-117](https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI/pull/8).

## 4. Validación antes y después

- **Antes:** la revisión detectó que una entrada con saltos de línea podía contaminar los registros.
- **Después:** el revisor confirmó manualmente que las rutas con `%0a` y `%0d%0a` quedan registradas en una sola línea.
- **Regresión:** ejecutar `python -m pytest tests -v` desde la raíz del repositorio.
- **Evidencia automatizada:** consultar los artefactos de los workflows en la pestaña Actions del repositorio.
- **CI:** el workflow de seguridad terminó con éxito sobre `27a871a`, el commit de fusión del PR #8 en `main`.

## 5. Operación segura

1. Ejecutar análisis únicamente sobre este repositorio y el staging local autorizado.
2. Usar exclusivamente datos ficticios y credenciales de prueba.
3. No incluir secretos, tokens ni datos personales en capturas, logs o reportes.
4. Revisar manualmente los hallazgos de SAST, SCA y detección de secretos antes de clasificarlos.
5. Corregir mediante Pull Requests y conservar evidencia de la prueba de regresión y el reescaneo.
6. No fusionar un Pull Request hasta que pasen las pruebas y el revisor confirme los cambios.
