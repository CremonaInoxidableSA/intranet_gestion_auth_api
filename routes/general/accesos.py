from fastapi import APIRouter, Depends, Query
from database import get_connection
from auth import get_current_user, TokenUser
from typing import Optional

router = APIRouter(tags=["general"])


@router.get("/accesos")
def obtener_accesos(
    user_id: int = Query(..., description="ID del usuario para el cual obtener accesos"),
    current_user: Optional[TokenUser] = Depends(get_current_user)
):
    """
    Obtiene los módulos y submódulos con sus permisos para un usuario específico.
    Jerarquía de validación:
    1. Si el usuario está deshabilitado (habilitado=false), retorna DESHABILITADO
    2. Si hay módulos bloqueados en usuarios_bloqueados, retorna BLOQUEADO para esos módulos
    3. Si no hay bloqueos, retorna los permisos normales con menor prioridad
    
    Args:
        user_id: ID del usuario del cual consultar accesos
        current_user: Usuario autenticado
    
    Returns:
        Lista de módulos con sus submódulos y permisos asociados
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Verificar si el usuario existe y su estado de habilitación
        query_usuario = "SELECT id, habilitado FROM usuarios WHERE id = %s"
        cursor.execute(query_usuario, (user_id,))
        usuario = cursor.fetchone()
        
        if not usuario:
            cursor.close()
            conn.close()
            return {
                "error": f"El usuario con ID {user_id} no existe",
                "user_id": user_id
            }
        
        # Si el usuario está deshabilitado, retornar DESHABILITADO
        if not usuario['habilitado']:
            cursor.close()
            conn.close()
            
            return {
                "estado": "DESHABILITADO"
            }
        
        # Obtener los roles del usuario
        query_roles_usuario = "SELECT rol_id FROM usuarios_roles WHERE usuario_id = %s"
        cursor.execute(query_roles_usuario, (user_id,))
        roles_resultado = cursor.fetchall()
        
        if not roles_resultado:
            cursor.close()
            conn.close()
            return {
                "user_id": user_id,
                "modulos": []
            }
        
        roles_ids = tuple(rol['rol_id'] for rol in roles_resultado)
        
        # Obtener módulos bloqueados para el usuario
        query_bloqueados = "SELECT modulo_id FROM usuarios_bloqueados WHERE usuario_id = %s AND bloqueado = TRUE"
        cursor.execute(query_bloqueados, (user_id,))
        bloqueados_resultado = cursor.fetchall()
        modulos_bloqueados = set(bl['modulo_id'] for bl in bloqueados_resultado)
        
        # Consulta para obtener módulos del usuario con sus permisos
        # Ordena por prioridad para seleccionar el permiso con menor prioridad
        query_modulos = f"""
            SELECT 
                m.id,
                m.nombre as modulo_nombre,
                m.path as modulo_path,
                p.nombre as permiso_nombre,
                p.prioridad
            FROM modulos m
            LEFT JOIN rol_modulos rm ON m.id = rm.modulo_id
            LEFT JOIN permisos p ON rm.permiso_id = p.id
            WHERE rm.rol_id IN ({','.join(['%s']*len(roles_ids))})
            ORDER BY m.id, p.prioridad ASC
        """
        cursor.execute(query_modulos, roles_ids)
        modulos_resultado = cursor.fetchall()

        # Organizar datos con prioridad - seleccionar el permiso de menor prioridad
        # O BLOQUEADO si el módulo está bloqueado
        modulos_dict = {}
        for modulo in modulos_resultado:
            modulo_id = modulo['id']
            if modulo_id not in modulos_dict:
                modulos_dict[modulo_id] = {
                    "id": modulo_id,
                    "nombre": modulo['modulo_nombre'],
                    "path": modulo['modulo_path'],
                    "permisos": []
                }
            
            # Si el módulo está bloqueado, marcar como BLOQUEADO
            if modulo_id in modulos_bloqueados:
                modulos_dict[modulo_id]["permisos"] = ["BLOQUEADO"]
            # Si no está bloqueado, agregar el permiso de menor prioridad
            elif modulo['permiso_nombre'] and not modulos_dict[modulo_id]["permisos"]:
                modulos_dict[modulo_id]["permisos"].append(modulo['permiso_nombre'])

        # Convertir a listas ordenadas
        modulos_lista = sorted(modulos_dict.values(), key=lambda x: x['id'])

        cursor.close()
        conn.close()

        return {
            "modulos": modulos_lista
        }

    except Exception as e:
        cursor.close()
        conn.close()
        return {
            "error": f"Error al consultar accesos: {str(e)}",
            "user_id": user_id
        }