# Guardar todos los archivos con current_user a cambiar por "current_user: TokenUser = Depends(get_current_user)".
# Para que este venga automáticamente inyectado por FastAPI desde el token JWT

---

## ARCHIVOS A MODIFICAR CUANDO SE IMPLEMENTE JWT

Estos archivos contienen `current_user_id` como parámetro JSON que debe ser reemplazado por inyección del token JWT:

1. **routes/set/deshabilitar_usuario.py**
   - Cambiar: `current_user_id: int` en `DeshabilitarUsuario`
   - Por: `current_user: TokenUser = Depends(get_current_user)` en la función
   - Usar: `current_user.get("id")` en lugar de `data.current_user_id`

2. **routes/set/habilitar_usuario.py**
   - Cambiar: `current_user_id: int` en `HabilitarUsuario`
   - Por: `current_user: TokenUser = Depends(get_current_user)` en la función
   - Usar: `current_user.get("id")` en lugar de `data.current_user_id`

3. **routes/produccion/crear-usuario-produccion.py**
   - Cambiar: `current_user_id: int` en `CrearUsuarioProduccion`
   - Por: `current_user: TokenUser = Depends(get_current_user)` en la función
   - Usar: `current_user.get("id")` en lugar de `data.current_user_id`

4. **routes/get/data_usuarios.py**
   - Cambiar: `current_user_id: int` en `DatosUsuarioRequest`
   - Por: `current_user: TokenUser = Depends(get_current_user)` en la función
   - Usar: `current_user.get("id")` en lugar de `data.current_user_id`

5. **routes/get/usuarios.py**
   - Cambiar: `current_user_id: int` en `ObtenerUsuariosRequest`
   - Por: `current_user: TokenUser = Depends(get_current_user)` en la función
   - Usar: `current_user.get("id")` en lugar de `data.current_user_id`

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

## OBTENER DATOS DE USUARIO

### 1. Obtener datos del usuario
```sql
SELECT u.id, u.email, u.username, u.nombre, u.apellido, u.habilitado, u.legajo, u.dni, u.cambiar_contra
FROM usuarios u
WHERE u.id = {usuario_id}
```

### 2. Obtener roles del usuario
```sql
SELECT r.nombre
FROM roles r
JOIN usuarios_roles ur ON r.id = ur.rol_id
WHERE ur.usuario_id = {usuario_id}
```

---

## OBTENER TODOS LOS USUARIOS

### 1. Verificar permisos del current_user
```sql
SELECT r.puede_consultar 
FROM usuarios u
JOIN usuarios_roles ur ON u.id = ur.usuario_id
JOIN roles r ON ur.rol_id = r.id
WHERE u.id = {current_user_id}
LIMIT 1
```
**Nota:** Reemplazar `{current_user_id}` por el ID del usuario autenticado (desde token JWT)

### 2. Obtener todos los usuarios
```sql
SELECT u.id, u.email, u.username, u.nombre, u.apellido, u.habilitado
FROM usuarios u
```

### 3. Obtener roles de cada usuario
```sql
SELECT r.nombre
FROM roles r
JOIN usuarios_roles ur ON r.id = ur.rol_id
WHERE ur.usuario_id = {usuario_id}
```

---

## NOTAS
- `{current_user_id}` debe reemplazarse por el ID extraído del token JWT
- `{usuario_id}` es el del usuario a deshabilitar (enviado en el request JSON)
- El campo `puede_habilitar` en la tabla `roles` determina si el usuario puede modificar otros usuarios