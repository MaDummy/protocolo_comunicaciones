import socket
from utils_new import HOST, PORT

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

            secuencia, mensaje = modelo.recibir(data)
            mensaje_total += mensaje

    print("Señal recibida: ")
    print(mensaje_total)
modelo.app.graficar_senal_digital(mensaje_total)
print("Señal graficada correctamente.")