import os
import subprocess
import sys
import webbrowser
import time
from threading import Timer

def run_command(command, cwd=None):
    """Ejecuta un comando en el sistema y retorna el código de salida."""
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        for line in process.stdout:
            print(line, end='')
        process.wait()
        return process.returncode
    except Exception as e:
        print(f"Error ejecutando comando: {e}")
        return 1

def open_browser():
    """Abre el navegador en la dirección del servidor."""
    webbrowser.open("http://localhost:8000")

def main():
    print("="*50)
    print("      EINSCAN PRO - COLEGIO ALBERT EINSTEIN")
    print("="*50)

    # 1. Verificar/Instalar dependencias de Python
    print("\n[1/4] Verificando dependencias de Python...")
    if run_command(f"{sys.executable} -m pip install -r requirements.txt") != 0:
        print("Error instalando dependencias de Python. Abortando.")
        sys.exit(1)

    # 2. Verificar/Compilar Frontend
    frontend_path = os.path.join(os.getcwd(), "frontend")
    dist_path = os.path.join(frontend_path, "dist")

    if not os.path.exists(dist_path):
        print("\n[2/4] Frontend no compilado. Instalando y compilando (esto puede tardar)...")
        if run_command("npm install", cwd=frontend_path) != 0:
            print("Error ejecutando 'npm install'. ¿Tienes Node.js instalado?")
            sys.exit(1)
        if run_command("npm run build", cwd=frontend_path) != 0:
            print("Error ejecutando 'npm run build'.")
            sys.exit(1)
    else:
        print("\n[2/4] Frontend ya compilado.")

    # 3. Preparar Base de Datos y Carpetas
    print("\n[3/4] Preparando entorno local...")
    os.makedirs("data/sheets", exist_ok=True)
    os.makedirs("data/scans", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)

    # 4. Iniciar Servidor FastAPI
    print("\n[4/4] Iniciando servidor en http://localhost:8000 ...")
    print("\n¡EinScan Pro está listo! El navegador se abrirá automáticamente.")
    
    # Abrir navegador después de 2 segundos
    Timer(2, open_browser).start()

    # Ejecutar FastAPI usando uvicorn
    # Se asume que backend/main.py es el punto de entrada
    run_command("python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
