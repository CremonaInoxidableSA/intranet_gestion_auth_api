# Guardar todos los archivos con current_user a cambiar por "current_user: TokenUser = Depends(get_current_user)".
# Para que este venga automáticamente inyectado por FastAPI desde el token JWT

---

## ACCESOS PRODUCCION

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

## CREAR USUARIO PRODUCCION

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

### 2. Verificar que no exista usuario con mismo legajo
```sql
SELECT nombre, apellido FROM usuarios WHERE legajo = {legajo}
```
**Si existe:** Retornar error "Ya existe un usuario con el legajo indicado en el sistema. Este usuario es {nombre} {apellido}"

### 3. Crear usuario con campos vacíos
```sql
INSERT INTO usuarios (nombre, apellido, legajo, password_hash, email, username, habilitado, dni, cambiar_contra)
VALUES ({nombre}, {apellido}, {legajo}, NULL, NULL, NULL, 1, NULL, 0)
```
**Mapeo de roles:**
- rol="encargado" -> rol_id=3
- rol="operario" -> rol_id=4

### 4. Asignar rol al usuario
```sql
INSERT INTO usuarios_roles (usuario_id, rol_id)
VALUES ({usuario_id}, {rol_id})
```
**Nota:** El `{usuario_id}` es el ID retornado del INSERT anterior

---

## NOTAS
- `{current_user_id}` debe reemplazarse por el ID extraído del token JWT
- `{usuario_id}` es el del usuario a deshabilitar (enviado en el request JSON)
- El campo `puede_habilitar` en la tabla `roles` determina si el usuario puede modificar otros usuarios