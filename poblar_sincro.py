"""
Integración del Sistema de Blockchain con la Población de Datos
Script limpio y funcional - Sin duplicaciones
"""

import sys
import time
# Importar sistema blockchain
from blockchain import SistemaBlockchainEvaluaciones

# Importar funciones de la base de datos
try:
    from bd_functions import *
    print("Módulos importados correctamente")
except ImportError as e:
    print(f"Error al importar: {e}")
    print("\nAsegúrate de tener estos archivos en el MISMO directorio:")
    print("   • blockchain.py")
    print("   • bd_functions.py")
    print("   • poblar_sincro.py")
    sys.exit(1)


# =============================================
# FUNCIÓN PRINCIPAL: POBLACIÓN CON BLOCKCHAIN
# =============================================

def poblar_evaluaciones_historicas_con_blockchain(cursor, connection, usuarios_ids, profesionales_ids,
                                                   total_evaluaciones=10000):
    """
    Función que puebla evaluaciones con registro en blockchain
    """
    print(f"\nMODO: Población con Blockchain habilitado")

    # Inicializar blockchain
    sistema_blockchain = SistemaBlockchainEvaluaciones(DB_CONFIG, dificultad=4)

    if not sistema_blockchain.inicializar_sistema():
        print("Error al inicializar blockchain")
        return None

    print("Sistema blockchain inicializado")
    print(f"Nota: Cada evaluación tomará ~0.5 segundos adicionales\n")

    # Distribución por año
    dist_anios = distribuir_evaluaciones_por_anio(total_evaluaciones)

    print(f"\nDistribución por año:")
    for anio, cant in sorted(dist_anios.items()):
        print(f"      {anio}: {cant} evaluaciones")

    evaluaciones_ids = []
    blockchain_registradas = 0
    blockchain_fallidas = 0
    contador_global = 0
    tiempo_inicio = time.time()

    # Iterar por año
    for anio, cantidad_anio in sorted(dist_anios.items()):
        print(f"\nProcesando año {anio}...")

        for i in range(cantidad_anio):
            # Generar fechas
            fecha_eval = generar_fecha_historica(anio, anio)
            fecha_cert = fecha_eval + timedelta(hours=random.randint(1, 24))
            fecha_impresion = fecha_cert + timedelta(hours=random.randint(1, 2))

            # Datos evaluación
            numero_reconocimiento = f"{random.randint(1000, 9999)}"
            id_usuario = random.choice(usuarios_ids)
            id_centro = random.randint(1, 5)
            categoria = random.choice(CATEGORIAS)
            concepto = random.choice(CONCEPTOS)
            fecha_vencimiento = fecha_cert + timedelta(days=365 * random.choice([1, 2, 3, 5]))
            # Generar datos del PDF
            nombre_pdf = f"Informe_{numero_reconocimiento}_{id_usuario}.pdf"
            ruta_pdf = f"/documentos/evaluaciones/{fecha_eval.year}/{fecha_eval.month:02d}/{nombre_pdf}"
            hash_pdf = generar_hash_archivo(f"{numero_reconocimiento}{id_usuario}")

            # Insertar evaluación
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

            values_eval = (
                numero_reconocimiento, id_usuario, id_centro, fecha_eval,
                fecha_cert, fecha_impresion, str(random.randint(1000, 9999)),
                random.choice(TRAMITES), categoria, 'Grupo 1', concepto,
                f"A-{random.randint(1000, 9999)}-{random.randint(100000, 999999)}",
                str(random.randint(10000000, 99999999)),
                fecha_vencimiento, random.choice([12, 24, 36, 60]),
                ruta_pdf, nombre_pdf, hash_pdf, random.randint(150, 500),
                fecha_impresion, 'usuario@sistema.com'
            )

            cursor.execute(query_eval, values_eval)
            id_evaluacion = cursor.lastrowid
            evaluaciones_ids.append(id_evaluacion)

            # Insertar evaluaciones especializadas (funciones importadas)
            insertar_eval_fonoaudiologia(cursor, id_evaluacion, profesionales_ids['Fonoaudiología'], 'usuario@sistema.com')
            insertar_eval_psicologia(cursor, id_evaluacion, profesionales_ids['Psicología'], 'usuario@sistema.com')
            insertar_eval_optometria(cursor, id_evaluacion, profesionales_ids['Optometría'], 'usuario@sistema.com')
            insertar_eval_medicina(cursor, id_evaluacion, profesionales_ids['Medicina General'], 'usuario@sistema.com')

            if concepto == 'APTO CON RESTRICCION':
                insertar_restricciones(cursor, id_evaluacion, 'usuario@sistema.com')

            insertar_concepto_final(cursor, id_evaluacion, profesionales_ids['Medicina General'], fecha_cert, fecha_vencimiento)

            # Registro en blockchain
            try:
                connection.commit()  # CAMBIADO
                exito = sistema_blockchain.registrar_evaluacion(id_evaluacion, 'sistema_poblacion')

                if exito:
                    blockchain_registradas += 1
                else:
                    blockchain_fallidas += 1
            except Exception as e:
                blockchain_fallidas += 1
                print(f"      Error blockchain eval {id_evaluacion}: {e}")

            contador_global += 1

            # Progreso
            if contador_global % 100 == 0:
                tiempo_transcurrido = time.time() - tiempo_inicio
                tiempo_promedio = tiempo_transcurrido / contador_global
                tiempo_restante = tiempo_promedio * (total_evaluaciones - contador_global)

                print(f"      {contador_global}/{total_evaluaciones}")
                print(f"         Blockchain: {blockchain_registradas} OK, {blockchain_fallidas} fail")
                print(f"         Resta: {tiempo_restante/60:.1f} min")

            if contador_global % 50 == 0:
                connection.commit()  # CAMBIADO

    connection.commit()  # CAMBIADO

    # Estadísticas blockchain
    print(f"\n{total_evaluaciones} evaluaciones insertadas")
    print(f"\nESTADÍSTICAS BLOCKCHAIN:")
    print(f"   Registradas: {blockchain_registradas}")
    print(f"   Fallidas: {blockchain_fallidas}")
    print(f"   Éxito: {(blockchain_registradas/total_evaluaciones)*100:.2f}%")

    if sistema_blockchain.blockchain.validar_cadena():
        print(f"   Cadena VÁLIDA ({len(sistema_blockchain.blockchain.cadena)} bloques)")
    else:
        print(f"   Cadena CORRUPTA")

    sistema_blockchain.desconectar()
    return evaluaciones_ids

