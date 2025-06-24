#!/usr/bin/env python3
import socket
import json
import sys
import os
import crcmod
from time import sleep
from utils_new import HOST, PORT, leer, CLAVE_CESAR, PROBABILIDAD_ERROR_CHECKSUM, base64, anade_ruido

crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')

def enviar_paquete(s, secuencia, longitud_mensaje, fragmento_mensaje, checksum, fin_de_paquete):
    paquete = {
        "secuencia": secuencia,
        "longitud": longitud_mensaje,
        "mensaje": fragmento_mensaje,
        "checksum": checksum,
        "fin_de_paquete": fin_de_paquete
    }

    # Convertir a JSON y agregar fin de linea para simular un archivo de texto
    json_paquete = json.dumps(paquete) + "\n"
    s.sendall(json_paquete.encode())

def cesar_general(data):
    resultado = bytearray()
    for b in data:
        resultado.append((b + CLAVE_CESAR) % 256)
    return bytes(resultado)

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
            fragmento_base64 = base64.b64encode(fragmento_bytes) # Paso 2: codificar a base64
            fragmento_cifrado = cesar_general(fragmento_base64) # Paso 3: cifrar con César
            checksum = crc16(fragmento_cifrado) # Paso 4: calcular checksum
            fragmento_a_enviar = base64.b64encode(fragmento_cifrado).decode('utf-8') # Paso 5: codificar a base64 para enviar
            fin_de_paquete = "1" if (i+1)*longitud_mensaje >= len(mensaje) else "0"
            
            # Se envía el paquete y se espera confirmación antes de seguir
            while True:
                enviar_paquete(s, secuencia, longitud_mensaje, fragmento_a_enviar, checksum, fin_de_paquete)

                """ VALIDANDO CONFIRMACIÓN """

                # Leer la respuesta del receptor
                respuesta = s_file.readline()

                if not respuesta:
                    print("no se recibió confirmación")
                    break # hay que decidir que hacer en este caso creo..
                try:
                    confirmacion = json.loads(respuesta.strip())
                    print(f"[estado: {confirmacion['tipo']} | secuencia: {confirmacion['secuencia']}]")

                    if confirmacion["tipo"] == "ACK":
                        break  # Se sigue enviando paquetes
                    elif confirmacion["tipo"] == "NAK":
                        print("Reenviando... secuencia:", confirmacion["secuencia"])

                except json.JSONDecodeError as e:
                    print(f"Error al decodificar JSON: {e}")


            
if __name__ == "__main__":
    main()