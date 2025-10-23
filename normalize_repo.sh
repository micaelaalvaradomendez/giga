#!/bin/bash

# Script para normalizar line endings después de configurar .gitattributes
# Esto se ejecuta UNA SOLA VEZ después de crear el .gitattributes

echo "🔧 Normalizando line endings del repositorio..."

# Renormalizar todos los archivos según .gitattributes
git add --renormalize .

echo "Archivos normalizados. Crear commit con:"
echo "git commit -m 'chore: enforce LF endings via .gitattributes'"
echo ""
echo "Si alguien ya clonó en Windows y tiene problemas, que ejecute:"
echo "   Git Bash: find . -type f -name '*.sh' -print0 | xargs -0 dos2unix"
echo "   O rebuilder Docker: docker compose build --no-cache back"