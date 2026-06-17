from fastapi import APIRouter, Depends, Query
from database import get_connection
from auth import get_current_user, TokenUser
from typing import Optional

router = APIRouter(tags=["produccion"])


@router.get("/accesos-produccion")
def obtener_accesos_produccion(
    user_id: int = Query(..., description="ID del usuario para el cual obtener accesos"),
    current_user: Optional[TokenUser] = Depends(get_current_user)
):
    """
    Obtiene los módulos y submódulos con sus permisos para un usuario específico.
    Si el usuario tiene múltiples roles con permisos superpuestos en el mismo módulo/submódulo,
    se mostrará solo el permiso con menor prioridad.
    
    Args:
        user_id: ID del usuario del cual consultar accesos
        current_user: Usuario autenticado
    
    Returns:
        Lista de módulos con sus submódulos y permisos asociados
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener los roles del usuario
        query_roles_usuario = "SELECT rol_id FROM usuarios_roles WHERE usuario_id = %s"
        cursor.execute(query_roles_usuario, (user_id,))
        roles_resultado = cursor.fetchall()
        
        if not roles_resultado:
            # Verificar que el usuario existe
            query_usuario = "SELECT id FROM usuarios WHERE id = %s"
            cursor.execute(query_usuario, (user_id,))
            usuario = cursor.fetchone()
            
            if not usuario:
                cursor.close()
                conn.close()
                return {
                    "error": f"El usuario con ID {user_id} no existe",
                    "user_id": user_id
                }
            else:
                cursor.close()
                conn.close()
                return {
                    "user_id": user_id,
                    "modulos": [],
                    "submodulos": []
                }
        
        roles_ids = tuple(rol['rol_id'] for rol in roles_resultado)
        
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

        # Consulta para obtener submódulos del usuario con sus permisos
        query_submodulos = f"""
            SELECT 
                s.id,
                s.nombre as submodulo_nombre,
                s.path as submodulo_path,
                s.modulo_id,
                m.nombre as modulo_padre_nombre,
                p.nombre as permiso_nombre,
                p.prioridad
            FROM submodulos s
            LEFT JOIN modulos m ON s.modulo_id = m.id
            LEFT JOIN rol_submodulos rs ON s.id = rs.submodulo_id
            LEFT JOIN permisos p ON rs.permiso_id = p.id
            WHERE rs.rol_id IN ({','.join(['%s']*len(roles_ids))})
            ORDER BY s.id, p.prioridad ASC
        """
        cursor.execute(query_submodulos, roles_ids)
        submodulos_resultado = cursor.fetchall()

        # Organizar datos con prioridad - seleccionar el permiso de menor prioridad
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
            
            # Solo agregamos el primer permiso encontrado (menor prioridad debido al ORDER BY)
            if modulo['permiso_nombre'] and not modulos_dict[modulo_id]["permisos"]:
                modulos_dict[modulo_id]["permisos"].append(modulo['permiso_nombre'])

        submodulos_dict = {}
        for submodulo in submodulos_resultado:
            submodulo_id = submodulo['id']
            if submodulo_id not in submodulos_dict:
                submodulos_dict[submodulo_id] = {
                    "id": submodulo_id,
                    "nombre": submodulo['submodulo_nombre'],
                    "path": submodulo['submodulo_path'],
                    "modulo_padre": {
                        "id": submodulo['modulo_id'],
                        "nombre": submodulo['modulo_padre_nombre']
                    },
                    "permisos": []
                }
            
            # Solo agregamos el primer permiso encontrado (menor prioridad debido al ORDER BY)
            if submodulo['permiso_nombre'] and not submodulos_dict[submodulo_id]["permisos"]:
                submodulos_dict[submodulo_id]["permisos"].append(submodulo['permiso_nombre'])

        # Convertir a listas ordenadas
        modulos_lista = sorted(modulos_dict.values(), key=lambda x: x['id'])
        submodulos_lista = sorted(submodulos_dict.values(), key=lambda x: x['id'])

        cursor.close()
        conn.close()

        return {
            "modulos": modulos_lista,
            "submodulos": submodulos_lista
        }

    except Exception as e:
        cursor.close()
        conn.close()
        return {
            "error": f"Error al consultar accesos: {str(e)}",
            "user_id": user_id
        }