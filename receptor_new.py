import socket
import json
import sys
import os
import crcmod
from utils_new import HOST, PORT
from traduccion import guardar

mensajeCompleto = []

crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')

CLAVE = 10


def decesar_general(data):
    resultado = bytearray()
    for b in data:
        resultado.append((b - CLAVE) % 256)
    return bytes(resultado)

def enviar_confirmacion(conn, secuencia, estado):
    # estado es "ACK" o "NAK"
    confirmacion = json.dumps({
        "tipo": estado,
        "secuencia": secuencia
    }) + "\n" # Salto de linea para delimitar el mensaje
    conn.sendall(confirmacion.encode())

# Envío de un mensaje largo a través de paquetes y reconstrucción del mensaje
def main():
    # Verifica que el codigo se este ejecutando correctamente
    if len(sys.argv) != 2:
        print("Uso: python receptor.py archivo_salida.ext")
        sys.exit(1)

    nombre_destino = sys.argv[1]
    extension = os.path.splitext(nombre_destino)[1].lower().replace(".", "")


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Esperando conexión en {HOST}:{PORT}")
        conn, addr = s.accept()
        with conn:
            print(f"Conectado con {addr}")
            # Creamos una especie de archivo de texto a partir del socket y leemos los paquetes ahi
            with conn.makefile("r") as f:
                for linea in f:
                    if not linea.strip():
                        continue
                    try:
                        paquete = json.loads(linea.strip())
                        print(f"[Seq: {paquete['secuencia']}| Lon: {paquete['longitud']}| CRC: {paquete['checksum']}] -> {paquete['mensaje']}")

                        

                        # Aquí dependiendo de si el checksum es correcto o no, enviamos ACK o NAK
                        if paquete['checksum'] == crc16(paquete['mensaje']):
                            mensajeCompleto.insert(paquete['secuencia'], decesar_general(paquete['mensaje']).decode('utf-8'))
                            enviar_confirmacion(conn, paquete['secuencia'], "ACK")
                        else:
                            enviar_confirmacion(conn, paquete['secuencia'], "NAK")
                        # Se imprime el mensaje completo si se recibió el mensaje final
                        if paquete['fin_de_paquete'] == "1":
                            print("listo!\n")
                            mensaje_total = "".join(mensajeCompleto)
                            guardar(mensaje_total, extension, nombre_destino)
                            print(f"Archivo guardado exitosamente en '{nombre_destino}'")
                            for elem in mensajeCompleto:
                                print(elem, end="")

                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar JSON: {e}")

if __name__ == "__main__":
    main()

    