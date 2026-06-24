import aiohttp
import asyncio
import os

async def notificar_nuevo_encargado(nombre: str, apellido: str, legajo: int):
    """Envía notificación de nuevo encargado a sistemas@creminox.com"""
    notificar_api_url = os.getenv("NEXT_PUBLIC_API_MAIL_URL")
    if not notificar_api_url:
        print("Error: NEXT_PUBLIC_API_MAIL_URL no configurado")
        return

    try:
        nuevo_encargado_url = f"{notificar_api_url}/notificar/nuevo-encargado"
        payload = {
            "nombre": nombre,
            "apellido": apellido,
            "legajo": legajo
        }
        
        print(f"[INFO] Intentando enviar notificación de nuevo encargado a {nuevo_encargado_url}")
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(nuevo_encargado_url, json=payload) as response:
                print(f"[SUCCESS] Notificación de nuevo encargado enviada. Status: {response.status}")
    except asyncio.TimeoutError:
        print(f"[ERROR] Timeout (30s) al enviar notificación de nuevo encargado a {notificar_api_url}")
    except aiohttp.ClientConnectorError as e:
        print(f"[ERROR] No se puede conectar a la API de notificación en {notificar_api_url}: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Error al enviar notificación de nuevo encargado: {str(e)}")
