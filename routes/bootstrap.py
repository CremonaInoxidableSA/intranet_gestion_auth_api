from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from bootstrap import has_users
from database import get_connection
import bcrypt

router = APIRouter(tags=["bootstrap"])

class CrearSuperAdmin(BaseModel):
    email: EmailStr
    username: str
    nombre: str
    apellido: str
    password: str

class BootstrapResponse(BaseModel):
    success: bool
    message: str

@router.get("/needs-setup")
def needs_setup() -> dict[str, bool]:
    return {
        "needs_setup": not has_users()
    }

@router.post("/create-superadmin", response_model=BootstrapResponse)
def create_superadmin(data: CrearSuperAdmin) -> BootstrapResponse:
    if has_users():
        raise HTTPException(
            status_code=400,
            detail="Ya existen usuarios en la base de datos"
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT 1 FROM usuarios WHERE username = %s OR email = %s",
            (data.username, data.email)
        )

        if cursor.fetchone():
            raise HTTPException(
                status_code=400,
                detail="El usuario o email ya existen"
            )

        hashed_password = bcrypt.hashpw(
            data.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        cursor.execute(
            """
            INSERT INTO usuarios
            (email, username, nombre, apellido, password_hash, habilitado, cambiar_contra)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.email,
                data.username,
                data.nombre,
                data.apellido,
                hashed_password,
                True,
                False
            )
        )

        # Obtener el ID del usuario recién creado
        usuario_id = cursor.lastrowid

        # Asignar el rol superadmin (id = 1) al usuario
        cursor.execute(
            """
            INSERT INTO usuarios_roles
            (usuario_id, rol_id)
            VALUES (%s, %s)
            """,
            (usuario_id, 1)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return BootstrapResponse(
            success=True,
            message="Superadmin creado exitosamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error creando superadmin: {str(e)}"
        )