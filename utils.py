import numpy as np
import matplotlib.pyplot as plt
import json

# -------------------- Definicion de valores ------------------
HOST = '127.0.0.1'
PORT = 6969

# -------------------- Definición de Funciones --------------------
def dividir_en_chunks(texto, tamano):
    return [texto[i:i+tamano] for i in range(0, len(texto), tamano)]

# -------------------- Definición de Funciones --------------------
class CapaAplicacion:
    def __init__(self):
        self.capa_inferior = None

    def set_inferior(self, capa):
        self.capa_inferior = capa
        capa.set_superior(self)

    def enviar(self, datos):
        paquete = {
            "header": {
                "tipo_mensaje": "bits",
                "longitud": len(datos),
                "encoding": "utf-8",
            },
            "payload": datos
        }
        return self.capa_inferior.enviar(paquete)

    def graficar_senal_digital(self, cadena_binaria, fs=1000, duracion_total=0.2, nombre_archivo="senal_digital_reconstruida.png"):
        senal_binaria = np.array([int(b) for b in cadena_binaria])
        n_muestras = len(senal_binaria)
        tiempo = np.linspace(0, duracion_total, n_muestras)

        plt.figure(figsize=(10, 3))
        plt.step(tiempo, senal_binaria, where='pre', color='blue', label="Señal digital reconstruida")
        plt.title("Señal recibida")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Nivel")
        plt.ylim(-0.2, 1.2)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(nombre_archivo)
        plt.close()

    def generar_y_digitalizar_senal(self, tipo='AC'):
        # Parámetros comunes
        duracion = 0.2  # segundos
        fs = 1000  # frecuencia de muestreo
        tiempo = np.linspace(0, duracion, int(duracion * fs))

        if tipo == 'AC':
            frecuencia = 10  # Hz
            amplitud = 2.5 +(np.random.rand() * 0.6)
            valor_dc = 5.0 +(np.random.rand() * 0.6)
            senal = valor_dc + amplitud * np.sin(2 * np.pi * frecuencia * tiempo)
            descripcion = "AC (senoidal + DC)"
        else:  # tipo == 'DC'
            valor_dc = 5.0
            senal = np.full_like(tiempo, valor_dc)
            descripcion = "DC (constante)"

        # Agregar ruido
        ruido = 0.8 * np.random.randn(len(tiempo))
        senal_con_ruido = senal + ruido

        # Filtro pasa bajas (promedio móvil)
        ventana = 30
        senal_filtrada = np.convolve(senal_con_ruido, np.ones(ventana)/ventana, mode='same')

        # Binarización
        umbral = valor_dc
        senal_binaria = (senal_filtrada > umbral).astype(int)

        # Graficar proceso
        plt.figure(figsize=(12, 8))

        plt.subplot(3, 1, 1)
        plt.plot(tiempo, senal_con_ruido, color="orange", alpha=0.6, label="Señal con ruido")
        plt.plot(tiempo, senal, color="gray", linestyle="dashed", label="Señal ideal")
        plt.title(f"1. Señal {descripcion} con ruido")
        plt.legend()
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(tiempo, senal_filtrada, color="green", label="Filtrada")
        plt.axhline(umbral, color='black', linestyle='--', label="Umbral")
        plt.title("2. Señal filtrada")
        plt.legend()
        plt.grid(True)

        plt.subplot(3, 1, 3)
        plt.step(tiempo, senal_binaria, where='pre', color='blue', label="Binaria")
        plt.title("3. Señal digital (binaria)")
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Nivel")
        plt.legend()
        plt.grid(True)

        plt.tight_layout()
        plt.savefig("señales.png")

        return str(senal_binaria).strip("[]").replace(" ", "").replace("\n", "")


    def recibir(self, paquete):
        print(f"[INFO] Paquete [{self.secuencia}] recibido en Capa Aplicación")
        print(f"Tipo de mensaje: {paquete['header']['tipo_mensaje']}")
        print(f"Longitud: {paquete['header']['longitud']}")
        print(f"Encoding: {paquete['header']['encoding']}")
        print(f"Datos: {paquete['payload']}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.datos_finales = paquete["payload"]
        self.secuencia = None  # Se setea desde Transporte
        return

class CapaTransporte:
    def __init__(self):
        self.capa_inferior = None
        self.capa_superior = None
        self.contador_secuencia = 1
        self.puerto_origen = PORT

    def set_inferior(self, capa):
        self.capa_inferior = capa
        capa.set_superior(self)

    def set_superior(self, capa):
        self.capa_superior = capa

    def enviar(self, datos, puerto_destino=PORT):
        paquete = {
            "header": {
                "puerto_origen": self.puerto_origen,
                "puerto_destino": puerto_destino,
                "protocolo": "TCP",
                "numero_secuencia": self.contador_secuencia,
            },
            "payload": datos
        }
        self.contador_secuencia += 1
        return self.capa_inferior.enviar(paquete)

    def recibir(self, paquete):
        print("[INFO] Paquete recibido en Capa Transporte")
        print(f"Puerto origen: {paquete['header']['puerto_origen']}")
        print(f"Puerto destino: {paquete['header']['puerto_destino']}")
        print(f"Protocolo: {paquete['header']['protocolo']}")
        print(f"Numero de secuencia: {paquete['header']['numero_secuencia']}")
        self.capa_superior.secuencia = paquete["header"]["numero_secuencia"]
        self.capa_superior.recibir(paquete["payload"])

class CapaRed:
    def __init__(self):
        self.capa_inferior = None
        self.capa_superior = None
        self.ip_origen = HOST

    def set_inferior(self, capa):
        self.capa_inferior = capa
        capa.set_superior(self)

    def set_superior(self, capa):
        self.capa_superior = capa

    def enviar(self, datos, ip_destino=HOST):
        paquete = {
            "header": {
                "ip_origen": self.ip_origen,
                "ip_destino": ip_destino,
                "protocolo": "IPv4",
            },
            "payload": datos
        }
        return self.capa_inferior.enviar(paquete)

    def recibir(self, paquete):
        print("[INFO] Paquete recibido en Capa Red")
        print(f"IP origen: {paquete['header']['ip_origen']}")
        print(f"IP destino: {paquete['header']['ip_destino']}")
        print(f"Protocolo: {paquete['header']['protocolo']}")
        self.capa_superior.recibir(paquete["payload"])

class CapaEnlace:
    def __init__(self, mac_origen="00:00:00:00:00:01"):
        self.capa_superior = None
        self.mac_origen = mac_origen

    def set_superior(self, capa):
        self.capa_superior = capa

    def enviar(self, datos, mac_destino="00:00:00:00:00:01"):
        paquete = {
            "header": {
                "mac_origen": self.mac_origen,
                "mac_destino": mac_destino,
            },
            "payload": datos
        }
        return json.dumps(paquete).encode()

    def recibir(self, paquete_bytes):
        paquete = json.loads(paquete_bytes.decode())
        print("[INFO] Paquete recibido en Capa Enlace")
        print(f"MAC origen: {paquete['header']['mac_origen']}")
        print(f"MAC destino: {paquete['header']['mac_destino']}")
        self.capa_superior.recibir(paquete["payload"])

class Modelo:
    def __init__(self):
        self.enlace = CapaEnlace()
        self.red = CapaRed()
        self.trans = CapaTransporte()
        self.app = CapaAplicacion()

        self.app.set_inferior(self.trans)
        self.trans.set_inferior(self.red)
        self.red.set_inferior(self.enlace)

    def empaquetar(self, mensaje):
        return self.app.enviar(mensaje)

    def recibir(self, paquete_bytes):
        self.enlace.recibir(paquete_bytes)
        return self.app.secuencia, self.app.datos_finales
