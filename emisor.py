#!/usr/bin/env python3
import socket
import sys
import os
from time import sleep
from utils import HOST, PORT, leer, base64, cesar_general, crc16
from utils_emisor import MAX_REINTENTOS, enviar_paquete, esperar_confirmacion_con_timeout

def main():
    # Verifica que el codigo se este ejecutando correctamente
    if len(sys.argv) != 2:
        print("Uso: python emisor_new.py <nombre_archivo.ext>")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    extension = os.path.splitext(ruta_archivo)[1].lower().replace('.', '')

    try:
        mensaje = leer(ruta_archivo, extension)
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        sys.exit(1)

    longitud_mensaje = 8
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        s_file = s.makefile("r") # archivo de lectura vinculado al socket (para ACK/NACK)

        for i in range(int(len(mensaje) / longitud_mensaje) + 1):
            secuencia = i
            fragmento_bytes = mensaje[i*longitud_mensaje:(i+1)*longitud_mensaje].encode('utf-8') # Paso 1: convertir a bytes
            
            # Saltar fragmentos vacíos
            if not fragmento_bytes:
                continue
                
            fragmento_base64 = base64.b64encode(fragmento_bytes) # Paso 2: codificar a base64
            fragmento_cifrado = cesar_general(fragmento_base64) # Paso 3: cifrar con César
            checksum = crc16(fragmento_cifrado) # Paso 4: calcular checksum
            fragmento_a_enviar = base64.b64encode(fragmento_cifrado).decode('utf-8') # Paso 5: codificar a base64 para enviar
            fin_de_paquete = "1" if (i+1)*longitud_mensaje >= len(mensaje) else "0"
            
            # Intentar enviar el paquete con reintentos
            reintentos = 0
            enviado_exitosamente = False
            
            while reintentos < MAX_REINTENTOS and not enviado_exitosamente:
                try:
                    enviar_paquete(s, secuencia, longitud_mensaje, fragmento_a_enviar, checksum, fin_de_paquete)
                    
                    # Esperar confirmación con timeout
                    ack_recibido, confirmacion = esperar_confirmacion_con_timeout(s, s_file, secuencia)
                    
                    if ack_recibido:
                        print(f"Paquete {secuencia} enviado exitosamente")
                        enviado_exitosamente = True
                    else:
                        reintentos += 1
                        if reintentos < MAX_REINTENTOS:
                            print(f"Reintento {reintentos}/{MAX_REINTENTOS} para secuencia {secuencia}")
                        else:
                            print(f"Se agotaron los reintentos para secuencia {secuencia}")
                            
                except Exception as e:
                    print(f"Error enviando paquete {secuencia}: {e}")
                    reintentos += 1
            
            if not enviado_exitosamente:
                print(f"Falló el envío del paquete {secuencia} después de {MAX_REINTENTOS} intentos")
                break

        print("Transmisión completada :3")

if __name__ == "__main__":
    main()