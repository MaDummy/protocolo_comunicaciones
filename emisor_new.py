import socket
import json
import sys
import os
import crcmod
from time import sleep
from utils_new import HOST, PORT
from traduccion import leer


crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')

CLAVE = 10



def enviar_paquete(s, secuencia, longitud, fragmento_mensaje, checksum, fin_de_paquete):
    paquete = {
        "secuencia": secuencia,
        "longitud": longitud,
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
        resultado.append((b + CLAVE) % 256)
    return bytes(resultado)

def main():
    # Verifica que el codigo se este ejecutando correctamente
    if len(sys.argv) != 2:
        print("Uso: python emisor_new.py nombre_archivo.ext")
        sys.exit(1)

    ruta_archivo = sys.argv[1]
    extension = os.path.splitext(ruta_archivo)[1].lower().replace('.', '')

    try:
        mensaje = leer(ruta_archivo, extension)
    except Exception as e:
        print(f"Error al leer archivo: {e}")
        sys.exit(1)

    longitud = 8
    mensaje = "El volcan de parangaricutirimicuaro quiere desparangaricutirimicuarizrse. " \
    "Aquel que lo desparangaricutirimicuarice será un buen desparangaricutirimicuarizador."

    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        s_file = s.makefile("r") # archivo de lectura vinculado al socket (para ACK/NACK)

        for i in range(int(len(mensaje) / longitud) + 1):
            secuencia = i
            fragmento_mensaje = mensaje[i*longitud:(i+1)*longitud]
            fragmento_mensaje = cesar_general(fragmento_mensaje)
            checksum = crc16(fragmento_mensaje)  # Por ahora fijo
            fin_de_paquete = "1" if (i+1)*longitud >= len(mensaje) else "0"
            
            # Se envía el paquete y se espera confirmación antes de seguir
            while True:
                enviar_paquete(s, secuencia, longitud, fragmento_mensaje, checksum, fin_de_paquete)

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


            sleep(0.5)

if __name__ == "__main__":
    main()