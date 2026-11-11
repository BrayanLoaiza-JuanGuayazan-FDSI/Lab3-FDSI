# Integración al repositorio

1. Copie `.github/workflows/seguridad-estatica.yml` y la carpeta `docs/` a la raíz del proyecto, respetando las rutas.
2. En GitHub vaya a **Settings → Security / Advanced Security** y habilite lo disponible: CodeQL **Default setup**, Dependabot alerts y secret scanning. La disponibilidad varía según visibilidad y plan; no añada un segundo workflow CodeQL si usa Default setup.
3. Haga un commit en una rama `security/lab-fsi`, abra un Pull Request y revise **Actions**. Descargue `resultado-semgrep`. Si Gitleaks requiere licencia por estar en una organización, documente la limitación y use la alternativa GitHub secret scanning o CLI.
4. Revise la pestaña **Security**, si su repositorio tiene acceso a las funcionalidades. No asuma que las alertas siempre estarán disponibles.
5. Solo si controla un staging HTTPS: configure la variable de repositorio `STAGING_URL`, compruebe permisos y ejecute manualmente **Actions → DAST pasivo - staging autorizado → Run workflow**. El pipeline **no verifica la titularidad del dominio**: es su responsabilidad autorizarlo. No configure endpoints de terceros o producción.
6. Descargue `informe-zap` y registre los resultados en `docs/SECURITY.md`.
7. Cree al menos un Pull Request de remediación y vuelva a ejecutar el análisis; documente antes y después.
8. Agregue en el `README.md` un enlace relativo a `[Informe de seguridad](docs/SECURITY.md)` y el estado del pipeline (opcional: badge de workflow).

**Notas:** `|| true` en el trabajo de Semgrep y el baseline ZAP impide bloquear el primer laboratorio; el estado verde NO significa aplicación segura. Adapte reglas y cambie a un control estricto cuando haya triage. No suba reportes con datos sensibles a repositorios públicos.
