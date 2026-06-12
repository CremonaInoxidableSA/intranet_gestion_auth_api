from database import get_connection
import logging
from typing import cast, Dict, Any

logger = logging.getLogger(__name__)

def has_users() -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM Usuarios")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result is None:
            return False
        
        result_dict = cast(Dict[str, Any], result)
        count: int = int(result_dict["count"]) if result_dict.get("count") is not None else 0
        return count > 0
    except Exception as e:
        logger.error(f"Error verificando usuarios: {e}")
        return False

def bootstrap():
    try:
        logger.info("Bootstrap iniciado")
    except Exception as e:
        logger.error(f"{e}")
