@echo off
REM ==========================================================
REM SCRIPT DE DESARROLLO LOCAL PARA PREFECT
REM ==========================================================
REM Este script:
REM 1. Crea un entorno virtual
REM 2. Instala dependencias
REM 3. Inicia Prefect Server en una ventana separada
REM 4. Deja la consola lista dentro del entorno virtual para ejecutar flujos
REM 
REM IMPORTANTE: Este script es SOLO PARA DESARROLLO LOCAL
REM No usar en producción.
REM ==========================================================

echo === Creando entorno virtual (.venv) ===
python -m venv .venv

echo === Activando entorno virtual ===
call .venv\Scripts\activate

echo === Actualizando pip y asegurando dependencias básicas ===
python -m ensurepip --upgrade
pip install --upgrade pip

echo === Instalando dependencias del proyecto ===
pip install -r requirements.txt

echo === Iniciando Prefect Server en nueva ventana (solo para desarrollo) ===
REM start cmd /k mantiene la ventana abierta
start cmd /k "call .venv\Scripts\activate && prefect server start"

echo === Entorno listo ===
echo Ejecutar tus flujos aquí, dentro del entorno virtual.
REM Mantener la consola activa dentro del entorno virtual
cmd /k "call .venv\Scripts\activate"