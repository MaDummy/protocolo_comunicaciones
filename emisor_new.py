from time import sleep
import socket
import json

from utils_new import HOST, PORT


def main():
    longitud = 8
    mensaje = "El volcan de parangaricutirimicuaro quiere desparangaricutirimicuarizrse. Aquel que lo desparangaricutirimicuarice será un buen desparangaricutirimicuarizador."

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        for i in range(int(len(mensaje)/longitud)+1):
            secuencia = i + 1 # Secuencia inicia en 1
            fragmento_mensaje = mensaje[i*longitud:(i+1)*longitud]
            checksum = 5 # Implementar
            fin_de_paquete = "1" if (i+1)*longitud >= len(mensaje) else "0"

            # Empaquetar el fragmento
            paquete = {
                "secuencia": secuencia,
                "mensaje": fragmento_mensaje,
                "checksum": checksum,
                "fin_de_paquete": fin_de_paquete
            }
            json.dumps(paquete).encode()
            s.sendall(paquete)
            # Simular el envío del fragmento
            sleep(0.5)

        

if __name__ == "__main__":
    main()