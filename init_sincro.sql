CREATE DATABASE sincro;

USE sincro;

-- TABLA 1: Centros de Reconocimiento
CREATE TABLE centros_reconocimiento (
    id_centro INT PRIMARY KEY AUTO_INCREMENT,
    nit VARCHAR(20) UNIQUE NOT NULL,
    nombre_centro VARCHAR(200) NOT NULL,
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    telefono VARCHAR(20),
    habilitacion_ministerio VARCHAR(50),
    registro_salud VARCHAR(50),
    acreditacion VARCHAR(50),

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    INDEX idx_activo (activo)
);

-- TABLA 2: Usuarios/Pacientes
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    numero_identificacion VARCHAR(20) UNIQUE NOT NULL,
    tipo_identificacion VARCHAR(5) NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    edad INT,
    sexo CHAR(1),
    estado_civil VARCHAR(20),
    grupo_sanguineo VARCHAR(5),
    nivel_educativo VARCHAR(50),
    ocupacion VARCHAR(100),
    eps VARCHAR(100),
    regimen_afiliacion VARCHAR(50),
    telefono VARCHAR(20),
    direccion VARCHAR(200),
    ciudad_residencia VARCHAR(100),

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    INDEX idx_identificacion (numero_identificacion),
    INDEX idx_activo (activo)
);

-- TABLA 3: Contactos de Emergencia
CREATE TABLE contactos_emergencia (
    id_contacto INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    nombre_contacto VARCHAR(100),
    telefono VARCHAR(20),
    parentesco VARCHAR(50),

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    INDEX idx_usuario (id_usuario),
    INDEX idx_activo (activo)
);

-- TABLA 4: Evaluaciones Principales
CREATE TABLE evaluaciones (
    id_evaluacion INT PRIMARY KEY AUTO_INCREMENT,
    numero_reconocimiento VARCHAR(50) UNIQUE NOT NULL,
    id_usuario INT NOT NULL,
    id_centro INT NOT NULL,
    fecha_evaluacion DATETIME NOT NULL,
    fecha_certificacion DATETIME,
    fecha_impresion DATETIME,
    numero_factura VARCHAR(50),
    tramite VARCHAR(50),
    categoria VARCHAR(10),
    grupo_categoria VARCHAR(20),
    concepto_final VARCHAR(20),
    numero_certificado_runt VARCHAR(50),
    numero_resultado VARCHAR(50),
    fecha_vencimiento DATETIME,
    vigencia_meses INT,

    -- Gestión de archivos PDF
    ruta_pdf VARCHAR(500),
    nombre_archivo_pdf VARCHAR(255),
    hash_archivo VARCHAR(64), -- SHA-256 para verificar integridad
    tamanio_archivo_kb INT,
    fecha_carga_pdf DATETIME,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_centro) REFERENCES centros_reconocimiento(id_centro),
    INDEX idx_usuario (id_usuario),
    INDEX idx_fecha (fecha_evaluacion),
    INDEX idx_numero_reconocimiento (numero_reconocimiento),
    INDEX idx_ruta_pdf (ruta_pdf),
    INDEX idx_activo (activo)
);

-- TABLA 5: Profesionales de Salud
CREATE TABLE profesionales (
    id_profesional INT PRIMARY KEY AUTO_INCREMENT,
    registro_medico VARCHAR(50) UNIQUE NOT NULL,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL,
    especialidad VARCHAR(50) NOT NULL,
    numero_identificacion VARCHAR(20),
    fecha_firma DATETIME,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    INDEX idx_activo (activo),
    INDEX idx_especialidad (especialidad)
);