# =============================================
# MENÚ PRINCIPAL
# =============================================

def menu_principal():
    """Menú interactivo"""
    print("\n" + "="*70)
    print("  POBLACIÓN CON BLOCKCHAIN INTEGRADO")
    print("="*70)
    print("\nusuario='usuario@sistema.com')Blockchain garantiza inmutabilidad")
    print("  Registro automático en cadena de bloques")

    print("\n  Opciones:")
    print("  1. Pequeña CON blockchain    (1,000 usuarios  | 2,000 evaluaciones)")
    print("  2. Mediana CON blockchain    (5,000 usuarios  | 10,000 evaluaciones)")
    print("  3. Grande CON blockchain     (10,000 usuarios | 25,000 evaluaciones)")
    print("  4. Personalizada")
    print("  5. Verificar evaluación existente")
    print("  6. Salir")
    print("="*70)

    #opcion = input("\nSeleccione (1-6): ")
    opcion = '1'

    if opcion == '1':
        ejecutar_poblacion(1000, 2000)
    elif opcion == '2':
        ejecutar_poblacion(5000, 10000)
    elif opcion == '3':
        print("Tomará ~3-4 horas.")
        ejecutar_poblacion(10000, 25000)
    elif opcion == '4':
        try:
            usuarios = int(input("Usuarios: "))
            evaluaciones = int(input("Evaluaciones: "))
            ejecutar_poblacion(usuarios, evaluaciones)
        except ValueError:
            print("Valores inválidos")
    elif opcion == '5':
        verificar_evaluacion()
    elif opcion == '6':
        print("\n¡Hasta luego!")
        return
    else:
        print("Opción inválida")

    #if input("\n¿Otra operación? (s/n): ").lower() == 's':
    #    menu_principal()


