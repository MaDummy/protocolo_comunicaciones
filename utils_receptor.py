import json
from random import random
from utils import crc16, base64

def enviar_confirmacion(conn, secuencia, estado):
    """Envia una confirmación al receptor indicando si el paquete fue recibido correctamente o no."""
    estado_encoded = estado.encode('utf-8')
    checksum = crc16(base64.b64encode(estado_encoded))
    confirmacion = json.dumps({
        "tipo": estado, # ACK o NAK
        "secuencia": secuencia,
        "checksum": checksum
    }) + "\n" # Salto de linea para delimitar el mensaje
    conn.sendall(confirmacion.encode())
    print(f"→ Enviado {estado} para secuencia {secuencia}")

def es_paquete_duplicado(secuencia, ultima_secuencia_recibida, paquetes_recibidos):
    """
    Verifica si un paquete es duplicado
    Un paquete es duplicado si ya está almacenado en paquetes_recibidos
    """
    return secuencia in paquetes_recibidos 

def es_secuencia_esperada(secuencia, ultima_secuencia_recibida):
    """
    Verifica si la secuencia recibida es la esperada
    La secuencia esperada es la siguiente a la última recibida correctamente
    """
    return secuencia == ultima_secuencia_recibida + 1

def pierde_paquete(contador, probabilidad):
    """
    Simula la pérdida de un paquete basado en una probabilidad dada.
    Retorna True si el paquete se pierde, False si se recibe correctamente.
    """
    if random() < probabilidad:
        contador += 1
        return True
    return False