-- TABLA 6: Evaluación Fonoaudiológica
CREATE TABLE eval_fonoaudiologia (
    id_fono INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_profesional INT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,

    -- Oído Derecho (OD)
    freq_250_od DECIMAL(5,2),
    freq_500_od DECIMAL(5,2),
    freq_1000_od DECIMAL(5,2),
    freq_2000_od DECIMAL(5,2),
    freq_3000_od DECIMAL(5,2),
    freq_4000_od DECIMAL(5,2),
    freq_6000_od DECIMAL(5,2),
    freq_8000_od DECIMAL(5,2),
    pta_od DECIMAL(5,2),

    -- Oído Izquierdo (OI)
    freq_250_oi DECIMAL(5,2),
    freq_500_oi DECIMAL(5,2),
    freq_1000_oi DECIMAL(5,2),
    freq_2000_oi DECIMAL(5,2),
    freq_3000_oi DECIMAL(5,2),
    freq_4000_oi DECIMAL(5,2),
    freq_6000_oi DECIMAL(5,2),
    freq_8000_oi DECIMAL(5,2),
    pta_oi DECIMAL(5,2),

    -- Ayudas auditivas
    audifono VARCHAR(50),
    implante_coclear VARCHAR(50),

    -- Diagnóstico
    categoria VARCHAR(10),
    concepto VARCHAR(20),
    impresion_diagnostica TEXT,
    observaciones TEXT,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- TABLA 7: Evaluación Psicológica
CREATE TABLE eval_psicologia (
    id_psico INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_profesional INT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,

    -- Pruebas de desempeño
    atencion_tiempo DECIMAL(5,2),
    atencion_errores INT,
    reaccion_multiple_tiempo DECIMAL(5,2),
    reaccion_multiple_errores INT,
    anticipacion_velocidad DECIMAL(5,2),
    coord_bimanual_tiempo DECIMAL(5,2),
    coord_bimanual_errores INT,
    reaccion_frenado DECIMAL(5,2),

    -- Evaluaciones
    inteligencia_practica VARCHAR(20),
    personalidad_puntaje INT,
    sustancias_puntaje INT,
    coeficiente_intelectual INT,
    items_acertados_tepsicon INT,

    -- Diagnóstico
    categoria VARCHAR(10),
    concepto VARCHAR(20),
    impresion_diagnostica TEXT,
    observaciones TEXT,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- TABLA 8: Cuestionario TEPSICON
CREATE TABLE tepsicon_respuestas (
    id_respuesta INT PRIMARY KEY AUTO_INCREMENT,
    id_psico INT NOT NULL,
    bloque VARCHAR(10),
    numero_pregunta INT,
    pregunta TEXT,
    respuesta VARCHAR(50),
    criterio_esperado VARCHAR(10),
    FOREIGN KEY (id_psico) REFERENCES eval_psicologia(id_psico) ON DELETE CASCADE,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    INDEX idx_psico (id_psico),
    INDEX idx_activo (activo)
);

-- TABLA 9: Evaluación Optométrica
CREATE TABLE eval_optometria (
    id_opto INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_profesional INT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,

    -- Agudeza visual lejana
    av_lejana_binocular VARCHAR(10),
    av_lejana_oi VARCHAR(10),
    av_lejana_od VARCHAR(10),

    -- Agudeza visual cercana
    av_cercana_binocular DECIMAL(5,2),
    av_cercana_oi DECIMAL(5,2),
    av_cercana_od DECIMAL(5,2),

    -- Campimetría
    campimetria_vertical INT,
    campimetria_horizontal INT,

    -- Otras evaluaciones
    discriminacion_colores VARCHAR(20),
    sensibilidad_contraste VARCHAR(20),
    vision_mesopica VARCHAR(20),
    recuperacion_encandilamiento VARCHAR(10),
    encandilamiento_segundos INT,
    phorias_lejanas VARCHAR(50),
    phorias_cercanas VARCHAR(50),
    diplopia VARCHAR(50),
    vision_profundidad_pct INT,

    -- Diagnóstico
    categoria VARCHAR(10),
    concepto VARCHAR(20),
    impresion_diagnostica TEXT,
    observaciones TEXT,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- TABLA 10: Oftalmoscopia - Hallazgos
CREATE TABLE oftalmoscopia_hallazgos (
    id_hallazgo INT PRIMARY KEY AUTO_INCREMENT,
    id_opto INT NOT NULL,
    estructura VARCHAR(50),
    tipo_hallazgo VARCHAR(100),
    ojo_izquierdo VARCHAR(50),
    ojo_derecho VARCHAR(50),

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_opto) REFERENCES eval_optometria(id_opto) ON DELETE CASCADE,
    INDEX idx_opto (id_opto),
    INDEX idx_estructura (estructura),
    INDEX idx_activo (activo)
);

-- TABLA 11: Evaluación Médica General
CREATE TABLE eval_medicina_general (
    id_medico INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_profesional INT,
    fecha_inicio DATETIME,
    fecha_fin DATETIME,

    -- Medidas vitales
    talla_cm DECIMAL(5,2),
    peso_kg DECIMAL(5,2),
    frecuencia_respiratoria INT,
    frecuencia_cardiaca INT,
    tension_arterial VARCHAR(20),
    imc DECIMAL(5,2),

    -- Diagnóstico
    categoria VARCHAR(10),
    concepto VARCHAR(20),
    impresion_diagnostica TEXT,
    observaciones TEXT,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_profesional) REFERENCES profesionales(id_profesional),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- TABLA 12: Sistemas Evaluados - Medicina General
CREATE TABLE sistemas_evaluados (
    id_sistema INT PRIMARY KEY AUTO_INCREMENT,
    id_medico INT NOT NULL,
    sistema VARCHAR(50),
    hallazgo VARCHAR(100),
    resultado VARCHAR(50),

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_medico) REFERENCES eval_medicina_general(id_medico) ON DELETE CASCADE,
    INDEX idx_medico (id_medico),
    INDEX idx_sistema (sistema),
    INDEX idx_activo (activo)
);

-- TABLA 13: Restricciones y Observaciones
CREATE TABLE restricciones (
    id_restriccion INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    codigo_restriccion VARCHAR(10),
    descripcion_restriccion TEXT,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- TABLA 14: Concepto Final Detallado
CREATE TABLE concepto_final (
    id_concepto INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_certificador INT,
    tramite VARCHAR(50),
    categoria VARCHAR(10),
    concepto_general TEXT,
    observaciones_generales TEXT,
    limitaciones_fisicas_progresivas BOOLEAN DEFAULT FALSE,
    fecha_certificacion DATETIME,
    fecha_vencimiento DATETIME,

    -- Campos de auditoría
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(100),
    deleted_at TIMESTAMP NULL,
    deleted_by VARCHAR(100),

    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_certificador) REFERENCES profesionales(id_profesional),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_activo (activo)
);

-- =============================================
-- TABLAS DE BLOCKCHAIN
-- =============================================

CREATE TABLE IF NOT EXISTS blockchain_auditoria (
    id_auditoria INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT,
    tipo_operacion ENUM('CREACION', 'VALIDACION', 'INTENTO_MODIFICACION') NOT NULL,
    hash_bloque VARCHAR(64),
    es_valida BOOLEAN,
    detalles TEXT,
    ip_origen VARCHAR(45),
    usuario VARCHAR(100),
    timestamp_operacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_timestamp (timestamp_operacion),
    INDEX idx_tipo (tipo_operacion)
);

CREATE TABLE IF NOT EXISTS blockchain_bloques (
    id_bloque INT PRIMARY KEY AUTO_INCREMENT,
    indice INT UNIQUE NOT NULL,
    timestamp DOUBLE NOT NULL,
    hash VARCHAR(64) UNIQUE NOT NULL,
    hash_anterior VARCHAR(64) NOT NULL,
    nonce INT NOT NULL,
    datos_json TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_hash (hash),
    INDEX idx_timestamp (timestamp)
);

CREATE TABLE IF NOT EXISTS blockchain_evaluaciones (
    id_registro INT PRIMARY KEY AUTO_INCREMENT,
    id_evaluacion INT NOT NULL,
    id_bloque INT NOT NULL,
    hash_bloque VARCHAR(64) NOT NULL,
    hash_datos VARCHAR(64) NOT NULL,
    timestamp_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    es_valido BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_evaluacion) REFERENCES evaluaciones(id_evaluacion) ON DELETE CASCADE,
    FOREIGN KEY (id_bloque) REFERENCES blockchain_bloques(id_bloque),
    INDEX idx_evaluacion (id_evaluacion),
    INDEX idx_bloque (id_bloque),
    INDEX idx_hash_datos (hash_datos),
    UNIQUE KEY uk_eval_bloque (id_evaluacion, id_bloque)
);

