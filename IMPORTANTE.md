# Guardar todos los archivos con current_user a cambiar por "current_user: TokenUser = Depends(get_current_user)".
# Para que este venga automáticamente inyectado por FastAPI desde el token JWT

---

## DESHABILITAR USUARIO

### 1. Verificar permisos del current_user
```sql
SELECT r.puede_habilitar 
FROM usuarios u
JOIN usuarios_roles ur ON u.id = ur.usuario_id
JOIN roles r ON ur.rol_id = r.id
WHERE u.id = {current_user_id}
LIMIT 1
```
**Nota:** Reemplazar `{current_user_id}` por el ID del usuario autenticado (desde token JWT)

### 2. Obtener usuario a deshabilitar
```sql
SELECT u.id, u.habilitado, r.nombre as rol_nombre
FROM usuarios u
LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
LEFT JOIN roles r ON ur.rol_id = r.id
WHERE u.id = {usuario_id}
LIMIT 1
```

### 3. Actualizar estado del usuario
```sql
UPDATE usuarios 
SET habilitado = 0 
WHERE id = {usuario_id}
```

---

## HABILITAR USUARIO

### 1. Verificar permisos del current_user
```sql
SELECT r.puede_habilitar 
FROM usuarios u
JOIN usuarios_roles ur ON u.id = ur.usuario_id
JOIN roles r ON ur.rol_id = r.id
WHERE u.id = {current_user_id}
LIMIT 1
```
**Nota:** Reemplazar `{current_user_id}` por el ID del usuario autenticado (desde token JWT)

### 2. Obtener usuario a habilitar
```sql
SELECT u.id, u.habilitado, r.nombre as rol_nombre
FROM usuarios u
LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
LEFT JOIN roles r ON ur.rol_id = r.id
WHERE u.id = {usuario_id}
LIMIT 1
```

### 3. Actualizar estado del usuario
```sql
UPDATE usuarios 
SET habilitado = 1 
WHERE id = {usuario_id}
```

---

## NOTAS
- `{current_user_id}` debe reemplazarse por el ID extraído del token JWT
- `{usuario_id}` es el del usuario a deshabilitar (enviado en el request JSON)
- El campo `puede_habilitar` en la tabla `roles` determina si el usuario puede modificar otros usuarios