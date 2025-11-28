-- =====================================================
-- TABLAS DE DJANGO - Sistema GIGA
-- Archivo: 09-django-tables.sql
-- Descripción: Tablas requeridas por Django para migraciones
-- =====================================================

-- Tabla para tracking de migraciones de Django
CREATE TABLE IF NOT EXISTS django_migrations (
    id BIGSERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para tipos de contenido (Django ContentType)
CREATE TABLE IF NOT EXISTS django_content_type (
    id BIGSERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Tabla para sesiones de Django
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

CREATE INDEX IF NOT EXISTS django_session_expire_date_idx ON django_session(expire_date);

-- Tablas de autenticación de Django
CREATE TABLE IF NOT EXISTS auth_permission (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id BIGINT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE CASCADE,
    UNIQUE(content_type_id, codename)
);

CREATE TABLE IF NOT EXISTS auth_group (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGSERIAL PRIMARY KEY,
    group_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(group_id, permission_id)
);

CREATE TABLE IF NOT EXISTS auth_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN NOT NULL DEFAULT false,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    email VARCHAR(254),
    is_staff BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS auth_user_groups (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(user_id, permission_id)
);

CREATE TABLE IF NOT EXISTS django_admin_log (
    id BIGSERIAL PRIMARY KEY,
    action_time TIMESTAMP NOT NULL,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id BIGINT,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);

-- Índices para Django
CREATE INDEX IF NOT EXISTS auth_permission_content_type_id_idx ON auth_permission(content_type_id);
CREATE INDEX IF NOT EXISTS auth_group_permissions_group_id_idx ON auth_group_permissions(group_id);
CREATE INDEX IF NOT EXISTS auth_group_permissions_permission_id_idx ON auth_group_permissions(permission_id);
CREATE INDEX IF NOT EXISTS auth_user_groups_user_id_idx ON auth_user_groups(user_id);
CREATE INDEX IF NOT EXISTS auth_user_groups_group_id_idx ON auth_user_groups(group_id);
CREATE INDEX IF NOT EXISTS auth_user_user_permissions_user_id_idx ON auth_user_user_permissions(user_id);
CREATE INDEX IF NOT EXISTS auth_user_user_permissions_permission_id_idx ON auth_user_user_permissions(permission_id);
CREATE INDEX IF NOT EXISTS django_admin_log_content_type_id_idx ON django_admin_log(content_type_id);
CREATE INDEX IF NOT EXISTS django_admin_log_user_id_idx ON django_admin_log(user_id);

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Tablas de Django creadas exitosamente';
END $$;
