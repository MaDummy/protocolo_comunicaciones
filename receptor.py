#!/usr/bin/env python3
import socket
import json
import sys
import os

from utils import HOST, PORT, PROBABILIDAD_ERROR_CHECKSUM, crc16, guardar, base64, cesar_general
from utils_receptor import enviar_confirmacion, es_paquete_duplicado, es_secuencia_esperada, pierde_paquete, anade_ruido

# Diccionario para almacenar mensajes recibidos (manejo de duplicados)
mensajeCompleto = {}
paquetes_perdidos = 0

def procesar_paquete(paquete, conn, ultima_secuencia_recibida, paquetes_recibidos, contador_errores_checksum):
    """
    Procesa un paquete recibido y maneja duplicados
    Retorna: (nueva_ultima_secuencia, nuevo_contador_errores, paquete_final_recibido)
    """
    secuencia = paquete['secuencia']
    
    print(f"← Recibido paquete [Seq: {secuencia}| Lon: {paquete['longitud']}| CRC: {paquete['checksum']}]")
    
    # Verificar si es un paquete duplicado
    if es_paquete_duplicado(secuencia, ultima_secuencia_recibida, paquetes_recibidos):
        print(f"Paquete duplicado detectado (secuencia {secuencia}) - Enviando ACK nuevamente")
        enviar_confirmacion(conn, secuencia, "ACK")
        return ultima_secuencia_recibida, contador_errores_checksum, False
    
    # Verificar si es la secuencia esperada
    if not es_secuencia_esperada(secuencia, ultima_secuencia_recibida):
        print(f"⚠️  Secuencia fuera de orden. Esperada: {ultima_secuencia_recibida + 1}, Recibida: {secuencia}")
        # Enviar NAK para la secuencia esperada
        enviar_confirmacion(conn, ultima_secuencia_recibida + 1, "NAK")
        return ultima_secuencia_recibida, contador_errores_checksum, False
    
    # Validar checksum
    try:
        mensaje_codificado = base64.b64decode(paquete['mensaje'])
        valor_checksum = anade_ruido(paquete['checksum'], PROBABILIDAD_ERROR_CHECKSUM)
        
        if valor_checksum == crc16(mensaje_codificado):
            # Checksum correcto - procesar mensaje
            mensaje_descifrado = cesar_general(mensaje_codificado, False)
            mensaje_descifrado = base64.b64decode(mensaje_descifrado)
            
            # Almacenar el fragmento del mensaje
            paquetes_recibidos[secuencia] = mensaje_descifrado.decode('utf-8')
            mensajeCompleto[secuencia] = mensaje_descifrado.decode('utf-8')
            
            print(f"Paquete {secuencia} procesado correctamente")
            enviar_confirmacion(conn, secuencia, "ACK")
            
            # Actualizar la última secuencia recibida
            nueva_ultima_secuencia = secuencia
            
            # Verificar si es el paquete final
            es_paquete_final = paquete['fin_de_paquete'] == "1"
            
            return nueva_ultima_secuencia, contador_errores_checksum, es_paquete_final
            
        else:
            # Checksum incorrecto
            print(f"Error de checksum en paquete {secuencia}")
            enviar_confirmacion(conn, secuencia, "NAK")
            return ultima_secuencia_recibida, contador_errores_checksum + 1, False
            
    except Exception as e:
        print(f"Error procesando paquete {secuencia}: {e}")
        enviar_confirmacion(conn, secuencia, "NAK")
        return ultima_secuencia_recibida, contador_errores_checksum + 1, False


def reconstruir_mensaje_completo():
    """
    Reconstruye el mensaje completo a partir de los fragmentos ordenados
    """
    if not mensajeCompleto:
        return ""
    
    # Ordenar por secuencia y concatenar
    secuencias_ordenadas = sorted(mensajeCompleto.keys())
    mensaje_total = ""
    
    for secuencia in secuencias_ordenadas:
        mensaje_total += mensajeCompleto[secuencia]
    
    return mensaje_total


# Envío de un mensaje largo a través de paquetes y reconstrucción del mensaje
def main():
    # Verifica que el codigo se este ejecutando correctamente
    if len(sys.argv) != 3:
        print("Uso: python receptor.py <archivo_salida.ext> <mostrar texto: 0|1>")
        sys.exit(1)

    nombre_destino = sys.argv[1]
    extension = os.path.splitext(nombre_destino)[1].lower().replace(".", "")
    mostrar_en_consola = int(sys.argv[2])

    # Variables para manejo de secuencias y duplicados
    ultima_secuencia_recibida = -1  # Última secuencia recibida correctamente
    paquetes_recibidos = {}  # Diccionario para detectar duplicados
    contador_errores_checksum = 0

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"🔗 Esperando conexión en {HOST}:{PORT}")
        conn, addr = s.accept()
        
        with conn:
            print(f"Conectado con {addr}")
            
            # Creamos una especie de archivo de texto a partir del socket y leemos los paquetes ahi
            with conn.makefile("r") as f:
                paquete_final_recibido = False
                
                for linea in f:
                    if not linea.strip():
                        continue
                        
                    try:
                        paquete = json.loads(linea.strip()) if not pierde_paquete(paquetes_perdidos, 0.1) else {} # Probabilidad de perder el paquete
                        
                        # Procesar el paquete
                        ultima_secuencia_recibida, contador_errores_checksum, es_final = procesar_paquete(
                            paquete, conn, ultima_secuencia_recibida, 
                            paquetes_recibidos, contador_errores_checksum
                        )
                        
                        # Si es el paquete final, terminar la recepción
                        if es_final:
                            paquete_final_recibido = True
                            print("Recepción completada!")
                            break
                            
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar JSON: {e}")
                        continue
                    except Exception as e:
                        print(f"Error procesando línea: {e}")
                        continue
                
                # Reconstruir y guardar el mensaje completo
                if paquete_final_recibido:
                    mensaje_total = reconstruir_mensaje_completo()
                    
                    if mensaje_total:
                        try:
                            guardar(mensaje_total, extension, nombre_destino)
                            print(f"Archivo guardado exitosamente en '{nombre_destino}'")
                            
                            if mostrar_en_consola == 1:
                                print("Contenido del archivo:")
                                print("-" * 50)
                                print(mensaje_total)
                                print("-" * 50)
                                
                        except Exception as e:
                            print(f"❌ Error guardando archivo: {e}")
                    else:
                        print("No se pudo reconstruir el mensaje completo")
                
                print(f"Paquetes recibidos correctamente: {len(paquetes_recibidos)}")
                print(f"Errores de checksum: {contador_errores_checksum}")
                print(f"Última secuencia procesada: {ultima_secuencia_recibida}")

if __name__ == "__main__":
    main()