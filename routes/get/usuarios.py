from fastapi import APIRouter, Depends
from database import get_connection
from auth import get_current_user, TokenUser

router = APIRouter(tags=["usuarios"])

@router.get("/usuarios")
def obtener_usuarios(current_user: TokenUser = Depends(get_current_user)):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if current_user.get("rol") in ("admin", "user") or not current_user.get("rol"):
        query = """
            SELECT email, username, nombre, apellido, rol, habilitado, reporte FROM Usuarios WHERE rol != 'superadmin'
        """
        cursor.execute(query)
    else:
        query = """
            SELECT email, username, nombre, apellido, rol, habilitado, reporte FROM Usuarios
        """
        cursor.execute(query)

    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return usuarios
