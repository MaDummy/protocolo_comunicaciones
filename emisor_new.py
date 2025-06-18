import socket
import json
from time import sleep

HOST = '127.0.0.1'
PORT = 6969

def main():
    longitud = 8
    mensaje = "El volcan de parangaricutirimicuaro quiere desparangaricutirimicuarizrse. Aquel que lo desparangaricutirimicuarice será un buen desparangaricutirimicuarizador."

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        for i in range(int(len(mensaje) / longitud) + 1):
            secuencia = i
            fragmento_mensaje = mensaje[i*longitud:(i+1)*longitud]
            checksum = 5  # Por ahora fijo
            fin_de_paquete = "1" if (i+1)*longitud >= len(mensaje) else "0"

            paquete = {
                "secuencia": secuencia,
                "mensaje": fragmento_mensaje,
                "checksum": checksum,
                "fin_de_paquete": fin_de_paquete
            }

            # Convertir a JSON y agregar fin de linea para simular un archivo de texto
            json_paquete = json.dumps(paquete) + "\n"
            s.sendall(json_paquete.encode())

            sleep(0.5)

if __name__ == "__main__":
    main()