# Import de las librerias importantes para el desarrollo del trabajo

import socket # Libreria para crear la comunicacion entre consolas a traves de un socket
import crcmod # Libreria para el uso de CRC-16-IBM

#Variables constantes del trabajo
HOST = 'localhost'
PORT = 65438

PORT_ESCUCHA = 65439

MSG = "yuyuyuyuyuyuyuuyuyuuyuyuyuy"

CLAVE = 10

TIEMPO_ESPERA = 2 #Segundos

MAX_UDP = 1024

MAX_DATOS = MAX_UDP - 4 - 2 - 2 - 1 # Maxima cantidad de Bytes que UDP (DGRAM) puede enviar


crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')

def cesar_general(data):
    resultado = bytearray()
    for b in data:
        resultado.append((b + CLAVE) % 256)
    return bytes(resultado)



def main():
    # Utilizando SOCK_DGRAM para eliminar la necesidad de crear una simulacion
    # SOCK_DGRAM no usa TCP, si no que UDP, que solo lanza paquetes, sin garantizar
    # el envio correcto de paquetes y es necesario realizar todos los pasos
    # de manera manual

    #Configurando el socket para escuchar y enviar
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIEMPO_ESPERA)
    sock.bind((HOST,PORT_ESCUCHA))

    #Creacion del mensaje
    mensaje = MSG.encode("utf-8")

    #Definir cuando
    total = (len(mensaje)+MAX_DATOS -1)

    for i in range(total):
        #Separa el mensaje
        separacion = mensaje[i*MAX_DATOS:(i+1)*MAX_DATOS]
        #Segmento
        cabezera = (i).to_bytes(2,'big') + (total-1).to_bytes(2,'big')
        #Cifrado Chiza
        cifrado = cesar_general(separacion)
        #Longitud del mensaje
        longitud_bytes = len(separacion).to_bytes(2,'big')

        #Se aplica el crc
        crc = crc16(cifrado)
        crc_bytes = crc.to_bytes(2,'big')

        #El fin del fin
        fin = 0
        if(i == total-1):
            fin = 1

        fin = fin.to_bytes(1,'big')
        #El paquete
        paquete = cabezera + cifrado + longitud_bytes + crc_bytes + fin

        while True: #logica para Acknoledgment
            sock.sendto(paquete,(HOST,PORT))
            try:
                respuesta,_ = sock.recvfrom(1024)
                if respuesta == b"ACK": #Si recibe la confirmacion
                    print("ACK recibido")
                    break
                elif respuesta == b"NAK": #Si no recibe la confirmacion correcta
                    print("NAK recibido, intentando nuevamente")

            except socket.timeout:
                print("Time out :c")

    print("El envio de el mensaje a finalizado")


if __name__ == "__main__":
    main()