def ejecutar_poblacion(num_usuarios, num_evaluaciones):
    """Ejecuta el proceso completo de población"""
    connection = crear_conexion()

    if not connection:
        print("Error de conexión")
        return

    try:
        cursor = connection.cursor()
        usuario_sistema = 'admin@sistemacom'

        print("\n" + "="*70)
        print("🚀 INICIANDO POBLACIÓN CON BLOCKCHAIN")
        print("="*70)
        print(f"\nParámetros:")
        print(f"   • Usuarios: {num_usuarios}")
        print(f"   • Evaluaciones: {num_evaluaciones}")

        # Poblar catálogos
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

        # Poblar evaluaciones con blockchain
        print("\n" + "="*70)
        print("EVALUACIONES + BLOCKCHAIN")
        print("="*70)

        evaluaciones_ids = poblar_evaluaciones_historicas_con_blockchain(
            cursor,
            connection,
            usuarios_ids,
            profesionales_ids,
            num_evaluaciones
        )

        print("\n" + "="*70)
        print("COMPLETADO")
        print("="*70)

        # Verificación aleatoria
        if evaluaciones_ids:
            print("\n" + "="*70)
            print("🔍 VERIFICACIÓN DE PRUEBA")
            print("="*70)

            sistema = SistemaBlockchainEvaluaciones(DB_CONFIG)
            if sistema.inicializar_sistema():
                id_eval = random.choice(evaluaciones_ids)
                print(f"\nVerificando evaluación {id_eval}...")

                resultado = sistema.verificar_integridad_evaluacion(id_eval)

                if resultado.get('valida'):
                    print(f"Verificada correctamente")
                    print(f"   Bloque: {resultado.get('bloque_indice')}")
                    print(f"   Hash: {resultado.get('bloque_hash', '')[:16]}...")
                else:
                    print(f"Error: {resultado.get('mensaje')}")

                sistema.desconectar()

    except KeyboardInterrupt:
        print("\n\nOperación cancelada por usuario")
        connection.rollback()
    except Exception as e:
        print(f"\nError: {e}")
        connection.rollback()
        import traceback
        traceback.print_exc()
    finally:
        if cursor:
            cursor.close()
        cerrar_conexion(connection)


def verificar_evaluacion():
    """Verifica una evaluación existente"""
    try:
        id_eval = int(input("ID evaluación: "))
        sistema = SistemaBlockchainEvaluaciones(DB_CONFIG)
        if sistema.inicializar_sistema():
            resultado = sistema.verificar_integridad_evaluacion(id_eval)
            print("\n" + "="*70)
            print("RESULTADO VERIFICACIÓN")
            print("="*70)
            import json
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
        sistema.desconectar()
    except ValueError:
        print("ID inválido")


# =============================================
# EJECUCIÓN PRINCIPAL
# =============================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   POBLACIÓN CON BLOCKCHAIN INTEGRADO                                 ║
║   Evaluaciones Médicas de Conductores                               ║
║                                                                      ║
║   RCHIVOS REQUERIDOS (mismo directorio):                        ║
║   • blockchain.py                                                   ║
║   • bd_functions.py                                                 ║
║   • poblar_sispro.py (este archivo)                                ║
║                                                                      ║
║   DEPENDENCIAS:                                                   ║
║   pip install faker mysql-connector-python                          ║
║                                                                      ║
║   ⚡ RENDIMIENTO:                                                    ║
║   • Con blockchain: ~1-2 horas (10k evaluaciones)                   ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\nOperación cancelada")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

    print("\nProceso finalizado")