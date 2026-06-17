INSERT INTO roles (id, nombre, puede_habilitar, puede_consultar) VALUES
 (1, 'superadmin', true, true),
 (2, 'admin-produccion', true, false),
 (3, 'encargado-produccion', false, false),
 (4, 'operario', false, false),
 (5, 'oficina', false, false),
 (6, 'empleado', false, false);