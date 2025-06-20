import socket
import json
from utils_new import HOST, PORT

mensajeCompleto = []

def enviar_confirmacion(conn, secuencia, estado):
    # estado es "ACK" o "NAK"
    confirmacion = json.dumps({
        "tipo": estado,
        "secuencia": secuencia
    }) + "\n" # Salto de linea para delimitar el mensaje
    conn.sendall(confirmacion.encode())

# Envío de un mensaje largo a través de paquetes y reconstrucción del mensaje
def main():
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

                        mensajeCompleto.insert(paquete['secuencia'], paquete['mensaje'])

                        # Aquí dependiendo de si el checksum es correcto o no, enviamos ACK o NAK
                        if paquete['checksum'] == 5:
                            enviar_confirmacion(conn, paquete['secuencia'], "ACK")
                        else:
                            enviar_confirmacion(conn, paquete['secuencia'], "NAK")
                        # Se imprime el mensaje completo si se recibió el mensaje final
                        if paquete['fin_de_paquete'] == "1":
                            print("listo!\n")
                            for elem in mensajeCompleto:
                                print(elem, end="")

                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar JSON: {e}")

if __name__ == "__main__":
    main()

    