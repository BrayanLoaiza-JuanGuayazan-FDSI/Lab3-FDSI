# Uso de IA en el Lab 3

- **Herramienta:** Claude Code (asistente de IA), como copiloto de apoyo.
- **En qué se usó:** redactar y organizar documentación (README, informe LaTeX, registro de riesgos), preparar el script de la regla de detección (`evidence/blue/detect_404.py`), generar el DFD de la arquitectura fortalecida y revisar la consistencia entre las guías del profesor y el repositorio.
- **Qué no hizo:** no ejecutó ninguna prueba contra la VM (no tiene acceso a la red del laboratorio). Los comandos de Nmap, curl, ZAP, tcpdump y el despliegue los ejecutó el equipo desde Kali y la VM.
- **Excepción documentada (informe de la Parte I):** la evidencia de ejecución local (`python3 -m http.server 8080`, `curl`, `git log`, `git status`) la ejecutó el asistente en el equipo de desarrollo. Las figuras `git-log.png` y `curl-local.png` del informe son imágenes generadas a partir de esa salida textual real, no capturas de pantalla del sistema operativo.
- **Datos compartidos:** solo datos ficticios del laboratorio y salidas de comandos del propio equipo. No se compartieron contraseñas, tokens, llaves ni PCAP completos.
- **Validación humana:** cada afirmación técnica se contrastó con una salida real del repositorio o de la VM (por ejemplo, la regla de detección se probó contra `evidence/blue/access_tail.txt`, y el contenido del PCAP se verificó con un lector independiente).
