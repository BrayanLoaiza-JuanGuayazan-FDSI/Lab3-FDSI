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

La corrección se trabaja en la rama `fix/log-injection-cwe117`, mediante el [PR #8](https://github.com/BrayanLoaiza-JuanGuayazan-FDSI/Lab3-FDSI/pull/8).

De acuerdo con la revisión recibida, las pruebas manuales con `%0a` y `%0d%0a` en la URL dejaron el registro en una sola línea. Durante esa revisión se identificó un caso adicional: valores no textuales en `analyst` o `alert_id` podían provocar HTTP 500 y, aun así, dejar guardada la acción.

Se incorporó validación de tipo para ambos campos antes de modificar la colección de acciones. Los valores no textuales deben rechazarse con HTTP 400, sin guardar la acción. También se añadieron pruebas para valores numéricos y nulos, para comprobar que el estado no cambia ante solicitudes inválidas y para comprobar el registro de solicitudes con una ruta que contiene `%0a`. La prueba de ruta se ajustó para enviar la credencial de prueba requerida por el endpoint.

El informe de hallazgos se actualizó para que F-15 haga referencia al SHA de remediación y no permanezca en la sección de limitaciones. Se documentó el alcance y las herramientas en `docs/SECURITY.md`. El PR #4, duplicado y con conflictos, se cerró; el fix continúa en el PR #8.

**Estado de CI:** la ejecución correspondiente al commit `4729d0202f9e32d38834e1bf309cfbfa44302df9` finalizó con resultado **success** en GitHub Actions. El resultado confirma que el workflow terminó correctamente para ese commit.

## 4. Resumen de estado

| Elemento | Estado |
|---|---|
| CodeQL Default setup | Habilitado |
| Secret Scanning | Habilitado |
| Dependabot alerts | Habilitado |
| Acceso a alertas | Configurado para administradores y equipos de seguridad |
| Corrección F-15 | Cambios y pruebas añadidos al PR #8 |
| CI del commit `4729d02` | Finalizado correctamente (success) |
| Revisión y fusión del PR #8 | Pendientes |

## 5. Inventario de evidencias visuales

Las capturas recibidas y utilizadas para elaborar el informe PDF adjunto son:

1. **Code Security inicial:** vista de CodeQL analysis y Secret Protection antes de completar la configuración.
2. **CodeQL Default configuration:** lenguajes detectados, query suite Default y Standard GitHub runner.
3. **Access to alerts:** permisos de acceso a las alertas de seguridad.
4. **Estado de CodeQL y Secret Protection:** CodeQL Default setup visible y Secret Protection habilitado.
5. **Dependabot alerts:** interruptor Dependabot alerts en estado On.

## 6. Conclusión

Las capturas confirman la habilitación de CodeQL Default setup, Secret Scanning y Dependabot alerts. La remediación F-15 también cuenta con cambios y pruebas adicionales en el PR #8. Para cerrar esta parte del laboratorio es necesario verificar que CI finalice correctamente y obtener la revisión final antes de fusionar el PR.

---

**Evidencia complementaria:** el PDF de trabajo generado incluye las cinco capturas descritas en el inventario. Las imágenes originales deben incorporarse como archivos independientes a esta carpeta del repositorio para que el documento fuente pueda compilarse directamente desde GitHub.
