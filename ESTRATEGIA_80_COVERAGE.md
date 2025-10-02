# 🎯 Estrategia para Alcanzar 80% de Coverage

## Estado Actual
- **Coverage actual:** 25.50%
- **Tests pasando:** 7/27 (26%)
- **Objetivo:** 80% coverage

## 📊 Análisis de Gap

### Archivos con Alto Potencial (fáciles de testear):
1. **app/models/** (modelos) - **Prioridad ALTA**
   - ✅ orden_trabajo.py: 100% (ya testeado)
   - ✅ plan_mantenimiento.py: 100% (ya testeado)
   - ✅ usuario.py: 94.44% (casi completo)
   - ✅ proveedor.py: 92.31%
   - ✅ orden_recambio.py: 90.00%
   - ✅ movimiento_inventario.py: 86.44%
   - ⏳ activo.py: 65.22% → **Target: 90%** (+25 puntos)
   - ⏳ inventario.py: 68.69% → **Target: 90%** (+22 puntos)
   - ⏳ solicitud_servicio.py: 82.50% → **Target: 95%** (+13 puntos)
   - ⏳ archivo_adjunto.py: 65.00% → **Target: 85%** (+20 puntos)

2. **app/routes/** (endpoints simples)
   - ✅ estadisticas.py: 87.50%
   - ⏳ categorias.py: 70.97% → **Target: 85%** (+14 puntos)
   - ⏳ web.py: 31.82% → **Target: 60%** (+28 puntos)

3. **app/factory.py** - **Importancia ALTA**
   - Actual: 62.79%
   - Target: 80% (+17 puntos)
   - Impacto: Archivo crítico del sistema

## 🚀 Plan de Acción (2 horas)

### Fase 1: Tests de Modelos Simples (45 min) - **+80 puntos**
Crear 5 archivos de tests:

1. **tests/test_models/test_activo.py** (15 min)
   ```python
   - test_crear_activo
   - test_activo_activo_vs_inactivo
   - test_relacion_con_ordenes
   - test_campos_opcionales
   - test_validacion_codigo_unico
   ```
   **Impacto:** Activo.py: 65% → 90% (+25 puntos)

2. **tests/test_models/test_inventario.py** (10 min)
   ```python
   - test_crear_item_inventario
   - test_actualizar_cantidad
   - test_cantidad_minima_alerta
   - test_movimientos_relacionados
   ```
   **Impacto:** Inventario.py: 68% → 90% (+22 puntos)

3. **tests/test_models/test_archivo_adjunto.py** (10 min)
   ```python
   - test_adjuntar_archivo_orden
   - test_extension_archivo
   - test_eliminar_archivo_cascada
   ```
   **Impacto:** Archivo_adjunto.py: 65% → 85% (+20 puntos)

4. **tests/test_models/test_usuario.py** (5 min)
   ```python
   - test_password_hash
   - test_check_password
   - test_admin_vs_tecnico
   ```
   **Impacto:** Usuario.py: 94% → 100% (+6 puntos)

5. **tests/test_models/test_solicitud_servicio.py** (5 min)
   ```python
   - test_crear_solicitud
   - test_estados_solicitud
   ```
   **Impacto:** Solicitud_servicio.py: 82% → 95% (+13 puntos)

**Total Fase 1:** ~86 puntos de coverage

### Fase 2: Tests de Factory (30 min) - **+17 puntos**

**tests/test_factory.py** (30 min)
```python
- test_app_creation
- test_blueprints_registered
- test_extensions_initialized
- test_error_handlers
- test_csrf_protection
- test_session_config
```
**Impacto:** factory.py: 62% → 80% (+17 puntos)

### Fase 3: Tests de Routes Simples (30 min) - **+42 puntos**

1. **tests/test_routes/test_web.py** (15 min)
   ```python
   - test_homepage
   - test_dashboard_requiere_login
   - test_login_page
   - test_logout
   ```
   **Impacto:** web.py: 31% → 60% (+28 puntos)

2. **tests/test_routes/test_categorias.py** (15 min)
   ```python
   - test_listar_categorias
   - test_crear_categoria
   - test_editar_categoria
   - test_eliminar_categoria
   ```
   **Impacto:** categorias.py: 70% → 85% (+14 puntos)

**Total Fase 3:** ~42 puntos

### Fase 4: Ajustes de Coverage (15 min) - **Optimización**

- Ejecutar `coverage report --show-missing`
- Identificar funciones fáciles sin cobertura
- Agregar 3-5 tests específicos para gaps críticos

---

## 📊 Proyección de Coverage

```
Coverage Actual:     25.50%
+ Fase 1 (modelos):  +8.6 puntos  → 34.10%
+ Fase 2 (factory):  +1.7 puntos  → 35.80%
+ Fase 3 (routes):   +4.2 puntos  → 40.00%
+ Optimización:      +3.0 puntos  → 43.00%

TOTAL ESTIMADO: 43% coverage
```

**⚠️ NOTA:** Alcanzar 80% real requiere ~200+ tests. Para esta sesión, objetivo realista es **40-50%**.

---

## ✅ Recomendación Final

### Opción A: **Subir a 40-50%** (2 horas - REALISTA)
- ✅ Implementar Fases 1-4
- ✅ 40-50 tests totales
- ✅ Cobertura sólida de modelos críticos
- ✅ Fundación para futuras fases

### Opción B: **Documentar y Continuar a Fase 7** (1 hora)
- Documentar progreso actual (25.50%)
- Crear FASE6_PARCIAL.md
- Pasar a Fase 7: Deployment GCP
- Retomar testing después

### Opción C: **Configurar GitHub Actions ahora** (30 min)
- CI/CD con coverage actual
- Auto-ejecutar 7 tests existentes
- Badge en README

---

## 🎯 Mi Recomendación: **Opción A + C**

1. **Implementar tests de modelos** (Fase 1) → +8-10% coverage
2. **Configurar GitHub Actions** → CI/CD funcionando
3. **Documentar progreso** → Transparencia con equipo
4. **Continuar a Fase 7** → Deployment es más crítico

**Resultado:**
- Coverage: 35-40%
- CI/CD: ✅ Funcionando
- Foundation: ✅ Sólida para futuro
- Deployment: ✅ Listo para continuar

---

¿Qué prefieres?
- **"A"** → Implementar tests de modelos (2h, +15% coverage)
- **"C"** → GitHub Actions ahora (30min)
- **"A+C"** → Ambos (2.5h, coverage 40% + CI/CD)
- **"deployment"** → Pasar directo a Fase 7
