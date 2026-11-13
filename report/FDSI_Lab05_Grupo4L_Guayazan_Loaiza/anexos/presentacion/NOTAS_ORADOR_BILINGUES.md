# Lab 5 — Notas del presentador (bilingües)

Las notas están organizadas por diapositiva. Primero aparece el discurso en inglés y después su versión en español.

## Slide 1 — Opening / Apertura

**English — Juan Sebastián**

Good morning. We are presenting the security assessment of our CrowdStrike Falcon Alert Simulator. We organized the work around four AppSec areas: SAST, SCA, Secret Detection, and DAST. For each one, we will explain what we found, how we detected it, what we changed, and how we validated the result.

**Español — Juan Sebastián**

Buenos días. Vamos a presentar la evaluación de seguridad de nuestro CrowdStrike Falcon Alert Simulator. Organizamos el trabajo en cuatro áreas de seguridad de aplicaciones: análisis estático de seguridad (SAST), análisis de composición de software (SCA), detección de secretos (SD) y análisis dinámico de seguridad (DAST). Para cada una explicaremos qué encontramos, cómo lo detectamos, qué cambiamos y cómo validamos los resultados.

## Slide 2 — Findings and detection / Hallazgos y detección

**English — Brayan**

For SAST, we used Semgrep and manual code review. The main findings were Stored XSS, missing authentication, and Log Injection. For SCA, we reviewed Dependabot and the Nginx reverse-proxy configuration. The dependency alert concerned pytest and was scoped to tests and CI. For Secret Detection, Gitleaks produced one match, which we reviewed as an intentionally invalid test value rather than a real credential. For DAST, we ran OWASP ZAP against the application in our local Docker environment. The initial scan identified the missing Content Security Policy header. Across findings with a documented severity, the count is two High, three Medium, and one Low.

**Español — Brayan**

En SAST utilizamos Semgrep y revisión manual del código. Los principales hallazgos fueron Cross-Site Scripting almacenado, ausencia de autenticación e inyección en registros. En SCA revisamos las alertas de Dependabot y la configuración del proxy Nginx. La alerta de dependencia correspondía a pytest y estaba limitada a pruebas y CI. Para detectar secretos utilizamos Gitleaks y revisamos una coincidencia que correspondía a un valor de prueba intencionalmente inválido, no a una credencial real. Para DAST ejecutamos OWASP ZAP contra la aplicación en nuestro entorno Docker local. El análisis inicial identificó la ausencia de la cabecera Content-Security-Policy. Entre los hallazgos con severidad documentada, el conteo es de dos altos, tres medios y uno bajo.

## Slide 3 — Remediation / Remediación

**English — Juan Sebastián**

We addressed the root causes rather than only suppressing alerts. In the application code, we handled untrusted output for the XSS issue, added authentication checks for restricted actions, and neutralized carriage-return and line-feed characters before logging. In the reverse proxy, we replaced the user-controlled Host value with the configured upstream host. For the dependency alert, Dependabot proposed updating pytest from 8.3.4 to 9.0.3. The captured evidence shows PR #11 is still open, so we describe this update as pending rather than completed. For DAST, we added a Content Security Policy response header. The Gitleaks match was reviewed as a test value, so it did not require rotating a real credential.

**Español — Juan Sebastián**

Abordamos las causas de los problemas en lugar de limitarnos a ocultar las alertas. En el código de la aplicación, corregimos el tratamiento de contenido no confiable para evitar el XSS, agregamos verificaciones de autenticación para las acciones restringidas y neutralizamos los caracteres de retorno de carro y salto de línea antes de guardar información en los registros. En el proxy inverso, cambiamos la configuración para utilizar el servidor de destino definido y no el valor Host que puede manipular el usuario. En cuanto a pytest, Dependabot propuso actualizar la versión 8.3.4 a la 9.0.3; como la evidencia muestra que el PR #11 sigue abierto, esta actualización está pendiente y no la presentamos como terminada. Para DAST agregamos una cabecera Content Security Policy. Finalmente, revisamos la coincidencia de Gitleaks y comprobamos que era un valor de prueba, no una credencial real.

## Slide 4 — Validation / Validación

**English — Brayan**

We validated the fixes with regression tests and repeated security checks. For Log Injection, the before-and-after test showed that CR/LF input no longer creates a forged log entry. For the Nginx Host header, Semgrep went from two findings to zero after the configuration change. The final Semgrep scan on main reported zero findings. The final OWASP ZAP scan reported zero High and zero Medium alerts. Gitleaks had no open findings in the final reported check. One private-IP disclosure was reviewed as a false positive. The DAST scan was local and used HTTP, so it does not assess production TLS. These results validate the tested scope, not the absence of every possible vulnerability.

**Español — Brayan**

Validamos las correcciones mediante pruebas de regresión y la repetición de los análisis de seguridad. Para la inyección en registros, la prueba antes y después mostró que la entrada CR/LF ya no genera una entrada falsa. Para la cabecera Host de Nginx, los hallazgos de Semgrep pasaron de dos a cero después del cambio de configuración. El análisis final de Semgrep en main reportó cero hallazgos. El análisis final de OWASP ZAP reportó cero alertas altas y cero medias. Gitleaks no tenía hallazgos abiertos en la última verificación reportada. Una divulgación de IP privada se revisó como falso positivo. El análisis DAST se ejecutó localmente sobre HTTP, por lo que no evalúa TLS en producción. Estos resultados validan el alcance probado, pero no demuestran la ausencia de todas las vulnerabilidades posibles.

## Slide 5 — Closing / Cierre

**English — Juan Sebastián**

To conclude, our assessment identified six findings with a documented severity: two High, three Medium, and one Low. We used static analysis, dependency review, secret detection, and dynamic testing to identify risks. We then applied targeted changes and validated them with regression tests and final scans. Our main lesson is that a security finding is not complete until its remediation has been checked. Thank you. We are ready for your questions.

**Español — Juan Sebastián**

Para concluir, nuestra evaluación identificó seis hallazgos con una severidad documentada: dos altos, tres medios y uno bajo. Utilizamos análisis estático, revisión de dependencias, detección de secretos y pruebas dinámicas para identificar los riesgos. Después aplicamos cambios específicos y los validamos con pruebas de regresión y análisis finales. Nuestra principal conclusión es que un hallazgo de seguridad no está completo hasta que se comprueba su corrección. Muchas gracias. Estamos atentos a sus preguntas.
