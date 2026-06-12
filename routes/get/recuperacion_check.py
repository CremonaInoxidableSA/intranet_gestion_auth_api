from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from database import get_connection
from typing import Dict, Any, Optional, cast
import aiohttp
import asyncio
import os

router = APIRouter(tags=["usuarios"])

class RecuperacionRequest(BaseModel):
  username: str
  email: EmailStr

async def send_recovery_email(nombre: str, apellido: str, email: str):
  """Envía email de recuperación de forma asíncrona"""
  mail_api_url = os.getenv("NEXT_PUBLIC_API_MAIL_URL")
  if not mail_api_url:
    print("Error: NEXT_PUBLIC_API_MAIL_URL no configurado")
    return

  try:
    recuperacion_url = f"{mail_api_url}/recuperacion"
    payload: Dict[str, str] = {
      "nombre": nombre,
      "apellido": apellido,
      "email": email
    }
    
    print(f"[INFO] Intentando enviar email a {recuperacion_url}")
    timeout = aiohttp.ClientTimeout(total=30)  # Timeout de 30 segundos
    async with aiohttp.ClientSession(timeout=timeout) as session:
      async with session.post(recuperacion_url, json=payload) as response:
        print(f"[SUCCESS] Email de recuperación enviado. Status: {response.status}")
  except asyncio.TimeoutError:
    print(f"[ERROR] Timeout (30s) al enviar email de recuperación a {mail_api_url}. La API de mail puede estar caída o muy lenta.")
  except aiohttp.ClientConnectorError as e:
    print(f"[ERROR] No se puede conectar a la API de mail en {mail_api_url}: {str(e)}")
  except Exception as e:
    print(f"[ERROR] Error al enviar email de recuperación: {str(e)}")

@router.post("/recuperacion_check")
async def check_user_email(data: RecuperacionRequest, background_tasks: BackgroundTasks):
  conn = get_connection()
  cursor = conn.cursor(dictionary=True)

  try:
    cursor.execute(
      "SELECT username, email, nombre, apellido FROM Usuarios WHERE username = %s AND email = %s",
      (data.username, data.email)
    )
    user = cast(Optional[Dict[str, Any]], cursor.fetchone())

    if user:
      # Enviar email en background (no bloquea la respuesta)
      background_tasks.add_task(
        send_recovery_email,
        nombre=str(user["nombre"]),
        apellido=str(user["apellido"]),
        email=str(user["email"])
      )
      
      return JSONResponse(
        content={
          "success": True,
          "message": "Usuario y correo verificados correctamente"
        },
        status_code=200
      )
    else:
      return JSONResponse(
        content={
          "success": False,
          "error": "El usuario y correo no coinciden o no existen"
        },
        status_code=404
      )

  except Exception as e:
    return JSONResponse(
      content={
        "success": False,
        "error": f"Error al verificar los datos: {str(e)}"
      },
      status_code=500
    )
  finally:
    cursor.close()
    conn.close() 
