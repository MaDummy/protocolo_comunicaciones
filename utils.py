import base64
import random


HOST = '127.0.0.1'
PORT = 6968
EXTENSIONES_TEXTO = {"txt", "csv", "json", "xml", "html"}

CLAVE_CESAR = 10

PROBABILIDAD_ERROR_CHECKSUM = 0.1

def leer(nombre_archivo, extension):
    if extension.lower() in EXTENSIONES_TEXTO:
        # Leer como texto
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            contenido_string = f.read()
    else:
        # Leer como binario y convertir a base64
        with open(nombre_archivo, "rb") as f:
            contenido_binario = f.read()
            contenido_string = base64.b64encode(contenido_binario).decode("utf-8")
    
    return contenido_string

def guardar(contenido_string, extension, nombre_destino):
    if extension.lower() in EXTENSIONES_TEXTO:
        # Es texto plano
        with open(nombre_destino, "w", encoding="utf-8") as f:
            f.write(contenido_string)
    else:
        # Es binario, se debe decodificar de base64
        binario = base64.b64decode(contenido_string.encode("utf-8"))
        with open(nombre_destino, "wb") as f:
            f.write(binario)

def anade_ruido(checksum, probabilidad):
    if random.random() < probabilidad:
        return checksum + 1
    return checksum