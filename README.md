# EinScan Pro — Sistema OMR Colegio Albert Einstein

EinScan Pro es una solución profesional de Reconocimiento Óptico de Marcas (OMR) diseñada para funcionar 100% de forma local. Permite calificar exámenes de opción múltiple con alta precisión usando visión por computadora e inteligencia artificial.

## 🚀 Inicio Rápido

### Requisitos Previos
1. **Python 3.11+**
2. **Node.js 18+**
3. **Tesseract OCR:** [Instalar](https://github.com/UB-Mannheim/tesseract/wiki) (Asegúrate de agregarlo al PATH o configurar la ruta en el código).

### Instalación y Ejecución
Solo necesitas ejecutar un comando:
```powershell
python run.py
```
Este script:
1. Instalará las dependencias de Python (`requirements.txt`).
2. Compilará el frontend de React (si no está compilado).
3. Iniciará el servidor backend.
4. Abrirá automáticamente tu navegador en `http://localhost:8000`.

## 🛠️ Configuración
Copia el archivo `.env.example` a `.env` y configura:
- `GEMINI_API_KEY`: Tu clave de Google AI para revisión de marcas dudosas.
- `ADMIN_PASSWORD`: Contraseña para el acceso docente (defecto: `admin123`).

## 📋 Flujo de Trabajo
1. **Generar:** Crea un examen en la pestaña "Generar Fichas" y descarga el PDF.
2. **Imprimir:** Imprime en A4 al 100% de escala.
3. **Configurar:** Define las respuestas correctas en "Claves de Respuestas".
4. **Escanear:** Sube las fotos de los exámenes en la pestaña "Escanear Hojas".
5. **Analizar:** Consulta estadísticas y exporta resultados en la pestaña "Resultados".

---
Desarrollado para el **Colegio Albert Einstein**. 100% Privacidad, 100% Local.
