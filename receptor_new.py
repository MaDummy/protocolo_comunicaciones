#!/usr/bin/env python3
import socket
import json
import sys
import os
import crcmod
from utils_new import HOST, PORT, CLAVE_CESAR, guardar, base64

mensajeCompleto = []

crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')


def descrifrar_cesar_general(data):
    """Descrifra un mensaje usando el cifrado César con una clave fija."""
    resultado = bytearray()
    for b in data:
        resultado.append((b - CLAVE_CESAR) % 256)
    return bytes(resultado)

def enviar_confirmacion(conn, secuencia, estado):
    """Envia una confirmación al receptor indicando si el paquete fue recibido correctamente o no."""
    confirmacion = json.dumps({
        "tipo": estado, # ACK o NAK
        "secuencia": secuencia
    }) + "\n" # Salto de linea para delimitar el mensaje
    conn.sendall(confirmacion.encode())

# Envío de un mensaje largo a través de paquetes y reconstrucción del mensaje
def main():
    # Verifica que el codigo se este ejecutando correctamente
    if len(sys.argv) != 2:
        print("Uso: python receptor.py <archivo_salida.ext>")
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
                        mensaje_codificado = base64.b64decode(paquete['mensaje'])
                        if paquete['checksum'] == crc16(mensaje_codificado):
                            mensaje_descifrado = descrifrar_cesar_general(mensaje_codificado)
                            mensajeCompleto.insert(paquete['secuencia'], mensaje_descifrado.decode('utf-8'))
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

    