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
| Code scanning | CodeQL | La activación de CodeQL Default Setup debe confirmarse en Settings → Security → Code security and analysis. No se afirma habilitado hasta verificarlo allí. |
| Alertas de dependencias | Dependabot alerts | La activación debe confirmarse en Settings → Security → Code security and analysis. |
| Secret scanning | GitHub secret scanning | La activación debe confirmarse en Settings → Security → Code security and analysis. |

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
- **Revisión pendiente:** confirmar los resultados de la ejecución de CI sobre el último commit del PR #8 antes de fusionarlo.

## 5. Operación segura

1. Ejecutar análisis únicamente sobre este repositorio y el staging local autorizado.
2. Usar exclusivamente datos ficticios y credenciales de prueba.
3. No incluir secretos, tokens ni datos personales en capturas, logs o reportes.
4. Revisar manualmente los hallazgos de SAST, SCA y detección de secretos antes de clasificarlos.
5. Corregir mediante Pull Requests y conservar evidencia de la prueba de regresión y el reescaneo.
6. No fusionar el PR #8 hasta que pasen las pruebas y el revisor confirme los cambios.
