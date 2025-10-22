#!/bin/bash

echo "🚀 Configurando Sistema GIGA para desarrollo..."

# 1. Crear archivos .env si no existen
if [ ! -f .env ]; then
    echo "📄 Creando archivo .env principal..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
else
    echo "ℹ️  Archivo .env ya existe"
fi

if [ ! -f back/.env ]; then
    echo "📄 Creando archivo .env del backend..."
    cp back/.env.example back/.env
    echo "✅ Archivo .env del backend creado"
else
    echo "ℹ️  Archivo .env del backend ya existe"
fi

# 2. Crear directorio de logs si no existe
if [ ! -d "back/logs" ]; then
    echo "📁 Creando directorio de logs..."
    mkdir -p back/logs
    touch back/logs/django.log
    echo "✅ Directorio de logs creado"
else
    echo "ℹ️  Directorio de logs ya existe"
fi

# 3. Construir contenedores Docker
echo "🐳 Construyendo contenedores Docker..."
docker-compose build

# 4. Iniciar servicios
echo "🔧 Iniciando servicios..."
docker-compose up -d

# 5. Esperar a que la base de datos esté lista
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 10

# 6. Ejecutar migraciones
echo "🗄️  Ejecutando migraciones de base de datos..."
docker-compose exec back python manage.py migrate

# 7. Crear usuarios de prueba
echo "👥 Creando usuarios de prueba..."
docker-compose exec back python manage.py shell << 'EOF'
from personas.models import Usuario, Agente, Area, Rol, AgenteRol

# Crear áreas
area_admin, _ = Area.objects.get_or_create(
    codigo="ADMIN",
    defaults={
        'nombre': 'Administración General',
        'descripcion': 'Área administrativa central'
    }
)

# Crear roles
rol_admin, _ = Rol.objects.get_or_create(
    nombre="Administrador",
    defaults={'descripcion': 'Administrador del sistema'}
)

rol_director, _ = Rol.objects.get_or_create(
    nombre="Director",
    defaults={'descripcion': 'Director de área'}
)

rol_jefatura, _ = Rol.objects.get_or_create(
    nombre="Jefatura",
    defaults={'descripcion': 'Jefe de área'}
)

rol_agente_avanzado, _ = Rol.objects.get_or_create(
    nombre="Agente Avanzado",
    defaults={'descripcion': 'Agente con permisos avanzados'}
)

rol_agente, _ = Rol.objects.get_or_create(
    nombre="Agente",
    defaults={'descripcion': 'Agente básico'}
)

# Crear usuarios de prueba
usuarios_data = [
    {
        'username': 'Tayra Aguila',
        'email': 'tayra.aguila@giga.gov.ar',
        'first_name': 'Tayra',
        'last_name': 'Aguila',
        'cuil': '27123456784',
        'password': '12345678',
        'rol': rol_admin
    },
    {
        'username': 'Micaela Alvarado',
        'email': 'micaela.alvarado@giga.gov.ar',
        'first_name': 'Micaela',
        'last_name': 'Alvarado',
        'cuil': '27234567894',
        'password': 'admin123',
        'rol': rol_director
    },
    {
        'username': 'Cristian Garcia',
        'email': 'cristian.garcia@giga.gov.ar',
        'first_name': 'Cristian',
        'last_name': 'Garcia',
        'cuil': '27345678904',
        'password': 'admin123',
        'rol': rol_jefatura
    },
    {
        'username': 'Leandro Gomez',
        'email': 'leandro.gomez@giga.gov.ar',
        'first_name': 'Leandro',
        'last_name': 'Gomez',
        'cuil': '27456789014',
        'password': 'admin123',
        'rol': rol_agente_avanzado
    },
    {
        'username': 'Teresa Criniti',
        'email': 'teresa.criniti@giga.gov.ar',
        'first_name': 'Teresa',
        'last_name': 'Criniti',
        'cuil': '27567890124',
        'password': 'admin123',
        'rol': rol_agente
    },
    {
        'username': 'Pamela Frers',
        'email': 'pamela.frers@giga.gov.ar',
        'first_name': 'Pamela',
        'last_name': 'Frers',
        'cuil': '27678901234',
        'password': 'admin123',
        'rol': rol_agente
    }
]

for user_data in usuarios_data:
    if not Usuario.objects.filter(cuil=user_data['cuil']).exists():
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            cuil=user_data['cuil']
        )
        
        # Crear agente
        agente = Agente.objects.create(
            usuario=usuario,
            dni=user_data['cuil'][2:10],  # Extraer DNI del CUIL
            apellido=user_data['last_name'],
            nombre=user_data['first_name'],
            fecha_nac='1990-01-01',
            email=user_data['email'],
            categoria_revista='A1',
            agrupacion='EPU'
        )
        
        # Asignar rol
        AgenteRol.objects.create(
            usuario=usuario,
            rol=user_data['rol'],
            area=area_admin
        )
        
        print(f"Usuario creado: {usuario.username} - CUIL: {usuario.cuil}")

print("✅ Usuarios de prueba creados exitosamente")
EOF

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "📋 Credenciales de prueba:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CUIL: 27-12345678-4 | Contraseña: 12345678 | Rol: Administrador"
echo "CUIL: 27-23456789-4 | Contraseña: admin123  | Rol: Director"
echo "CUIL: 27-34567890-4 | Contraseña: admin123  | Rol: Jefatura"
echo "CUIL: 27-45678901-4 | Contraseña: admin123  | Rol: Agente Avanzado"
echo "CUIL: 27-56789012-4 | Contraseña: admin123  | Rol: Agente"
echo "CUIL: 27-67890123-4 | Contraseña: admin123  | Rol: Agente"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 URLs del sistema:"
echo "• Frontend: http://localhost:5173"
echo "• Backend:  http://localhost:8000"
echo "• Admin:    http://localhost:8000/admin"
echo ""
echo "🔧 Para detener el sistema: docker-compose down"
echo "🔧 Para ver logs: docker-compose logs -f"