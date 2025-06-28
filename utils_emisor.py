import json
import select

# Configuración de timeout
TIMEOUT_SEGUNDOS = 0.5
MAX_REINTENTOS = 200

def enviar_paquete(s, secuencia, longitud_mensaje, fragmento_mensaje, checksum, fin_de_paquete):
    paquete = {
        "secuencia": secuencia,
        "longitud": longitud_mensaje,
        "mensaje": fragmento_mensaje,
        "checksum": checksum,
        "fin_de_paquete": fin_de_paquete
    }

    # Convertir a JSON y agregar fin de linea para simular un archivo de texto
    json_paquete = json.dumps(paquete) + "\n"
    s.sendall(json_paquete.encode())
    print(f"→ Enviado paquete secuencia {secuencia}")

def esperar_confirmacion_con_timeout(s, s_file, secuencia_esperada):
    """
    Espera confirmación con timeout y valida que sea para la secuencia correcta
    Returns: (True, confirmacion) si recibe ACK correcto, (False, None) si debe reenviar
    """
    try:
        # Usar select para implementar timeout
        ready, _, _ = select.select([s], [], [], TIMEOUT_SEGUNDOS) # Retorna una lista (de un elemento en este caso) de sockets disponibles para leer, [] si no
        
        if not ready:
            print(f"Timeout esperando confirmación para secuencia {secuencia_esperada}")
            return False, None
        
        # Leer la respuesta del receptor
        respuesta = s_file.readline()
        
        if not respuesta:
            print("No se recibió confirmación (conexión cerrada)")
            return False, None
            
        try:
            confirmacion = json.loads(respuesta.strip())
            print(f"← Recibido: {confirmacion['tipo']} para secuencia {confirmacion['secuencia']}")
            
            # Validar que la confirmación sea para la secuencia correcta
            if confirmacion['secuencia'] != secuencia_esperada:
                print(f"Confirmación para secuencia incorrecta. Esperaba {secuencia_esperada}, recibí {confirmacion['secuencia']}")
                return False, None
            
            if confirmacion["tipo"] == "ACK":
                return True, confirmacion
            elif confirmacion["tipo"] == "NAK":
                print(f"NAK recibido para secuencia {confirmacion['secuencia']} - Reenviando...")
                return False, confirmacion
            else:
                print(f"Tipo de confirmación desconocido: {confirmacion['tipo']}")
                return False, None
                
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            return False, None
            
    except Exception as e:
        print(f"Error esperando confirmación: {e}")
        return False, None