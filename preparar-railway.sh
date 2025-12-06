#!/bin/bash
# Script para preparar archivos para deployment en Railway
# Ejecutar desde: /home/micaela/giga

echo "🚀 Preparando archivos para Railway..."

# 1. Renombrar Dockerfiles de producción
echo "📝 Renombrando Dockerfiles..."
mv back/Dockerfile.prod.backend back/Dockerfile.prod
mv front/Dockerfile.prod.frontend front/Dockerfile.prod

echo "✅ Dockerfiles renombrados:"
echo "   - back/Dockerfile.prod"
echo "   - front/Dockerfile.prod"

# 2. Verificar que los archivos existen
echo ""
echo "🔍 Verificando archivos necesarios..."

archivos_necesarios=(
    "docker-compose.prod.yml"
    ".env.railway.example"
    "back/Dockerfile.prod"
    "front/Dockerfile.prod"
)

todos_ok=true
for archivo in "${archivos_necesarios[@]}"; do
    if [ -f "$archivo" ]; then
        echo "   ✅ $archivo"
    else
        echo "   ❌ $archivo - NO ENCONTRADO"
        todos_ok=false
    fi
done

if [ "$todos_ok" = false ]; then
    echo ""
    echo "❌ Faltan archivos necesarios. Revisa la configuración."
    exit 1
fi

# 3. Mostrar estado de git
echo ""
echo "📊 Estado de Git:"
git status --short

# 4. Preparar commit
echo ""
echo "📦 Preparando commit..."
git add docker-compose.prod.yml
git add .env.railway.example
git add back/Dockerfile.prod
git add front/Dockerfile.prod
git add .gitignore
git add bd/init-scripts/01-init-database.sh

echo ""
echo "✅ Archivos agregados al staging area"
echo ""
echo "📝 Archivos listos para commit:"
git status --short

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ PREPARACIÓN COMPLETA"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎯 PRÓXIMOS PASOS:"
echo ""
echo "1️⃣  Hacer commit:"
echo '    git commit -m "feat: archivos de producción para Railway"'
echo ""
echo "2️⃣  Push al repositorio:"
echo "    git push origin version-limpia"
echo ""
echo "3️⃣  Generar SECRET_KEY:"
echo "    python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
echo ""
echo "4️⃣  Ir a Railway y crear proyecto desde GitHub"
echo ""
echo "📚 Ver documentación completa en:"
echo "    documentacion/mio/CHECKLIST_DEPLOYMENT_RAILWAY.md"
echo ""
