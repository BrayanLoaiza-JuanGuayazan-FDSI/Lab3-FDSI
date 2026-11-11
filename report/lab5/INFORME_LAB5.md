# Informe — Laboratorio 5: Seguridad de Aplicaciones (AppSec)

**Proyecto:** CrowdStrike Falcon Alert Simulator  
**Curso:** Fundamentos de Seguridad de la Información  
**Equipo:** Brayan Loaiza Leal y Juan Sebastián Guayazán Clavijo  
**Repositorio:** https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI  
**Periodo:** 2026-2

> Este informe registra el avance confirmado hasta el 11 de noviembre de 2026. Distingue los controles habilitados de las verificaciones que aún están pendientes; no se presentan como exitosas pruebas que todavía no han terminado.

## 1. Alcance

La práctica se desarrolla sobre el repositorio del proyecto CrowdStrike Falcon Alert Simulator. El trabajo se limita al código y a los servicios del proyecto, en el entorno autorizado para el laboratorio y con datos de prueba. No se incluyen sistemas de terceros ni entornos de producción.

## 2. Configuración de seguridad de GitHub

### 2.1 CodeQL

Se habilitó **CodeQL Default setup**. GitHub detectó los siguientes lenguajes en la rama predeterminada:

- GitHub Actions
- JavaScript / TypeScript
- Python

Se mantuvo el conjunto de consultas **Default** y el ejecutor **Standard GitHub runner**.

### 2.2 Secret Scanning

La sección **Secret Protection** muestra la opción **Disable**, señal de que Secret Scanning se encuentra habilitado en el repositorio.

### 2.3 Dependabot alerts

La sección **Dependabot** muestra **Dependabot alerts: On**. Por tanto, las alertas por vulnerabilidades detectadas en las dependencias están habilitadas.

Otras opciones observadas en la misma pantalla:

- Malware alerts: Off.
- Dependabot security updates: Off.
- Grouped security updates: Off.
- Dependabot auto-triage rules: 1 regla habilitada.
- Dependabot version updates: configurado mediante `.github/dependabot.yml`.

Estas opciones se registran tal como aparecen en la captura; no se afirma que estén habilitadas las funciones que muestran Off.

### 2.4 Acceso a las alertas

La configuración mostrada concede acceso para consultar y administrar alertas de code scanning, Dependabot y secret scanning a:

- Administradores de la organización.
- Administradores del repositorio.
- Equipos con el rol de administrador de seguridad.

No se agregaron usuarios ni equipos adicionales.

## 3. Remediación de Log Injection (CWE-117, F-15)

