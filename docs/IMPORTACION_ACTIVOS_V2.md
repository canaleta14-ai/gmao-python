# Importación de Activos desde Excel - Versión 2.0

## 📋 Resumen

Se ha realizado la importación exitosa de activos desde el archivo `Activos.xlsx` a la base de datos PostgreSQL del sistema GMAO, **con extracción automática de departamentos y asociación de proveedores**.

## ✅ Resultado de la Importación

- **Total de activos procesados**: 211
- **Activos creados exitosamente**: 211
- **Activos con errores**: 0
- **Activos duplicados**: 0
- **Tasa de éxito**: 100%

## 📊 Distribución por Departamento

| Código | Departamento   | Cantidad |
| ------ | -------------- | -------- |
| 000    | General        | 2        |
| 100    | Producción     | 166      |
| 140    | Zona cocción   | 11       |
| 150    | Envasado       | 13       |
| 160    | Mantenimiento  | 2        |
| 300    | Calidad        | 5        |
| 400    | Administración | 1        |
| 500    | Logística      | 3        |
| 510    | Almacén        | 8        |

## 🏢 Proveedores Asociados

- **Activos con proveedor**: 110
- **Activos sin proveedor**: 101

Los proveedores se asocian mediante el campo "Identificación fiscal proveedor activo" del Excel, buscando en la tabla de proveedores por NIF.

**Principales proveedores**:

- R. MASIP-INGENIERO. S. A (NIF: A46170858): ~45 activos
- SALVA INDUSTRIAL. S. A. (NIF: A20039426): ~15 activos
- ELECPROY AUT. Y ROBOTICA IND. S.L. (NIF: B98479819): ~13 activos
- DIOSNA Dierks & Söhne GmbH (NIF: DE811796248): 3 activos
- ROSER Construcciones Metalicas. S.A. (NIF: A17028721): 3 activos

## 🔧 Script Utilizado

**Archivo**: `scripts/cargar_activos_excel.py`

### Características principales:

1. **Extracción de departamento**: Se extrae del campo "Codigo SAGE" (primeros 3 dígitos)
2. **Código de activo**: Se usa directamente el "Codigo SAGE" del Excel
3. **Asociación de proveedores**: Búsqueda por NIF usando "Identificación fiscal proveedor activo"
4. **Mapeo de estado**: Conversión de estados del Excel a estados del sistema
5. **Validación de datos**: Verificación de campos requeridos antes de crear
6. **Transaccionalidad**: Commits cada 50 registros para optimización

### Campos mapeados:

| Campo Excel                            | Campo Modelo | Notas                         |
| -------------------------------------- | ------------ | ----------------------------- |
| Codigo SAGE                            | codigo       | Usado directamente            |
| Codigo SAGE (primeros 3)               | departamento | Extraído automáticamente      |
| Nombre del activo                      | nombre       | Requerido                     |
| Descripción                            | descripcion  | Opcional                      |
| Estado                                 | estado       | Mapeado a valores del sistema |
| Modelo                                 | modelo       | Opcional                      |
| Número de serie                        | numero_serie | Opcional                      |
| Identificación fiscal proveedor activo | proveedor    | Búsqueda por NIF              |

## 📁 Estructura del Excel

**Archivo fuente**: `Activos.xlsx`
**Filas procesadas**: 211

**Columnas utilizadas**:

- Nombre del activo
- Código del activo (no usado directamente)
- Descripción
- Estado
- **Codigo SAGE** ⭐ (usado para código y departamento)
- Modelo
- Número de serie
- Código activo del que depende
- Codigo SAGE del que depende
- **Identificación fiscal proveedor activo** ⭐ (usado para proveedor)
- Cuenta contable

## 🚀 Ejecución del Script

```bash
python scripts/cargar_activos_excel.py
```

### Opciones durante la ejecución:

1. Eliminar activos existentes (s/N)
2. Confirmación de eliminación (s/N)

### Ejemplo de salida:

```
📖 Leyendo archivo Excel: Activos.xlsx
📊 Encontradas 211 filas en el Excel
✅ Activo 1: 000A00248 - PORTON CORREDERA OFICINAS (Dpto: 000)
✅ Activo 8: 100A00019 - Camara conservación congelados 2 (Dpto: 100)
   🏢 Proveedor encontrado: R. MASIP-INGENIERO. S. A (NIF: A46170858)
...
💾 Commit intermedio: 50 activos guardados
...
📊 RESUMEN DE IMPORTACIÓN
✅ Activos creados: 211
⚠️  Activos duplicados: 0
❌ Activos con errores: 0
📈 Total procesado: 211
```

## ⚠️ Consideraciones

1. **Proveedor no encontrado**: 1 activo con NIF `B97415707` no tiene proveedor registrado en la base de datos
2. **Activos sin proveedor**: 101 activos no tienen proveedor en el Excel (es normal)
3. **Limpieza de datos**: El script limpia y valida todos los datos antes de insertarlos
4. **Códigos únicos**: Se verifica que no existan códigos duplicados

## 🔍 Validación Post-Importación

```sql
-- Verificar total de activos
SELECT COUNT(*) FROM activo;
-- Resultado: 211

-- Verificar distribución por departamento
SELECT departamento, COUNT(*) FROM activo GROUP BY departamento;

-- Verificar activos con proveedor
SELECT COUNT(*) FROM activo WHERE proveedor IS NOT NULL;
-- Resultado: 110
```

## 📝 Próximos Pasos

- [ ] Revisar el activo con proveedor faltante (NIF: B97415707)
- [ ] Completar campos opcionales (fecha_adquisicion, fabricante, etc.)
- [ ] Asignar planes de mantenimiento a activos críticos
- [ ] Configurar prioridades específicas por departamento

## 📌 Compatibilidad con Modal de Nuevo Activo

La importación está **totalmente compatible** con el formulario del modal de nuevo activo:

### Campos del Modal vs Importación:

| Campo Modal     | ¿Importado? | Fuente                                                    |
| --------------- | ----------- | --------------------------------------------------------- |
| Departamento\*  | ✅          | Codigo SAGE (primeros 3 dígitos)                          |
| Código\*        | ✅          | Codigo SAGE completo                                      |
| Nombre\*        | ✅          | Nombre del activo                                         |
| Tipo            | ❌          | No disponible en Excel                                    |
| Ubicación       | ❌          | No disponible en Excel                                    |
| Estado          | ✅          | Estado (mapeado)                                          |
| Prioridad       | ❌          | No disponible en Excel (default: Media)                   |
| Modelo          | ✅          | Modelo                                                    |
| Número de Serie | ✅          | Número de serie                                           |
| Fabricante      | ❌          | No disponible en Excel                                    |
| Proveedor       | ✅          | Identificación fiscal proveedor activo (búsqueda por NIF) |
| Descripción     | ✅          | Descripción                                               |

**Campos obligatorios (\*)**: Todos cubiertos ✅

## 🔄 Cambios Respecto a Versión 1.0

### Versión 1.0 (Original):

- ❌ Todos los activos asignados a departamento "000"
- ❌ Proveedor no asociado
- ❌ Usaba "Código del activo" (números simples)

### Versión 2.0 (Actual):

- ✅ Departamentos extraídos del "Codigo SAGE"
- ✅ Proveedores asociados por NIF
- ✅ Usa "Codigo SAGE" directamente
- ✅ 9 departamentos diferentes correctamente distribuidos
- ✅ 110 activos con proveedor asignado

---

_Documentación generada: 18 de octubre de 2025_
_Script: scripts/cargar_activos_excel.py_
_Versión: 2.0_
