# Lista de verificación integrada de Sistemas de Gestión (ISO 9001 · ISO 14001 · ISO 45001)

Aplicación web en **Streamlit** para realizar un diagnóstico / autoevaluación integrada de un
Sistema de Gestión, aprovechando la estructura común de alto nivel (Anexo SL, cláusulas 4 a 10)
de las normas:

- ISO 9001 (Calidad)
- ISO 14001 (Ambiental)
- ISO 45001 (Seguridad y Salud en el Trabajo)

## Funciones
- Checklist integrado por cláusulas (4 a 10); cada requisito indica a qué norma(s) aplica.
- Selección de las normas a evaluar (una, dos o las tres).
- Respuestas: Cumple / Cumple parcialmente / No cumple / No aplica, con observaciones y evidencia.
- Resultados: % de cumplimiento global, por norma y por cláusula, con gráficos.
- Plan de acción editable para los incumplimientos (responsable, fecha, acción).
- Exportación a Excel y CSV.

## Ejecutar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Despliegue en streamlit.app (Community Cloud)
1. Sube esta carpeta a un repositorio de GitHub (`app.py` y `requirements.txt` en la raíz).
2. Entra a https://share.streamlit.io e inicia sesión con GitHub.
3. **Create app** → elige el repositorio, rama `main` y archivo principal `app.py`.
4. **Deploy**.

## Aviso
Las preguntas son redacciones propias basadas en la estructura de las normas; no reproducen el
texto oficial. Para una auditoría formal consulte las normas ISO vigentes.