La corrección se integró mediante el [PR #8](https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI/pull/8), que fue fusionado en `main`. La ejecución posterior del workflow de seguridad se realizó sobre el commit `27a871adde809ff74bbc2746be73d8c39c740927`.

De acuerdo con la revisión recibida, las pruebas manuales con `%0a` y `%0d%0a` en la URL dejaron el registro en una sola línea. Durante esa revisión se identificó un caso adicional: valores no textuales en `analyst` o `alert_id` podían provocar HTTP 500 y, aun así, dejar guardada la acción.

Se incorporó validación de tipo para ambos campos antes de modificar la colección de acciones. Los valores no textuales deben rechazarse con HTTP 400, sin guardar la acción. También se añadieron pruebas para valores numéricos y nulos, para comprobar que el estado no cambia ante solicitudes inválidas y para comprobar el registro de solicitudes con una ruta que contiene `%0a`. La prueba de ruta se ajustó para enviar la credencial de prueba requerida por el endpoint.

El informe de hallazgos se actualizó para que F-15 haga referencia al SHA de remediación y no permanezca en la sección de limitaciones. Se documentó el alcance y las herramientas en `docs/SECURITY.md`. El PR #4, duplicado y con conflictos, se cerró. El PR #8 quedó integrado en `main`.

**Estado de CI:** la ejecución #21 del workflow `Seguridad estática - SAST y secretos`, sobre el commit `27a871adde809ff74bbc2746be73d8c39c740927`, finalizó con resultado **success** en 33 segundos. Generó dos artefactos: `resultado-semgrep` y `resultado-gitleaks`.


## 4. Resultados de SAST y detección de secretos

La ejecución #21 del workflow de seguridad terminó correctamente. Los tres trabajos —Semgrep (SAST), pruebas de regresión y Gitleaks— finalizaron con estado exitoso. La ejecución tardó 33 segundos y generó dos artefactos.

### 4.1 Semgrep

En la línea base, Semgrep reportó 15 resultados. Después de la primera remediación y de excluir las copias históricas identificadas como F-17, el análisis quedó en 2 coincidencias de F-16. Semgrep versión 1.185.0 examinó 26 rutas de archivos y no reportó errores de análisis. Identificó dos coincidencias de la regla `generic.nginx.security.request-host-used.request-host-used` en `nginx/lab3-fdsi.conf`, líneas 29 y 36. Ambas correspondían a la directiva `proxy_set_header Host $host;`, utilizada en los proxies de Alerts API y Actions API.

El reporte clasificó las coincidencias como WARNING y las relacionó con CWE-290, con confianza media y estimaciones de probabilidad e impacto bajos. Se consideran advertencias que requieren validación contextual; por sí solas no demuestran explotación ni autenticación omitida.

### 4.2 Remediación preventiva de encabezado Host

Para evitar reenviar a los microservicios el valor Host recibido del cliente, se modificaron ambas directivas a `proxy_set_header Host $proxy_host;`. De esta forma Nginx utiliza el host del upstream definido en cada `proxy_pass` (127.0.0.1:5000 y 127.0.0.1:5001), en lugar de conservar el encabezado Host de la solicitud externa.

El cambio se encuentra en la rama `docs/lab5-report`, en el commit `ca6fa69`, y se propone para revisión en el PR #9. En el reescaneo posterior a este cambio, Semgrep examinó nuevamente `nginx/lab3-fdsi.conf` y el reporte resultó sin coincidencias (`results: []`) ni errores (`errors: []`). Las pruebas de regresión también finalizaron correctamente. Por tanto, F-16 quedó corregido y Semgrep pasó de 15 resultados en la línea base, a 2 tras la primera remediación, y finalmente a 0 con este cambio.

### 4.3 Gitleaks

Gitleaks finalizó correctamente en la misma ejecución #24 y produjo un reporte JSON vacío (`[]`), por lo que no detectó secretos en el intervalo de commits configurado por el workflow (`HEAD~1..HEAD`). Este resultado no equivale a un análisis de todo el historial del repositorio.

## 5. Resumen de estado

| Elemento | Estado |
|---|---|
| CodeQL Default setup | Habilitado |
| Semgrep (línea base) | 15 resultados |
| Semgrep (tras primera remediación) | 2 resultados: F-16 en Nginx |
| Semgrep (tras commit `ca6fa69`) | 0 hallazgos; `results: []`, sin errores |
| Gitleaks #24 | 0 secretos detectados en `HEAD~1..HEAD` |
| Secret Scanning | Habilitado |
| Dependabot alerts | Habilitado |
| Acceso a alertas | Configurado para administradores y equipos de seguridad |
| Corrección F-15 | Integrada en `main` mediante PR #8 |
| Workflow SAST/Gitleaks #24 | Los tres jobs finalizaron correctamente (success) |
| PR #8 | Fusionado en `main` |

## 6. Evidencias visuales

Las capturas de configuración de CodeQL, Dependabot alerts, Secret Scanning y permisos de acceso se incorporan en el [PR #10](https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI/pull/10), dentro de `evidence/lab5/github-controles/`. Este informe no afirma que adjunte un PDF ni imágenes que no estén versionadas junto con el documento fuente.

## 7. Conclusión

Las capturas del PR #10 respaldan la configuración de CodeQL Default setup, Secret Scanning y Dependabot alerts. La remediación F-15 fue integrada en `main`. Semgrep pasó de 15 resultados en la línea base a 2 tras la primera remediación y a 0 después de corregir F-16 mediante el commit `ca6fa69`. La validación de Brayan confirmó en Docker que el encabezado Host falso llega a la API como `127.0.0.1:5000` y que las APIs, la autenticación y el dashboard continúan funcionando. Los artefactos reportan Gitleaks 0 y 55 pruebas exitosas.


