import socket
import sys
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Security")

DEV_MODE = True 

def check_air_gapped_environment(timeout=1.5):
    """
    Verifica la ausencia de conexión a internet para garantizar entorno air-gapped.
    """
    if DEV_MODE:
        logger.warning("DEV_MODE activo. Omitiendo bloqueo de red.")
        return True

    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout)
        logger.error("Conexión de red externa detectada.")
        logger.error("Violación de política air-gapped. Abortando ejecución.")
        sys.exit(1)
        
    except OSError:
        logger.info("Entorno air-gapped validado.")
        return True

if __name__ == "__main__":
    check_air_gapped_environment()