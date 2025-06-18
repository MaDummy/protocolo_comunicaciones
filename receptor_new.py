import socket
import json
from utils_new import HOST, PORT

mensajeCompleto = []

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
                        print(f"[{paquete['secuencia']}] -> {paquete['mensaje']}, checksum: {paquete['checksum']})")
                        mensajeCompleto.insert(paquete['secuencia'], paquete['mensaje'])

                        if paquete['fin_de_paquete'] == "1":
                            print("listo!\n")
                            for elem in mensajeCompleto:
                                print(elem, end="")
                    except json.JSONDecodeError as e:
                        print(f"Error al decodificar JSON: {e}")

if __name__ == "__main__":
    main()

    