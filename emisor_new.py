from time import sleep
import socket
from utils_new import HOST, PORT


def main():
    bytes_mensaje = 8
    mensaje = "El volcan de parangaricutirimicuaro quiere desparangaricutirimicuarizrse. Aquel que lo desparangaricutirimicuarice será un buen desparangaricutirimicuarizador."

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        for i in range(int(len(mensaje)/bytes_mensaje)+1):
            fragmento = mensaje[i*bytes_mensaje:(i+1)*bytes_mensaje]
            print(f"Enviando fragmento: {fragmento}")
            s.sendall(fragmento.encode('utf-8'))
            # Simular el envío del fragmento
            sleep(0.5)

        

if __name__ == "__main__":
    main()