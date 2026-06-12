from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_connection
import bcrypt

router = APIRouter(tags=["usuarios"])

class CrearUsuario(BaseModel):
    email: EmailStr
    username: str
    nombre: str
    apellido: str
    rol: str
    password: str
    reporte: bool

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@router.post("/crear_usuario", response_model=ApiResponse)
def crear_usuario(data: CrearUsuario) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar duplicados
    cursor.execute(
        "SELECT 1 FROM Usuarios WHERE username = %s OR email = %s",
        (data.username, data.email)
    )

    if cursor.fetchone():
        raise HTTPException(
            status_code=400,
            detail="El usuario o email ya existen"
        )

    # Hash de contraseña
    hashed_password = bcrypt.hashpw(
        data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    try:
        cursor.execute(
            """
            INSERT INTO Usuarios
            (email, username, nombre, apellido, rol, password_hash, habilitado, reporte)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.email,
                data.username,
                data.nombre,
                data.apellido,
                data.rol,
                hashed_password,
                1,
                int(data.reporte),
            )
        )
        conn.commit()
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(success=True, message="Usuario creado correctamente")
