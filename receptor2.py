import socket
import crcmod

HOST = 'localhost'
PORT = 65438

PORT_CONFIRMA = 65439

CLAVE = 10

TIEMPO_ESPERA = 2 #Segundos

crc16 = crcmod.predefined.mkCrcFun('crc-ccitt-false')

def decesar_general(data):
    resultado = bytearray()
    for b in data:
        resultado.append((b - CLAVE) % 256)
    return bytes(resultado)


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    while True:
        data,_ = sock.recvfrom(1024)
        print("Mensaje recibido:", data)
        segmento = int.from_bytes(data[0:2], 'big')
        total = int.from_bytes(data[2:4], 'big')
        # La longitud de los datos cifrados está en los 2 bytes antes del CRC y fin
        longitud = int.from_bytes(data[-5:-3], 'big')
        crc_recibido = int.from_bytes(data[-3:-1], 'big')
        fin = data[-1]

        # Extraer datos cifrados
        cifrado = data[4:-5]

        crc_calculado = crc16(cifrado)
        if crc_calculado != crc_recibido:
            print("¡Error de CRC!")
            sock.sendto(b"NAK", (HOST,PORT_CONFIRMA))

        datos = decesar_general(cifrado)
        print(f"Segmento {segmento}/{total}, fin={fin}")
        print("Datos descifrados:", datos[:longitud].decode('utf-8'))

        sock.sendto(b"ACK", (HOST,PORT_CONFIRMA))
        if fin == 1:
            break

if __name__ == "__main__":
    main()