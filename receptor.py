import socket
from utils_new import HOST, PORT
import json

modelo = Modelo()

mensaje_total = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Esperando conexión en {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        print(f"Conectado con {addr}")
        while True:
            data = conn.recv(4096)
            if not data:
                break
            data = data.decode('utf-8')
            paquete = json.loads(data.decode())
            print(f"mensaje recibido: {paquete["mensaje"]}")

    print("Señal recibida: ")
    print(mensaje_total)
modelo.app.graficar_senal_digital(mensaje_total)
print("Señal graficada correctamente.")