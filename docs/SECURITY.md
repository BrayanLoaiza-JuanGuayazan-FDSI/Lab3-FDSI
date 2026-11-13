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
| DAST pasivo | OWASP ZAP Baseline | Evidencia y configuración en `report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/`; ejecutado contra staging local. |
| Code scanning | CodeQL Default setup | **Activo** desde 2026-11-10: Python, JavaScript/TypeScript y Actions. Análisis completado sin alertas. Evidencia: [configuración](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/03-codeql-settings.png), [Actions](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/05-codeql-actions.png), [JavaScript](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/06-codeql-javascript.png), [Python](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/07-codeql-python.png), [alertas](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/08-alertas-code-scanning.png). |
| Alertas de dependencias | Dependabot alerts | **Activo** desde 2026-11-10. Al 2026-11-11: 0 alertas abiertas y 1 corregida (`pytest`, CVE-2025-71176, severidad media, cerrada al fusionar el PR #11). Evidencia: [grafo de dependencias](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/01-dependency-graph.png), [configuración](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/02-dependabot-settings.png) y [estado actualizado de las alertas](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/09-alertas-dependabot.png). |
| Secret scanning | GitHub secret scanning | **Activo** desde 2026-11-10, con 0 alertas abiertas. Detecta secretos ya presentes en el repositorio. Evidencia: [configuración](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/04-secret-protection.png), [alertas](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/10-alertas-secret-scanning.png). |
| Push protection | GitHub secret scanning push protection | **Activo** desde 2026-11-10. Es un ajuste independiente: bloquea el push que contenga un secreto compatible. Evidencia: [configuración](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/github-controles/04-secret-protection.png) y API del repositorio (`secret_scanning_push_protection=enabled`). |

**Limitación de CodeQL:** el análisis capturado corresponde al commit `01389df` de `main`, anterior a la corrección de Log Injection (PR #8). Con la suite por defecto reportó 0 alertas aunque ese commit aún tenía F-15, por lo que un resultado limpio no demuestra ausencia de vulnerabilidades. El análisis más reciente de `main`, sobre `21d6f92`, tampoco reporta alertas.

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
- **Validación manual de F-15:** [`validacion-f15.txt`](../report/FDSI_Lab05_Grupo4L_Guayazan_Loaiza/anexos/validacion-f15.txt), con la misma petición antes y después, pasando por Nginx.
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
