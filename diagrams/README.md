# Diagramas

- `dfd-lab3.png` — arquitectura inicial: actores, componentes, protocolo, puertos, almacenes de datos, límites de confianza y puntos de generación de logs.
- `dfd-lab3-fortalecida.png` (fuente: `dfd-lab3-fortalecida.svg`) — arquitectura después del hardening: servicios en loopback, UFW limitado a `LAB_CIDR`, sin `/debug/env` ni `debug=True`, y los riesgos que siguen abiertos.

La cadena arquitectura inicial → gap → riesgo → mejora → arquitectura fortalecida está en la hoja `Improvements` de `threat-model/threat-model.xlsx`.
