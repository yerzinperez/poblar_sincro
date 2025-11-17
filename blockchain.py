"""
Sistema de Blockchain para Garantizar Integridad de Evaluaciones Médicas
Implementación de cadena de bloques para registros inmutables
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import mysql.connector
from mysql.connector import Error

# =============================================
# CLASE BLOQUE
# =============================================

class Bloque:
    """
    Representa un bloque en la cadena de blockchain
    """
    def __init__(self, indice: int, timestamp: float, datos: Dict, 
                 hash_anterior: str, nonce: int = 0):
        self.indice = indice
        self.timestamp = timestamp
        self.datos = datos
        self.hash_anterior = hash_anterior
        self.nonce = nonce
        self.hash = self.calcular_hash()
    
    def calcular_hash(self) -> str:
        """
        Calcula el hash SHA-256 del bloque
        """
        contenido_bloque = json.dumps({
            'indice': self.indice,
            'timestamp': self.timestamp,
            'datos': self.datos,
            'hash_anterior': self.hash_anterior,
            'nonce': self.nonce
        }, sort_keys=True, default=str)
        
        return hashlib.sha256(contenido_bloque.encode()).hexdigest()
    
    def minar_bloque(self, dificultad: int = 4):
        """
        Prueba de trabajo (Proof of Work)
        Encuentra un nonce que genere un hash con N ceros al inicio
        """
        objetivo = '0' * dificultad
        
        while self.hash[:dificultad] != objetivo:
            self.nonce += 1
            self.hash = self.calcular_hash()
        
        print(f"Bloque minado: {self.hash}")
    
    def to_dict(self) -> Dict:
        """Convierte el bloque a diccionario"""
        return {
            'indice': self.indice,
            'timestamp': self.timestamp,
            'datos': self.datos,
            'hash_anterior': self.hash_anterior,
            'nonce': self.nonce,
            'hash': self.hash
        }

# =============================================
# CLASE BLOCKCHAIN
# =============================================

class BlockchainEvaluaciones:
    """
    Cadena de bloques para registros de evaluaciones médicas
    """
    def __init__(self, dificultad: int = 4):
        self.cadena: List[Bloque] = []
        self.dificultad = dificultad
        self.crear_bloque_genesis()
    
    def crear_bloque_genesis(self):
        """
        Crea el primer bloque de la cadena (Bloque Génesis)
        """
        bloque_genesis = Bloque(
            indice=0,
            timestamp=time.time(),
            datos={
                'tipo': 'GENESIS',
                'mensaje': 'Bloque Génesis - Sistema de Evaluaciones Médicas',
                'fecha_creacion': datetime.now().isoformat()
            },
            hash_anterior='0'
        )
        bloque_genesis.minar_bloque(self.dificultad)
        self.cadena.append(bloque_genesis)
        print(f"Bloque Génesis creado: {bloque_genesis.hash}")
    
    def obtener_ultimo_bloque(self) -> Bloque:
        """Retorna el último bloque de la cadena"""
        return self.cadena[-1]
    
    def agregar_bloque(self, datos: Dict) -> Bloque:
        """
        Agrega un nuevo bloque a la cadena
        """
        ultimo_bloque = self.obtener_ultimo_bloque()
        
        nuevo_bloque = Bloque(
            indice=ultimo_bloque.indice + 1,
            timestamp=time.time(),
            datos=datos,
            hash_anterior=ultimo_bloque.hash
        )
        
        nuevo_bloque.minar_bloque(self.dificultad)
        self.cadena.append(nuevo_bloque)
        
        return nuevo_bloque
    
    def validar_cadena(self) -> bool:
        """
        Valida toda la cadena de bloques
        Verifica:
        1. Hash de cada bloque es correcto
        2. Hash anterior coincide con el bloque previo
        3. Prueba de trabajo es válida
        """
        for i in range(1, len(self.cadena)):
            bloque_actual = self.cadena[i]
            bloque_anterior = self.cadena[i - 1]
            
            # Verificar hash del bloque
            if bloque_actual.hash != bloque_actual.calcular_hash():
                print(f"Hash inválido en bloque {i}")
                return False
            
            # Verificar enlace con bloque anterior
            if bloque_actual.hash_anterior != bloque_anterior.hash:
                print(f"Cadena rota en bloque {i}")
                return False
            
            # Verificar prueba de trabajo
            if not bloque_actual.hash.startswith('0' * self.dificultad):
                print(f"Prueba de trabajo inválida en bloque {i}")
                return False
        
        return True
    
    def obtener_bloque_por_hash(self, hash_buscado: str) -> Optional[Bloque]:
        """Busca un bloque específico por su hash"""
        for bloque in self.cadena:
            if bloque.hash == hash_buscado:
                return bloque
        return None
    
    def obtener_bloques_por_evaluacion(self, id_evaluacion: int) -> List[Bloque]:
        """Obtiene todos los bloques relacionados a una evaluación"""
        bloques = []
        for bloque in self.cadena:
            if bloque.datos.get('id_evaluacion') == id_evaluacion:
                bloques.append(bloque)
        return bloques

# =============================================
# FUNCIONES DE INTEGRACIÓN CON BD
# =============================================

def guardar_bloque_en_bd(cursor, bloque: Bloque) -> int:
    """
    Guarda un bloque en la base de datos
    """
    query = """
    INSERT INTO blockchain_bloques 
    (indice, timestamp, hash, hash_anterior, nonce, datos_json)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    datos_json = json.dumps(bloque.datos, default=str)
    
    cursor.execute(query, (
        bloque.indice,
        bloque.timestamp,
        bloque.hash,
        bloque.hash_anterior,
        bloque.nonce,
        datos_json
    ))
    
    return cursor.lastrowid

