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
            "SELECT 1 FROM Usuarios WHERE username = %s OR email = %s",
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
            INSERT INTO Usuarios
            (email, username, nombre, apellido, rol, password_hash, habilitado, reporte)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data.email,
                data.username,
                data.nombre,
                data.apellido,
                "superadmin",
                hashed_password,
                True,
                True
            )
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
