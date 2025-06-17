import time
import socket
from utils import Modelo, HOST, PORT, dividir_en_chunks

if __name__ == "__main__":
    modelo = Modelo()
    tipo_senal = input("¿Qué tipo de señal deseas usar? (AC/DC): ").strip().upper()
    if tipo_senal not in ["AC", "DC"]:
        print("Tipo inválido. Usando AC por defecto.")
        tipo_senal = "AC"

    datos_binarios = modelo.app.generar_y_digitalizar_senal(tipo=tipo_senal)

    print("\n[RESULTADO BINARIO] Primeros 100 bits de la señal digital:")
    print("".join(str(bit) for bit in datos_binarios[:100]))

    print(f"\n[INFO] Total de bits generados: {len(datos_binarios)}")

    # Aplicación de la arquitectura de 4 capas
    modelo = Modelo()

    chunks = dividir_en_chunks(datos_binarios, 8)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Conectado al receptor")

        for i, chunk in enumerate(chunks):
            paquete = modelo.empaquetar(chunk)
            s.sendall(paquete)
            print(f"Enviado paquete {i+1}: {chunk}")
            time.sleep(0.01) # Para evitar JSONDecodeError (más de un paquete siendo enviado a la vez)