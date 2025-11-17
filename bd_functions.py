"""
Script para poblar la base de datos de evaluaciones médicas de conductores
con datos aleatorios realistas basados en la Resolución 000217 de 2014
"""

import mysql.connector
from mysql.connector import Error
import random
from datetime import datetime, timedelta
from faker import Faker
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

# Inicializar Faker con locale español
fake = Faker('es_CO')

# =============================================
# CONFIGURACIÓN DE CONEXIÓN A BASE DE DATOS
# =============================================
DB_CONFIG = {
    'host':  os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSW'),
    'database': os.getenv('DB_NAME'),
    'port': os.getenv('DB_PORT')
}

ANIO_INICIO = 2018
ANIO_FIN = 2025

# =============================================
# DATOS BASE PARA GENERACIÓN
# =============================================

CENTROS_RECONOCIMIENTO = [
    {
        'nit': '901603003-9',
        'nombre': 'CENTRO DE RECONOCIMIENTO DE CONDUCTORES LOS BALCANES SAS',
        'direccion': 'Cra 2 a # 49-05 piso 01',
        'ciudad': 'Cali',
        'departamento': 'Valle del Cauca',
        'telefono': '3007080089',
        'habilitacion': '000',
        'registro_salud': '760011547501',
        'acreditacion': '23CEP067'
    },
    {
        'nit': '900123456-7',
        'nombre': 'CENTRO MÉDICO AUTOMOTRIZ DEL NORTE SAS',
        'direccion': 'Calle 100 # 15-20',
        'ciudad': 'Bogotá',
        'departamento': 'Cundinamarca',
        'telefono': '3101234567',
        'habilitacion': '001',
        'registro_salud': '110012345678',
        'acreditacion': '23CEP001'
    },
    {
        'nit': '900234567-8',
        'nombre': 'EVALUACIONES MÉDICAS CONDUCTORES MEDELLÍN SAS',
        'direccion': 'Carrera 43A # 7-50',
        'ciudad': 'Medellín',
        'departamento': 'Antioquia',
        'telefono': '3209876543',
        'habilitacion': '002',
        'registro_salud': '050023456789',
        'acreditacion': '23CEP002'
    },
    {
        'nit': '900345678-9',
        'nombre': 'CENTRO DE RECONOCIMIENTO VIAL CARIBE SAS',
        'direccion': 'Avenida El Río # 45-67',
        'ciudad': 'Barranquilla',
        'departamento': 'Atlántico',
        'telefono': '3158765432',
        'habilitacion': '003',
        'registro_salud': '080034567890',
        'acreditacion': '23CEP003'
    },
    {
        'nit': '900456789-0',
        'nombre': 'SERVICIOS MÉDICOS PARA CONDUCTORES SANTANDER SAS',
        'direccion': 'Calle 36 # 19-02',
        'ciudad': 'Bucaramanga',
        'departamento': 'Santander',
        'telefono': '3187654321',
        'habilitacion': '004',
        'registro_salud': '680045678901',
        'acreditacion': '23CEP004'
    }
]

CIUDADES_COLOMBIA = [
    'Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena',
    'Bucaramanga', 'Pereira', 'Manizales', 'Ibagué', 'Santa Marta',
    'Cúcuta', 'Villavicencio', 'Pasto', 'Neiva', 'Armenia'
]

GRUPOS_SANGUINEOS = ['O +', 'O -', 'A +', 'A -', 'B +', 'B -', 'AB +', 'AB -']
ESTADOS_CIVILES = ['Soltero(a)', 'Casado(a)', 'Unión Libre', 'Divorciado(a)', 'Viudo(a)']
NIVELES_EDUCATIVOS = ['Primaria', 'Bachillerato', 'Técnico', 'Tecnólogo', 'Profesional', 'Posgrado']
OCUPACIONES = ['INDEPENDIENTE', 'EMPLEADO', 'CONDUCTOR', 'PENSIONADO', 'COMERCIANTE', 'PROFESIONAL']
EPS_LIST = ['NUEVA EPS SA', 'SURA', 'SANITAS', 'COMPENSAR', 'SALUD TOTAL', 'FAMISANAR']
REGIMENES = ['Contributivo', 'Subsidiado', 'Especial']

