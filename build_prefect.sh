#!/bin/bash
# ==========================================================
# 🚀 build_prefect.sh — Script de construcción Prefect
# Autor: Alexander Oyuela
# Descripción: Automatiza la creación y despliegue de los
# flujos Prefect 
# ==========================================================

set -e  # Detiene el script ante cualquier error

echo "🏗️ Iniciando build de Prefect..."

# ----------------------------------------------------------
# 1️⃣ Limpieza previa
# ----------------------------------------------------------
echo "🧹 Eliminando archivos de despliegue anteriores..."
rm -f *-deployment.yaml || true

# ----------------------------------------------------------
# 2️⃣ Construcción de deployments
# ----------------------------------------------------------
echo "📦 Construyendo deployments de flujos..."
prefect deploy

# ----------------------------------------------------------
# 3️⃣ (Opcional) Crear y ejecutar un work pool / agente local
# ----------------------------------------------------------
echo "🌐 Verificando pool de ejecución..."
prefect work-pool create "etl-agent" --type process || true

echo "🚀 Iniciando agente Prefect en segundo plano..."
prefect worker start --pool "etl-agent" &
# Nota: el '&' ejecuta el worker en background

# ----------------------------------------------------------
# 4️⃣ Confirmación final
# ----------------------------------------------------------
echo "✅ Build Prefect completado correctamente."
echo "Para ejecutar manualmente el orquestador:"
echo "prefect deployment run 'Orquestador Principal'"