def registrar_evaluacion_en_blockchain(cursor, id_evaluacion: int, 
                                      bloque: Bloque, hash_datos: str):
    """
    Registra la relación entre evaluación y bloque
    """
    query = """
    INSERT INTO blockchain_evaluaciones 
    (id_evaluacion, id_bloque, hash_bloque, hash_datos)
    VALUES (%s, %s, %s, %s)
    """
    
    # Obtener id_bloque
    cursor.execute(
        "SELECT id_bloque FROM blockchain_bloques WHERE hash = %s",
        (bloque.hash,)
    )
    id_bloque = cursor.fetchone()[0]
    
    cursor.execute(query, (id_evaluacion, id_bloque, bloque.hash, hash_datos))

def registrar_auditoria(cursor, id_evaluacion: int, tipo_operacion: str,
                       hash_bloque: str = None, es_valida: bool = True,
                       detalles: str = None, usuario: str = None):
    """
    Registra operaciones en auditoría
    """
    query = """
    INSERT INTO blockchain_auditoria 
    (id_evaluacion, tipo_operacion, hash_bloque, es_valida, detalles, usuario)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    cursor.execute(query, (
        id_evaluacion, tipo_operacion, hash_bloque, 
        es_valida, detalles, usuario
    ))

def calcular_hash_evaluacion(cursor, id_evaluacion: int) -> str:
    """
    Calcula el hash de todos los datos de una evaluación
    Incluye: evaluacion principal + evaluaciones especializadas
    """
    # Obtener datos de evaluación principal
    cursor.execute("SELECT * FROM evaluaciones WHERE id_evaluacion = %s", (id_evaluacion,))
    eval_principal = cursor.fetchone()
    
    if not eval_principal:
        return None
    
    # Obtener evaluaciones especializadas
    cursor.execute("SELECT * FROM eval_fonoaudiologia WHERE id_evaluacion = %s", (id_evaluacion,))
    eval_fono = cursor.fetchone()
    
    cursor.execute("SELECT * FROM eval_psicologia WHERE id_evaluacion = %s", (id_evaluacion,))
    eval_psico = cursor.fetchone()
    
    cursor.execute("SELECT * FROM eval_optometria WHERE id_evaluacion = %s", (id_evaluacion,))
    eval_opto = cursor.fetchone()
    
    cursor.execute("SELECT * FROM eval_medicina_general WHERE id_evaluacion = %s", (id_evaluacion,))
    eval_med = cursor.fetchone()
    
    # Crear estructura de datos
    datos_completos = {
        'evaluacion_principal': list(eval_principal) if eval_principal else None,
        'fonoaudiologia': list(eval_fono) if eval_fono else None,
        'psicologia': list(eval_psico) if eval_psico else None,
        'optometria': list(eval_opto) if eval_opto else None,
        'medicina': list(eval_med) if eval_med else None
    }
    
    # Calcular hash
    datos_json = json.dumps(datos_completos, sort_keys=True, default=str)
    return hashlib.sha256(datos_json.encode()).hexdigest()

# =============================================
# CLASE PRINCIPAL DEL SISTEMA
# =============================================

class SistemaBlockchainEvaluaciones:
    """
    Sistema completo de blockchain integrado con la base de datos
    """
    def __init__(self, db_config: Dict, dificultad: int = 4):
        self.db_config = db_config
        self.blockchain = BlockchainEvaluaciones(dificultad=dificultad)
        self.connection = None
        self.cursor = None
    
    def conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("Conectado a la base de datos")
            return True
        except Error as e:
            print(f"Error de conexión: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Desconectado de la base de datos")
    
    def inicializar_sistema(self):
        """Inicializa el sistema de blockchain"""
        if not self.conectar():
            return False
        
        # Cargar blockchain existente de la BD
        self.cargar_blockchain_desde_bd()
        
        return True
    
    def cargar_blockchain_desde_bd(self):
        """Carga la blockchain desde la base de datos"""
        query = """
        SELECT indice, timestamp, hash, hash_anterior, nonce, datos_json
        FROM blockchain_bloques
        ORDER BY indice
        """
        
        self.cursor.execute(query)
        bloques = self.cursor.fetchall()
        
        if not bloques:
            print("No hay blockchain previa, se creará nueva")
            return
        
        # Si hay bloques, reconstruir la cadena
        self.blockchain.cadena = []
        
        for row in bloques:
            indice, timestamp, hash_bloque, hash_anterior, nonce, datos_json = row
            datos = json.loads(datos_json)
            
            bloque = Bloque(indice, timestamp, datos, hash_anterior, nonce)
            bloque.hash = hash_bloque  # Usar hash almacenado
            
            self.blockchain.cadena.append(bloque)
        
        print(f"Blockchain cargada: {len(self.blockchain.cadena)} bloques")
        
        # Validar integridad
        if self.blockchain.validar_cadena():
            print("Blockchain válida")
        else:
            print("ADVERTENCIA: Blockchain corrupta")
    
    def registrar_evaluacion(self, id_evaluacion: int, usuario: str = 'sistema') -> bool:
        """
        Registra una evaluación en el blockchain
        Este método se llama DESPUÉS de insertar la evaluación en la BD
        """
        try:
            self.connection.commit()
        except Exception as e:
            print(f"Advertencia al hacer commit: {e}")

        print(f"\nRegistrando evaluación {id_evaluacion} en blockchain...")
        
        # Calcular hash de los datos de la evaluación
        hash_datos = calcular_hash_evaluacion(self.cursor, id_evaluacion)
        
        if not hash_datos:
            print(f"No se encontró la evaluación {id_evaluacion}")
            return False
        
        # Obtener datos de la evaluación
        self.cursor.execute("""
            SELECT e.numero_reconocimiento, e.fecha_evaluacion,
                   u.numero_identificacion, u.nombres, u.apellidos,
                   e.concepto_final
            FROM evaluaciones e
            JOIN usuarios u ON e.id_usuario = u.id_usuario
            WHERE e.id_evaluacion = %s
        """, (id_evaluacion,))
        
        datos_eval = self.cursor.fetchone()
        
        if not datos_eval:
            return False
        
        # Crear datos del bloque
        datos_bloque = {
            'tipo': 'EVALUACION_MEDICA',
            'id_evaluacion': id_evaluacion,
            'numero_reconocimiento': datos_eval[0],
            'fecha_evaluacion': str(datos_eval[1]),
            'paciente': {
                'identificacion': datos_eval[2],
                'nombres': datos_eval[3],
                'apellidos': datos_eval[4]
            },
            'concepto': datos_eval[5],
            'hash_datos': hash_datos,
            'timestamp_registro': datetime.now().isoformat(),
            'registrado_por': usuario
        }
        
        # Agregar bloque a la cadena
        nuevo_bloque = self.blockchain.agregar_bloque(datos_bloque)
        
        # Guardar en BD
        guardar_bloque_en_bd(self.cursor, nuevo_bloque)
        registrar_evaluacion_en_blockchain(
            self.cursor, id_evaluacion, nuevo_bloque, hash_datos
        )
        registrar_auditoria(
            self.cursor, id_evaluacion, 'CREACION', 
            nuevo_bloque.hash, True, 
            f'Evaluación registrada en bloque {nuevo_bloque.indice}',
            usuario
        )
        
        self.connection.commit()
        
        print(f"Evaluación {id_evaluacion} registrada en bloque {nuevo_bloque.indice}")
        print(f"   Hash del bloque: {nuevo_bloque.hash}")
        print(f"   Hash de datos: {hash_datos}")
        
        return True
    
    def verificar_integridad_evaluacion(self, id_evaluacion: int, 
                                       usuario: str = 'sistema') -> Dict:
        """
        Verifica si una evaluación ha sido modificada después de su registro
        """
        print(f"\n🔍 Verificando integridad de evaluación {id_evaluacion}...")
        
        # Obtener registro blockchain de la evaluación
        query = """
        SELECT hash_bloque, hash_datos
        FROM blockchain_evaluaciones
        WHERE id_evaluacion = %s
        ORDER BY timestamp_registro DESC
        LIMIT 1
        """
        
        self.cursor.execute(query, (id_evaluacion,))
        registro = self.cursor.fetchone()
        
        if not registro:
            resultado = {
                'evaluacion_id': id_evaluacion,
                'registrada': False,
                'valida': False,
                'mensaje': 'Evaluación no registrada en blockchain'
            }
            registrar_auditoria(
                self.cursor, id_evaluacion, 'VALIDACION',
                None, False, resultado['mensaje'], usuario
            )
            self.connection.commit()
            return resultado
        
        hash_bloque_registrado, hash_datos_registrado = registro
        
        # Calcular hash actual de los datos
        hash_datos_actual = calcular_hash_evaluacion(self.cursor, id_evaluacion)
        
        # Verificar bloque en la cadena
        bloque = self.blockchain.obtener_bloque_por_hash(hash_bloque_registrado)
        
        if not bloque:
            resultado = {
                'evaluacion_id': id_evaluacion,
                'registrada': True,
                'valida': False,
                'mensaje': 'Bloque no encontrado en la cadena',
                'hash_registrado': hash_bloque_registrado
            }
        elif hash_datos_actual != hash_datos_registrado:
            resultado = {
                'evaluacion_id': id_evaluacion,
                'registrada': True,
                'valida': False,
                'mensaje': 'DATOS MODIFICADOS: Los datos actuales no coinciden con el registro blockchain',
                'hash_original': hash_datos_registrado,
                'hash_actual': hash_datos_actual,
                'bloque_indice': bloque.indice,
                'bloque_hash': bloque.hash,
                'timestamp_registro': datetime.fromtimestamp(bloque.timestamp).isoformat()
            }
            registrar_auditoria(
                self.cursor, id_evaluacion, 'INTENTO_MODIFICACION',
                hash_bloque_registrado, False,
                f'Hash original: {hash_datos_registrado}, Hash actual: {hash_datos_actual}',
                usuario
            )
        else:
            # Validar toda la cadena
            cadena_valida = self.blockchain.validar_cadena()
            
            resultado = {
                'evaluacion_id': id_evaluacion,
                'registrada': True,
                'valida': True and cadena_valida,
                'mensaje': 'Datos íntegros y sin modificaciones',
                'hash_datos': hash_datos_actual,
                'bloque_indice': bloque.indice,
                'bloque_hash': bloque.hash,
                'timestamp_registro': datetime.fromtimestamp(bloque.timestamp).isoformat(),
                'cadena_blockchain_valida': cadena_valida
            }
            registrar_auditoria(
                self.cursor, id_evaluacion, 'VALIDACION',
                hash_bloque_registrado, True,
                'Verificación exitosa', usuario
            )
        
        self.connection.commit()
        return resultado
    
    def obtener_certificado_integridad(self, id_evaluacion: int) -> Dict:
        """
        Genera un certificado de integridad para la evaluación
        """
        verificacion = self.verificar_integridad_evaluacion(id_evaluacion)
        
        if not verificacion['valida']:
            return verificacion
        
        # Obtener datos adicionales
        self.cursor.execute("""
            SELECT bb.indice, bb.hash, bb.hash_anterior, bb.timestamp,
                   be.timestamp_registro
            FROM blockchain_evaluaciones be
            JOIN blockchain_bloques bb ON be.hash_bloque = bb.hash
            WHERE be.id_evaluacion = %s
            ORDER BY be.timestamp_registro DESC
            LIMIT 1
        """, (id_evaluacion,))
        
        bloque_info = self.cursor.fetchone()
        
        certificado = {
            'evaluacion_id': id_evaluacion,
            'valida': True,
            'certificado': {
                'mensaje': 'Este documento certifica que la evaluación médica no ha sido alterada desde su registro',
                'bloque_indice': bloque_info[0],
                'hash_bloque': bloque_info[1],
                'hash_bloque_anterior': bloque_info[2],
                'fecha_registro_blockchain': datetime.fromtimestamp(bloque_info[3]).isoformat(),
                'fecha_certificacion': datetime.now().isoformat(),
                'cadena_bloques_valida': self.blockchain.validar_cadena(),
                'total_bloques_cadena': len(self.blockchain.cadena)
            },
            'verificacion_url': f'/api/verificar/{id_evaluacion}/{bloque_info[1]}'
        }
        
        return certificado