CATEGORIAS = ['A1', 'A2', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
TRAMITES = ['Obtención', 'Refrendación', 'Recategorización']
CONCEPTOS = ['APTO', 'APTO CON RESTRICCION', 'NO APTO']

ESPECIALIDADES_PROFESIONALES = ['Fonoaudiología', 'Psicología', 'Optometría', 'Medicina General']

RESTRICCIONES_CODIGOS = [
    ('1', 'Conducir con lentes'),
    ('2', 'Conducir con audífono'),
    ('36', 'Pérdida auditiva leve PAL'),
    ('15', 'Solo vehículos automáticos'),
    ('20', 'Solo conducir de día')
]


# =============================================
# FUNCIONES DE CONEXIÓN
# =============================================

def crear_conexion():
    """Crear conexión a la base de datos"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Conexión exitosa a la base de datos")
            return connection
    except Error as e:
        print(f"❌ Error al conectar a la base de datos: {e}")
        return None


def cerrar_conexion(connection):
    """Cerrar conexión a la base de datos"""
    if connection and connection.is_connected():
        connection.close()
        print("Conexión cerrada")


# =============================================
# FUNCIONES DE INSERCIÓN
# =============================================

def insertar_centros_reconocimiento(cursor, usuario='admin@sistema.com'):
    """Insertar los 5 centros de reconocimiento"""
    print("\n📍 Insertando centros de reconocimiento...")

    query = """
    INSERT IGNORE INTO centros_reconocimiento 
    (nit, nombre_centro, direccion, ciudad, departamento, telefono, 
     habilitacion_ministerio, registro_salud, acreditacion, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for centro in CENTROS_RECONOCIMIENTO:
        values = (
            centro['nit'], centro['nombre'], centro['direccion'],
            centro['ciudad'], centro['departamento'], centro['telefono'],
            centro['habilitacion'], centro['registro_salud'],
            centro['acreditacion'], usuario
        )
        cursor.execute(query, values)

    print(f"{len(CENTROS_RECONOCIMIENTO)} centros insertados")


def generar_numero_identificacion():
    """Generar número de identificación único"""
    return str(random.randint(10000000, 99999999))


def generar_telefono():
    """Generar número de teléfono celular colombiano"""
    return f"3{random.randint(100000000, 199999999)}"


def insertar_usuarios(cursor, cantidad=1000, usuario='admin@sistema.com'):
    """Insertar usuarios/pacientes"""
    print(f"\n👤 Insertando {cantidad} usuarios...")

    query = """
    INSERT IGNORE INTO usuarios 
    (numero_identificacion, tipo_identificacion, nombres, apellidos, 
     fecha_nacimiento, edad, sexo, estado_civil, grupo_sanguineo, 
     nivel_educativo, ocupacion, eps, regimen_afiliacion, telefono, 
     direccion, ciudad_residencia, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    usuarios_ids = []

    for i in range(cantidad):
        # Generar fecha de nacimiento (18-85 años)
        edad = random.randint(18, 85)
        fecha_nacimiento = fake.date_of_birth(minimum_age=edad, maximum_age=edad)

        sexo = random.choice(['M', 'F'])
        nombres = fake.first_name_male() if sexo == 'M' else fake.first_name_female()
        apellidos = f"{fake.last_name()} {fake.last_name()}"

        values = (
            generar_numero_identificacion(),
            'CC',
            nombres.upper(),
            apellidos.upper(),
            fecha_nacimiento,
            edad,
            sexo,
            random.choice(ESTADOS_CIVILES),
            random.choice(GRUPOS_SANGUINEOS),
            random.choice(NIVELES_EDUCATIVOS),
            random.choice(OCUPACIONES),
            random.choice(EPS_LIST),
            random.choice(REGIMENES),
            generar_telefono(),
            fake.street_address(),
            random.choice(CIUDADES_COLOMBIA),
            usuario
        )

        cursor.execute(query, values)
        usuarios_ids.append(cursor.lastrowid)

        if (i + 1) % 100 == 0:
            print(f"   ⏳ Insertados {i + 1}/{cantidad} usuarios...")

    print(f"{cantidad} usuarios insertados")
    return usuarios_ids


def insertar_contactos_emergencia(cursor, usuarios_ids, usuario='admin@sistema.com'):
    """Insertar contactos de emergencia"""
    print(f"\n📞 Insertando contactos de emergencia...")

    query = """
    INSERT IGNORE INTO contactos_emergencia 
    (id_usuario, nombre_contacto, telefono, parentesco, created_by)
    VALUES (%s, %s, %s, %s, %s)
    """

    parentescos = ['Hijo(a)', 'Padre/Madre', 'Hermano(a)', 'Cónyuge', 'Amigo(a)', 'Otro']

    for id_usuario in usuarios_ids:
        values = (
            id_usuario,
            fake.name().upper(),
            generar_telefono(),
            random.choice(parentescos),
            usuario
        )
        cursor.execute(query, values)

    print(f"{len(usuarios_ids)} contactos de emergencia insertados")


def insertar_profesionales(cursor, cantidad_por_especialidad=10, usuario='admin@sistema.com'):
    """Insertar profesionales de salud"""
    print(f"\n👨‍⚕️ Insertando profesionales de salud...")

    query = """
    INSERT IGNORE INTO profesionales 
    (registro_medico, nombres, apellidos, especialidad, numero_identificacion, created_by)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    profesionales_ids = {especialidad: [] for especialidad in ESPECIALIDADES_PROFESIONALES}

    for especialidad in ESPECIALIDADES_PROFESIONALES:
        for i in range(cantidad_por_especialidad):
            sexo = random.choice(['M', 'F'])
            nombres = fake.first_name_male() if sexo == 'M' else fake.first_name_female()
            apellidos = f"{fake.last_name()} {fake.last_name()}"

            values = (
                str(random.randint(100000, 999999)),
                nombres.upper(),
                apellidos.upper(),
                especialidad,
                generar_numero_identificacion(),
                usuario
            )

            cursor.execute(query, values)
            profesionales_ids[especialidad].append(cursor.lastrowid)

    total = len(ESPECIALIDADES_PROFESIONALES) * cantidad_por_especialidad
    print(f"{total} profesionales insertados")
    return profesionales_ids


def generar_hash_archivo(texto):
    """Generar hash SHA-256 para simular archivo PDF"""
    return hashlib.sha256(texto.encode()).hexdigest()


def insertar_evaluaciones(cursor, usuarios_ids, profesionales_ids, cantidad=1000, usuario='admin@sistema.com'):
    """Insertar evaluaciones completas"""
    print(f"\n📋 Insertando {cantidad} evaluaciones completas...")

    evaluaciones_ids = []

    # Query para evaluación principal
    query_eval = """
    INSERT IGNORE INTO evaluaciones 
    (numero_reconocimiento, id_usuario, id_centro, fecha_evaluacion, 
     fecha_certificacion, fecha_impresion, numero_factura, tramite, 
     categoria, grupo_categoria, concepto_final, numero_certificado_runt, 
     numero_resultado, fecha_vencimiento, vigencia_meses,
     ruta_pdf, nombre_archivo_pdf, hash_archivo, tamanio_archivo_kb, 
     fecha_carga_pdf, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for i in range(cantidad):
        # Datos de la evaluación
        numero_reconocimiento = str(random.randint(1000, 9999))
        id_usuario = random.choice(usuarios_ids)
        id_centro = random.randint(1, 5)  # 5 centros

        # Fechas
        fecha_eval = fake.date_time_between(start_date='-2y', end_date='now')
        fecha_cert = fecha_eval + timedelta(hours=random.randint(1, 24))
        fecha_impresion = fecha_cert + timedelta(hours=random.randint(1, 2))
        fecha_vencimiento = fecha_cert + timedelta(days=365 * random.choice([1, 2, 3, 5]))

        categoria = random.choice(CATEGORIAS)
        concepto = random.choice(CONCEPTOS)

        # Generar datos del PDF
        nombre_pdf = f"Informe_{numero_reconocimiento}_{id_usuario}.pdf"
        ruta_pdf = f"/documentos/evaluaciones/{fecha_eval.year}/{fecha_eval.month:02d}/{nombre_pdf}"
        hash_pdf = generar_hash_archivo(f"{numero_reconocimiento}{id_usuario}")

        values_eval = (
            numero_reconocimiento, id_usuario, id_centro, fecha_eval,
            fecha_cert, fecha_impresion, str(random.randint(1000, 9999)),
            random.choice(TRAMITES), categoria, 'Grupo 1', concepto,
            f"A-{random.randint(1000, 9999)}-{random.randint(100000, 999999)}",
            str(random.randint(10000000, 99999999)),
            fecha_vencimiento, random.choice([12, 24, 36, 60]),
            ruta_pdf, nombre_pdf, hash_pdf, random.randint(150, 500),
            fecha_impresion, usuario
        )

        cursor.execute(query_eval, values_eval)
        id_evaluacion = cursor.lastrowid
        evaluaciones_ids.append(id_evaluacion)

        # Insertar evaluaciones especializadas
        insertar_eval_fonoaudiologia(cursor, id_evaluacion, profesionales_ids['Fonoaudiología'], usuario='usuario@sistema.com')
        insertar_eval_psicologia(cursor, id_evaluacion, profesionales_ids['Psicología'], usuario='usuario@sistema.com')
        insertar_eval_optometria(cursor, id_evaluacion, profesionales_ids['Optometría'], usuario='usuario@sistema.com')
        insertar_eval_medicina(cursor, id_evaluacion, profesionales_ids['Medicina General'], usuario='usuario@sistema.com')

        # Insertar restricciones si es APTO CON RESTRICCION
        if concepto == 'APTO CON RESTRICCION':
            insertar_restricciones(cursor, id_evaluacion, usuario='usuario@sistema.com')

        # Insertar concepto final
        insertar_concepto_final(cursor, id_evaluacion, profesionales_ids['Medicina General'], fecha_cert,
                                fecha_vencimiento, usuario='usuario@sistema.com')

        if (i + 1) % 100 == 0:
            print(f"   ⏳ Insertadas {i + 1}/{cantidad} evaluaciones...")

    print(f"{cantidad} evaluaciones completas insertadas")
    return evaluaciones_ids


def insertar_eval_fonoaudiologia(cursor, id_evaluacion, profesionales_ids, usuario='usuario@sistema.com'):
    """Insertar evaluación fonoaudiológica"""
    query = """
    INSERT IGNORE INTO eval_fonoaudiologia 
    (id_evaluacion, id_profesional, fecha_inicio, fecha_fin,
     freq_250_od, freq_500_od, freq_1000_od, freq_2000_od, 
     freq_3000_od, freq_4000_od, freq_6000_od, freq_8000_od, pta_od,
     freq_250_oi, freq_500_oi, freq_1000_oi, freq_2000_oi,
     freq_3000_oi, freq_4000_oi, freq_6000_oi, freq_8000_oi, pta_oi,
     audifono, implante_coclear, categoria, concepto, 
     impresion_diagnostica, observaciones, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    fecha_inicio = fake.date_time_between(start_date='-1d', end_date='now')
    fecha_fin = fecha_inicio + timedelta(minutes=random.randint(5, 15))

    # Generar valores auditivos (0-40 dB es normal a leve)
    valores_od = [random.uniform(0, 40) for _ in range(8)]
    valores_oi = [random.uniform(0, 40) for _ in range(8)]

    # Calcular PTA (promedio de 500, 1000, 2000 Hz)
    pta_od = round((valores_od[1] + valores_od[2] + valores_od[3]) / 3, 2)
    pta_oi = round((valores_oi[1] + valores_oi[2] + valores_oi[3]) / 3, 2)

    concepto = 'APTO' if pta_od <= 25 and pta_oi <= 25 else 'APTO CON RESTRICCION'

    values = (
        id_evaluacion, random.choice(profesionales_ids), fecha_inicio, fecha_fin,
        *valores_od, pta_od,
        *valores_oi, pta_oi,
        'Ninguno', 'Ninguno', random.choice(CATEGORIAS), concepto,
        'Audición normal' if concepto == 'APTO' else 'Hipoacusia leve',
        'APTO' if concepto == 'APTO' else 'APTO CON PAL - SE RECOMIENDA CONTROL AUDITIVO',
        usuario
    )

    cursor.execute(query, values)


def insertar_eval_psicologia(cursor, id_evaluacion, profesionales_ids, usuario='usuario@sistema.com'):
    """Insertar evaluación psicológica"""
    query = """
    INSERT IGNORE INTO eval_psicologia 
    (id_evaluacion, id_profesional, fecha_inicio, fecha_fin,
     atencion_tiempo, atencion_errores, reaccion_multiple_tiempo,
     reaccion_multiple_errores, anticipacion_velocidad, coord_bimanual_tiempo,
     coord_bimanual_errores, reaccion_frenado, inteligencia_practica,
     personalidad_puntaje, sustancias_puntaje, coeficiente_intelectual,
     items_acertados_tepsicon, categoria, concepto,
     impresion_diagnostica, observaciones, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    fecha_inicio = fake.date_time_between(start_date='-1d', end_date='now')
    fecha_fin = fecha_inicio + timedelta(minutes=random.randint(20, 40))

    # Generar valores de pruebas psicotécnicas (dentro de rangos normales)
    ci = random.randint(89, 125)
    items_acertados = random.randint(11, 15)

    values = (
        id_evaluacion, random.choice(profesionales_ids), fecha_inicio, fecha_fin,
        round(random.uniform(0.15, 0.80), 2), random.randint(0, 3),
        round(random.uniform(0.15, 0.70), 2), random.randint(0, 4),
        round(random.uniform(0.20, 0.90), 2), round(random.uniform(0.02, 10.00), 2),
        random.randint(0, 5), round(random.uniform(0.10, 0.70), 2),
        'Cumple', random.randint(19, 26), random.randint(15, 20),
        ci, items_acertados, random.choice(CATEGORIAS), 'APTO',
        'Candidato apto, cumple con los criterios de aprobación',
        'APTO', usuario
    )

    cursor.execute(query, values)

    # Insertar respuestas TEPSICON
    insertar_tepsicon_respuestas(cursor, cursor.lastrowid, usuario='usuario@sistema.com')


def insertar_tepsicon_respuestas(cursor, id_psico, usuario='usuario@sistema.com'):
    """Insertar respuestas del cuestionario TEPSICON"""
    query = """
    INSERT IGNORE INTO tepsicon_respuestas 
    (id_psico, bloque, numero_pregunta, pregunta, respuesta, criterio_esperado, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    # Insertar algunas respuestas de ejemplo (normalmente serían 63 preguntas)
    preguntas_muestra = [
        ('10.1', 1, 'Con frecuencia se me olvida mi nombre', 'NO', 'NO'),
        ('10.3', 8, 'Con frecuencia veo cosas que nadie mas ve', 'NO', 'NO'),
        ('10.4', 10, 'En los últimos meses he pensado en dejar de vivir', 'NO', 'NO'),
        ('11.1', 28, 'Combino licores para embriagarme más rápido', 'NO', 'NO'),
        ('11.2', 31, 'Puedo pasar más de un mes sin consumir alcohol', 'NO', 'SI'),
    ]

    for bloque, num_pregunta, pregunta, respuesta, criterio in preguntas_muestra:
        values = (id_psico, bloque, num_pregunta, pregunta, respuesta, criterio, usuario)
        cursor.execute(query, values)


def insertar_eval_optometria(cursor, id_evaluacion, profesionales_ids, usuario='usuario@sistema.com'):
    """Insertar evaluación optométrica"""
    query = """
    INSERT IGNORE INTO eval_optometria 
    (id_evaluacion, id_profesional, fecha_inicio, fecha_fin,
     av_lejana_binocular, av_lejana_oi, av_lejana_od,
     av_cercana_binocular, av_cercana_oi, av_cercana_od,
     campimetria_vertical, campimetria_horizontal,
     discriminacion_colores, sensibilidad_contraste, vision_mesopica,
     recuperacion_encandilamiento, encandilamiento_segundos,
     phorias_lejanas, phorias_cercanas, diplopia, vision_profundidad_pct,
     categoria, concepto, impresion_diagnostica, observaciones, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    fecha_inicio = fake.date_time_between(start_date='-1d', end_date='now')
    fecha_fin = fecha_inicio + timedelta(minutes=random.randint(10, 20))

    # Valores de agudeza visual
    agudezas = ['20/20', '20/25', '20/30', '20/40']
    usa_lentes = random.choice([True, False])

    concepto = 'APTO CON RESTRICCION' if usa_lentes else 'APTO'

    values = (
        id_evaluacion, random.choice(profesionales_ids), fecha_inicio, fecha_fin,
        random.choice(agudezas), random.choice(agudezas), random.choice(agudezas),
        round(random.uniform(0.5, 1.0), 2), round(random.uniform(0.5, 1.0), 2),
        round(random.uniform(0.5, 1.0), 2),
        random.randint(70, 90), random.randint(120, 150),
        'Normal', 'Normal', 'Normal',
        '20/20', random.randint(3, 5),
        'No presenta', 'No presenta', 'No presenta', random.randint(75, 95),
        random.choice(CATEGORIAS), concepto,
        'Candidato apto' if not usa_lentes else 'Candidato apto con restricción (gafas)',
        'APTO' if not usa_lentes else 'APTO CON RESTRICCION',
        usuario
    )

    cursor.execute(query, values)


def insertar_eval_medicina(cursor, id_evaluacion, profesionales_ids, usuario='usuario@sistema.com'):
    """Insertar evaluación médica general"""
    query = """
    INSERT IGNORE INTO eval_medicina_general 
    (id_evaluacion, id_profesional, fecha_inicio, fecha_fin,
     talla_cm, peso_kg, frecuencia_respiratoria, frecuencia_cardiaca,
     tension_arterial, imc, categoria, concepto,
     impresion_diagnostica, observaciones, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    fecha_inicio = fake.date_time_between(start_date='-1d', end_date='now')
    fecha_fin = fecha_inicio + timedelta(minutes=random.randint(15, 30))

    # Generar signos vitales realistas
    talla = random.randint(150, 190)
    peso = random.randint(50, 100)
    imc = round(peso / ((talla / 100) ** 2), 2)

    presion_sistolica = random.randint(110, 140)
    presion_diastolica = random.randint(70, 90)

    values = (
        id_evaluacion, random.choice(profesionales_ids), fecha_inicio, fecha_fin,
        talla, peso, random.randint(12, 20), random.randint(60, 100),
        f"{presion_sistolica}/{presion_diastolica}", imc,
        random.choice(CATEGORIAS), 'APTO',
        'Candidato apto, cumple con los criterios de aprobación',
        'CUMPLE RESOLUCION 217/14',
        usuario
    )

    cursor.execute(query, values)

    # Insertar sistemas evaluados
    insertar_sistemas_evaluados(cursor, cursor.lastrowid, usuario='usuario@sistema.com')


def insertar_sistemas_evaluados(cursor, id_medico, usuario='usuario@sistema.com'):
    """Insertar sistemas evaluados en medicina general"""
    query = """
    INSERT IGNORE INTO sistemas_evaluados 
    (id_medico, sistema, hallazgo, resultado, created_by)
    VALUES (%s, %s, %s, %s, %s)
    """

    sistemas = [
        ('Cardiovascular', 'Hipertensión Arterial', random.choice(['Sí presenta', 'No presenta'])),
        ('Respiratorio', 'Disneas', 'No presenta'),
        ('Nervioso', 'Alteraciones del equilibrio', 'No presenta'),
        ('Locomotor', 'Motilidad', 'No presenta')
    ]

    for sistema, hallazgo, resultado in sistemas:
        values = (id_medico, sistema, hallazgo, resultado, usuario)
        cursor.execute(query, values)


def insertar_restricciones(cursor, id_evaluacion, usuario='usuario@sistema.com'):
    """Insertar restricciones para conductores"""
    query = """
    INSERT IGNORE INTO restricciones 
    (id_evaluacion, codigo_restriccion, descripcion_restriccion, created_by)
    VALUES (%s, %s, %s, %s)
    """

    # Seleccionar 1-2 restricciones aleatorias
    num_restricciones = random.randint(1, 2)
    restricciones_seleccionadas = random.sample(RESTRICCIONES_CODIGOS, num_restricciones)

    for codigo, descripcion in restricciones_seleccionadas:
        values = (id_evaluacion, codigo, descripcion, usuario)
        cursor.execute(query, values)


def insertar_concepto_final(cursor, id_evaluacion, profesionales_ids, fecha_cert, fecha_venc, usuario='usuario@sistema.com'):
    """Insertar concepto final de la evaluación"""
    query = """
    INSERT IGNORE INTO concepto_final 
    (id_evaluacion, id_certificador, tramite, categoria, concepto_general,
     observaciones_generales, limitaciones_fisicas_progresivas,
     fecha_certificacion, fecha_vencimiento, created_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        id_evaluacion,
        random.choice(profesionales_ids),
        random.choice(TRAMITES),
        random.choice(CATEGORIAS),
        'Cumple con los criterios de aprobación de la resolución 0217 de 2014 anexo I',
        'El candidato cumple con los requisitos exigidos',
        False,
        fecha_cert,
        fecha_venc,
        usuario
    )

    cursor.execute(query, values)

def distribuir_evaluaciones_por_anio(total_evaluaciones):
    """Distribuir evaluaciones por año con crecimiento orgánico"""
    anios = list(range(ANIO_INICIO, ANIO_FIN + 1))
    num_anios = len(anios)

    # Crecimiento exponencial suave
    pesos = [1.5 ** i for i in range(num_anios)]
    total_peso = sum(pesos)

    distribucion = {}
    evaluaciones_asignadas = 0

    for anio, peso in zip(anios, pesos):
        cantidad = int((peso / total_peso) * total_evaluaciones)
        distribucion[anio] = cantidad
        evaluaciones_asignadas += cantidad

    # Ajustar diferencia por redondeo
    diferencia = total_evaluaciones - evaluaciones_asignadas
    distribucion[anios[-1]] += diferencia

    return distribucion

def generar_fecha_historica(anio_inicio=ANIO_INICIO, anio_fin=ANIO_FIN):
    """Generar fecha aleatoria entre años especificados"""
    fecha_inicio = datetime(anio_inicio, 1, 1)
    fecha_fin = datetime(anio_fin, 12, 31)

    delta = fecha_fin - fecha_inicio
    dias_random = random.randint(0, delta.days)

    fecha = fecha_inicio + timedelta(days=dias_random)

    # Agregar hora aleatoria (8:00 AM - 5:00 PM)
    hora = random.randint(8, 17)
    minuto = random.randint(0, 59)

    return fecha.replace(hour=hora, minute=minuto, second=0)

# =============================================
# FUNCIÓN PRINCIPAL DE POBLACIÓN
# =============================================

def poblar_base_datos(num_usuarios=1000, num_evaluaciones=1000):
    """
    Función principal para poblar la base de datos

    Args:
        num_usuarios: Número de usuarios a crear
        num_evaluaciones: Número de evaluaciones a crear
    """
    connection = crear_conexion()

    if not connection:
        print("❌ No se pudo establecer conexión. Abortando...")
        return

    try:
        cursor = connection.cursor()
        usuario_sistema = 'admin@sistema.com'

        print("=" * 60)
        print("INICIANDO POBLACIÓN DE BASE DE DATOS")
        print("=" * 60)

        # 1. Insertar centros de reconocimiento
        insertar_centros_reconocimiento(cursor, usuario_sistema)
        connection.commit()

        # 2. Insertar profesionales
        profesionales_ids = insertar_profesionales(cursor, cantidad_por_especialidad=10, usuario=usuario_sistema)
        connection.commit()

        # 3. Insertar usuarios
        usuarios_ids = insertar_usuarios(cursor, cantidad=num_usuarios, usuario=usuario_sistema)
        connection.commit()

        # 4. Insertar contactos de emergencia
        insertar_contactos_emergencia(cursor, usuarios_ids, usuario_sistema)
        connection.commit()

        # 5. Insertar evaluaciones completas (con todas las especialidades)
        evaluaciones_ids = insertar_evaluaciones(
            cursor,
            usuarios_ids,
            profesionales_ids,
            cantidad=num_evaluaciones,
            usuario=usuario_sistema
        )
        connection.commit()

        print("\n" + "=" * 60)
        print("POBLACIÓN DE BASE DE DATOS COMPLETADA CON ÉXITO")
        print("=" * 60)
        print(f"\n📊 RESUMEN:")
        print(f"   • Centros de reconocimiento: {len(CENTROS_RECONOCIMIENTO)}")
        print(f"   • Profesionales: {len(ESPECIALIDADES_PROFESIONALES) * 10}")
        print(f"   • Usuarios: {num_usuarios}")
        print(f"   • Contactos de emergencia: {num_usuarios}")
        print(f"   • Evaluaciones completas: {num_evaluaciones}")
        print(f"   • Total de registros: ~{num_usuarios * 2 + num_evaluaciones * 10 + 45}")
        print("=" * 60)

    except Error as e:
        print(f"\n❌ Error durante la población: {e}")
        connection.rollback()

    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(connection)


# =============================================
# CONSULTAS DE VERIFICACIÓN
# =============================================

def verificar_datos():
    """Ejecutar consultas para verificar que los datos se insertaron correctamente"""
    connection = crear_conexion()

    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        print("\n" + "=" * 60)
        print("🔍 VERIFICACIÓN DE DATOS INSERTADOS")
        print("=" * 60)

        # Contar registros por tabla
        tablas = [
            'centros_reconocimiento',
            'usuarios',
            'contactos_emergencia',
            'profesionales',
            'evaluaciones',
            'eval_fonoaudiologia',
            'eval_psicologia',
            'eval_optometria',
            'eval_medicina_general',
            'restricciones',
            'concepto_final'
        ]

        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) as total FROM {tabla}")
            resultado = cursor.fetchone()
            print(f"   📋 {tabla}: {resultado['total']} registros")

        # Consultas adicionales de verificación
        print("\n📊 ESTADÍSTICAS ADICIONALES:")

        # Evaluaciones por concepto
        cursor.execute("""
            SELECT concepto_final, COUNT(*) as total 
            FROM evaluaciones 
            GROUP BY concepto_final
        """)
        print("\n   Evaluaciones por concepto:")
        for row in cursor.fetchall():
            print(f"      • {row['concepto_final']}: {row['total']}")

        # Evaluaciones por centro
        cursor.execute("""
            SELECT c.nombre_centro, COUNT(e.id_evaluacion) as total
            FROM centros_reconocimiento c
            LEFT JOIN evaluaciones e ON c.id_centro = e.id_centro
            GROUP BY c.id_centro
        """)
        print("\n   Evaluaciones por centro:")
        for row in cursor.fetchall():
            print(f"      • {row['nombre_centro'][:50]}: {row['total']}")

        # Evaluaciones por categoría
        cursor.execute("""
            SELECT categoria, COUNT(*) as total 
            FROM evaluaciones 
            GROUP BY categoria
        """)
        print("\n   Evaluaciones por categoría:")
        for row in cursor.fetchall():
            print(f"      • {row['categoria']}: {row['total']}")

        # Evaluación completa de ejemplo
        cursor.execute("""
            SELECT 
                e.numero_reconocimiento,
                u.nombres,
                u.apellidos,
                e.concepto_final,
                e.categoria,
                e.ruta_pdf,
                ef.pta_od,
                ef.pta_oi,
                ep.coeficiente_intelectual,
                eo.av_lejana_binocular,
                emg.tension_arterial,
                emg.imc
            FROM evaluaciones e
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            LEFT JOIN eval_fonoaudiologia ef ON e.id_evaluacion = ef.id_evaluacion
            LEFT JOIN eval_psicologia ep ON e.id_evaluacion = ep.id_evaluacion
            LEFT JOIN eval_optometria eo ON e.id_evaluacion = eo.id_evaluacion
            LEFT JOIN eval_medicina_general emg ON e.id_evaluacion = emg.id_evaluacion
            LIMIT 1
        """)

        print("\n   📄 Ejemplo de evaluación completa:")
        ejemplo = cursor.fetchone()
        if ejemplo:
            print(f"      • Reconocimiento: {ejemplo['numero_reconocimiento']}")
            print(f"      • Paciente: {ejemplo['nombres']} {ejemplo['apellidos']}")
            print(f"      • Concepto: {ejemplo['concepto_final']}")
            print(f"      • Categoría: {ejemplo['categoria']}")
            print(f"      • PTA OD/OI: {ejemplo['pta_od']}/{ejemplo['pta_oi']} dB")
            print(f"      • CI: {ejemplo['coeficiente_intelectual']}")
            print(f"      • AV Binocular: {ejemplo['av_lejana_binocular']}")
            print(f"      • Tensión: {ejemplo['tension_arterial']}")
            print(f"      • IMC: {ejemplo['imc']}")
            print(f"      • PDF: {ejemplo['ruta_pdf']}")

        print("\n" + "=" * 60)

    except Error as e:
        print(f"\n❌ Error en verificación: {e}")

    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(connection)


# =============================================
# CONSULTAS MASIVAS DE EJEMPLO
# =============================================

def ejemplos_consultas_masivas():
    """Ejemplos de consultas masivas para testing de rendimiento"""
    connection = crear_conexion()

    if not connection:
        return

    try:
        cursor = connection.cursor(dictionary=True)

        print("\n" + "=" * 60)
        print("⚡ EJEMPLOS DE CONSULTAS MASIVAS")
        print("=" * 60)

        import time

        # 1. Búsqueda por número de identificación
        print("\n1️⃣  Búsqueda por identificación...")
        inicio = time.time()
        cursor.execute("""
            SELECT u.*, e.numero_reconocimiento, e.concepto_final
            FROM usuarios u
            LEFT JOIN evaluaciones e ON u.id_usuario = e.id_usuario
            WHERE u.numero_identificacion = (SELECT numero_identificacion FROM usuarios LIMIT 1)
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos - {len(resultado)} resultados")

        # 2. Evaluaciones por rango de fechas
        print("\n2️⃣  Evaluaciones en último año...")
        inicio = time.time()
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM evaluaciones
            WHERE fecha_evaluacion >= DATE_SUB(NOW(), INTERVAL 1 YEAR)
        """)
        resultado = cursor.fetchone()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos - {resultado['total']} evaluaciones")

        # 3. Evaluaciones próximas a vencer
        print("\n3️⃣  Evaluaciones próximas a vencer (30 días)...")
        inicio = time.time()
        cursor.execute("""
            SELECT 
                e.numero_reconocimiento,
                u.nombres,
                u.apellidos,
                u.numero_identificacion,
                e.fecha_vencimiento,
                DATEDIFF(e.fecha_vencimiento, NOW()) as dias_restantes
            FROM evaluaciones e
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.fecha_vencimiento BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
            AND e.activo = TRUE
            ORDER BY e.fecha_vencimiento
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos - {len(resultado)} resultados")

        # 4. Estadísticas por centro
        print("\n4️⃣  Estadísticas por centro de reconocimiento...")
        inicio = time.time()
        cursor.execute("""
            SELECT 
                c.nombre_centro,
                c.ciudad,
                COUNT(e.id_evaluacion) as total_evaluaciones,
                SUM(CASE WHEN e.concepto_final = 'APTO' THEN 1 ELSE 0 END) as aptos,
                SUM(CASE WHEN e.concepto_final = 'APTO CON RESTRICCION' THEN 1 ELSE 0 END) as con_restriccion,
                SUM(CASE WHEN e.concepto_final = 'NO APTO' THEN 1 ELSE 0 END) as no_aptos,
                ROUND(AVG(TIMESTAMPDIFF(MINUTE, e.fecha_evaluacion, e.fecha_certificacion)), 2) as tiempo_promedio_min
            FROM centros_reconocimiento c
            LEFT JOIN evaluaciones e ON c.id_centro = e.id_centro
            GROUP BY c.id_centro
            ORDER BY total_evaluaciones DESC
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos")
        for row in resultado:
            print(f"      • {row['nombre_centro'][:40]}")
            print(f"        Total: {row['total_evaluaciones']} | Aptos: {row['aptos']} | "
                  f"Con restricción: {row['con_restriccion']} | No aptos: {row['no_aptos']}")

        # 5. Profesionales más activos
        print("\n5️⃣  Top 10 profesionales más activos...")
        inicio = time.time()
        cursor.execute("""
            SELECT 
                p.nombres,
                p.apellidos,
                p.especialidad,
                COUNT(DISTINCT ef.id_evaluacion) + 
                COUNT(DISTINCT ep.id_evaluacion) + 
                COUNT(DISTINCT eo.id_evaluacion) + 
                COUNT(DISTINCT em.id_evaluacion) as total_evaluaciones
            FROM profesionales p
            LEFT JOIN eval_fonoaudiologia ef ON p.id_profesional = ef.id_profesional
            LEFT JOIN eval_psicologia ep ON p.id_profesional = ep.id_profesional
            LEFT JOIN eval_optometria eo ON p.id_profesional = eo.id_profesional
            LEFT JOIN eval_medicina_general em ON p.id_profesional = em.id_profesional
            GROUP BY p.id_profesional
            ORDER BY total_evaluaciones DESC
            LIMIT 10
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos")
        for i, row in enumerate(resultado, 1):
            print(f"      {i}. {row['nombres']} {row['apellidos']} ({row['especialidad']}) - "
                  f"{row['total_evaluaciones']} evaluaciones")

        # 6. Análisis de restricciones más comunes
        print("\n6️⃣  Restricciones más comunes...")
        inicio = time.time()
        cursor.execute("""
            SELECT 
                r.codigo_restriccion,
                r.descripcion_restriccion,
                COUNT(*) as frecuencia,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM restricciones), 2) as porcentaje
            FROM restricciones r
            WHERE r.activo = TRUE
            GROUP BY r.codigo_restriccion, r.descripcion_restriccion
            ORDER BY frecuencia DESC
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos")
        for row in resultado:
            print(f"      • Código {row['codigo_restriccion']}: {row['descripcion_restriccion']}")
            print(f"        Frecuencia: {row['frecuencia']} ({row['porcentaje']}%)")

        # 7. Distribución de edades de conductores
        print("\n7️⃣  Distribución de edades...")
        inicio = time.time()
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN edad BETWEEN 18 AND 25 THEN '18-25'
                    WHEN edad BETWEEN 26 AND 35 THEN '26-35'
                    WHEN edad BETWEEN 36 AND 45 THEN '36-45'
                    WHEN edad BETWEEN 46 AND 55 THEN '46-55'
                    WHEN edad BETWEEN 56 AND 65 THEN '56-65'
                    ELSE '66+'
                END as rango_edad,
                COUNT(*) as cantidad
            FROM usuarios
            WHERE activo = TRUE
            GROUP BY rango_edad
            ORDER BY rango_edad
        """)
        resultado = cursor.fetchall()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos")
        for row in resultado:
            print(f"      • {row['rango_edad']} años: {row['cantidad']} conductores")

        # 8. Búsqueda de evaluaciones con PDF
        print("\n8️⃣  Evaluaciones con archivos PDF disponibles...")
        inicio = time.time()
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM evaluaciones
            WHERE ruta_pdf IS NOT NULL
            AND activo = TRUE
        """)
        resultado = cursor.fetchone()
        tiempo = time.time() - inicio
        print(f"   Ejecutada en {tiempo:.4f} segundos - {resultado['total']} PDFs disponibles")

        print("\n" + "=" * 60)

    except Error as e:
        print(f"\n❌ Error en consultas masivas: {e}")

    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(connection)


# =============================================
# MENÚ PRINCIPAL
# =============================================

def menu_principal():
    """Menú principal del script"""
    print("\n" + "=" * 60)
    print("  SISTEMA DE POBLACIÓN DE BASE DE DATOS")
    print("  Evaluaciones Médicas de Conductores")
    print("=" * 60)
    print("\n Opciones:")
    print("  1. Poblar base de datos (Bajo: 1.000 registros)")
    print("  2. Poblar base de datos (Recomendado: 5.000 registros)")
    print("  3. Poblar base de datos (Medio: 10.000 registros)")
    print("  4. Poblar base de datos (Alto: 100.000 registros)")
    print("  5. Poblar base de datos (Extremo: 1.000.000 registros)")
    print("  6. Cantidad personalizada")
    print("  7. Verificar datos insertados")
    print("  8. Ejecutar consultas masivas de ejemplo")
    print("  9. Salir")
    print("=" * 60)

    #opcion = input("\n👉 Seleccione una opción (1-9): ")
    opcion = '5'
    
    if opcion == '1':
        poblar_base_datos(num_usuarios=1_000, num_evaluaciones=1_000)
        verificar_datos()
    elif opcion == '2':
        poblar_base_datos(num_usuarios=5_000, num_evaluaciones=5_000)
        verificar_datos()
    elif opcion == '3':
        poblar_base_datos(num_usuarios=10_000, num_evaluaciones=10_000)
        verificar_datos()
    elif opcion == '4':
        poblar_base_datos(num_usuarios=100_000, num_evaluaciones=100_000)
        verificar_datos()
    elif opcion == '5':
        poblar_base_datos(num_usuarios=1_000_000, num_evaluaciones=1_000_000)
        verificar_datos()
    elif opcion == '6':
        try:
            num = int(input("\n📊 Ingrese la cantidad de registros: "))
            poblar_base_datos(num_usuarios=num, num_evaluaciones=num)
            verificar_datos()
        except ValueError:
            print("❌ Cantidad inválida")
    elif opcion == '7':
        verificar_datos()
    elif opcion == '8':
        ejemplos_consultas_masivas()
    elif opcion == '9':
        print("\n👋 ¡Hasta luego!")
        return
    else:
        print("❌ Opción inválida")

    # Preguntar si desea continuar
    #if input("\n¿Desea realizar otra operación? (s/n): ").lower() == 's':
    #    menu_principal()


# =============================================
# EJECUCIÓN DEL SCRIPT
# =============================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   GENERADOR DE DATOS PARA EVALUACIONES MÉDICAS              ║
║   Sistema de Reconocimiento de Conductores                  ║
║   Resolución 000217 de 2014 - ISO/IEC 17024:2012           ║
║                                                              ║
║   IMPORTANTE:                                                ║
║   • Asegúrese de tener la base de datos creada              ║
║   • Configure las credenciales en DB_CONFIG                 ║
║   • Se recomienda comenzar con 1000 registros               ║
║   • Instale dependencias: pip install faker mysql-connector ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()
