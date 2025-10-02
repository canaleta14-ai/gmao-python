# ⏰ FASE 5: Google Cloud Scheduler - Plan de Implementación

**Objetivo:** Automatizar generación de órdenes de mantenimiento preventivo mediante cron jobs

**Tiempo estimado:** 2-3 horas  
**Prioridad:** 🟡 MEDIA (mejora operativa importante)

---

## 🎯 Problema a Resolver

### **Situación Actual:**
```
Plan de Mantenimiento Preventivo
├─ Frecuencia: Cada 30 días
├─ Última ejecución: 15/09/2025
├─ Próxima ejecución: 15/10/2025 ⚠️ YA VENCIDO
└─ Acción: ❌ REQUIERE INTERVENCIÓN MANUAL

Usuario debe:
1. Revisar planes manualmente
2. Crear orden de trabajo manualmente
3. Asignar técnico manualmente
4. Enviar notificaciones manualmente
```

### **Solución con Cloud Scheduler:**
```
Cloud Scheduler (cron diario)
├─ Ejecuta: 00:00 AM cada día
├─ Revisa: Planes de mantenimiento vencidos
├─ Genera: Órdenes de trabajo automáticamente
├─ Asigna: Técnico responsable
├─ Notifica: Email a técnico y supervisores
└─ Actualiza: Próxima fecha de ejecución

✅ AUTOMATIZACIÓN COMPLETA
```

---

## 📋 Tareas

### **1. Crear Endpoint de Cron** ⏱️ 45 min

**Archivo:** `app/routes/cron.py` (NUEVO)

```python
"""
Endpoints para tareas programadas (cron jobs)
Protegidos con X-Appengine-Cron header
"""
from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.plan_mantenimiento import PlanMantenimiento
from app.models.orden_trabajo import OrdenTrabajo
from app.models.activo import Activo
from app.models.usuario import Usuario
from datetime import datetime, timezone, timedelta
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)

cron_bp = Blueprint('cron', __name__, url_prefix='/api/cron')

def is_valid_cron_request():
    """
    Verificar que la petición viene de Cloud Scheduler
    En App Engine, el header X-Appengine-Cron solo puede ser
    establecido por el sistema, no por usuarios externos
    """
    # En desarrollo, permitir sin header
    if current_app.config.get('FLASK_ENV') == 'development':
        return True
    
    # En producción, verificar header de App Engine
    return request.headers.get('X-Appengine-Cron') == 'true'

@cron_bp.route('/generar-ordenes-preventivas', methods=['GET', 'POST'])
def generar_ordenes_preventivas():
    """
    Genera órdenes de trabajo para planes de mantenimiento vencidos
    
    Ejecutado por Cloud Scheduler diariamente a las 00:00 AM
    
    Returns:
        JSON con resumen de órdenes generadas
    """
    # Verificar que la petición es válida
    if not is_valid_cron_request():
        logger.warning("Intento de acceso no autorizado a endpoint de cron")
        return jsonify({
            "error": "Acceso no autorizado",
            "mensaje": "Este endpoint solo puede ser llamado por Cloud Scheduler"
        }), 403
    
    try:
        logger.info("=== INICIO: Generación automática de órdenes preventivas ===")
        
        # Obtener fecha actual
        hoy = datetime.now(timezone.utc).date()
        
        # Buscar planes activos que necesitan ejecución
        # (próxima_ejecucion <= hoy)
        planes_vencidos = PlanMantenimiento.query.filter(
            and_(
                PlanMantenimiento.activo == True,
                PlanMantenimiento.proxima_ejecucion <= hoy
            )
        ).all()
        
        logger.info(f"Planes vencidos encontrados: {len(planes_vencidos)}")
        
        ordenes_creadas = []
        errores = []
        
        for plan in planes_vencidos:
            try:
                # Generar orden de trabajo
                orden = crear_orden_desde_plan(plan)
                
                if orden:
                    ordenes_creadas.append({
                        "orden_id": orden.id,
                        "numero_orden": orden.numero_orden,
                        "plan_id": plan.id,
                        "activo": plan.activo.nombre if plan.activo else "N/A",
                        "descripcion": orden.descripcion
                    })
                    
                    logger.info(f"✅ Orden creada: {orden.numero_orden} para plan {plan.id}")
                    
                    # Enviar notificación (si está configurado)
                    enviar_notificacion_orden_creada(orden, plan)
                
            except Exception as e:
                error_msg = f"Error procesando plan {plan.id}: {str(e)}"
                logger.error(error_msg)
                errores.append({
                    "plan_id": plan.id,
                    "error": str(e)
                })
        
        # Commit de todos los cambios
        db.session.commit()
        
        # Preparar respuesta
        resumen = {
            "fecha_ejecucion": hoy.isoformat(),
            "planes_revisados": len(planes_vencidos),
            "ordenes_creadas": len(ordenes_creadas),
            "errores": len(errores),
            "detalles": {
                "ordenes": ordenes_creadas,
                "errores": errores
            }
        }
        
        logger.info(f"=== FIN: {len(ordenes_creadas)} órdenes creadas, {len(errores)} errores ===")
        
        return jsonify(resumen), 200
        
    except Exception as e:
        logger.error(f"Error crítico en generación de órdenes: {str(e)}")
        db.session.rollback()
        return jsonify({
            "error": "Error en generación de órdenes",
            "mensaje": str(e)
        }), 500

def crear_orden_desde_plan(plan):
    """
    Crea una orden de trabajo a partir de un plan de mantenimiento
    
    Args:
        plan: PlanMantenimiento instance
    
    Returns:
        OrdenTrabajo: Nueva orden creada
    """
    # Generar número de orden único
    ultimo_numero = db.session.query(db.func.max(OrdenTrabajo.id)).scalar() or 0
    numero_orden = f"OT-{ultimo_numero + 1:06d}"
    
    # Crear descripción basada en el plan
    descripcion = f"Mantenimiento {plan.tipo_mantenimiento}: {plan.descripcion}"
    if plan.tareas:
        descripcion += f"\n\nTareas:\n{plan.tareas}"
    
    # Crear orden
    nueva_orden = OrdenTrabajo(
        numero_orden=numero_orden,
        tipo="Preventivo",
        prioridad=plan.prioridad or "Media",
        estado="Pendiente",
        descripcion=descripcion,
        activo_id=plan.activo_id,
        tecnico_id=plan.responsable_id,
        tiempo_estimado=plan.duracion_estimada,
        fecha_programada=datetime.now(timezone.utc).date(),
        plan_mantenimiento_id=plan.id
    )
    
    db.session.add(nueva_orden)
    
    # Actualizar próxima ejecución del plan
    plan.ultima_ejecucion = datetime.now(timezone.utc).date()
    
    # Calcular próxima ejecución según frecuencia
    if plan.frecuencia_dias:
        plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(days=plan.frecuencia_dias)
    elif plan.frecuencia_meses:
        # Aproximación: 1 mes = 30 días
        dias = plan.frecuencia_meses * 30
        plan.proxima_ejecucion = plan.ultima_ejecucion + timedelta(days=dias)
    
    return nueva_orden

def enviar_notificacion_orden_creada(orden, plan):
    """
    Envía notificación por email sobre orden creada
    
    Args:
        orden: OrdenTrabajo instance
        plan: PlanMantenimiento instance
    """
    try:
        # Verificar si el email está configurado
        if not current_app.config.get('MAIL_SERVER'):
            logger.info("Email no configurado, omitiendo notificación")
            return
        
        from flask_mail import Message, Mail
        
        mail = Mail(current_app)
        
        # Destinatarios
        destinatarios = []
        
        # Técnico responsable
        if orden.tecnico and orden.tecnico.email:
            destinatarios.append(orden.tecnico.email)
        
        # Administradores (desde configuración)
        admin_emails = current_app.config.get('ADMIN_EMAILS', '').split(',')
        destinatarios.extend([e.strip() for e in admin_emails if e.strip()])
        
        if not destinatarios:
            logger.warning("No hay destinatarios configurados para notificación")
            return
        
        # Crear mensaje
        asunto = f"Nueva Orden Preventiva: {orden.numero_orden}"
        
        cuerpo = f"""
Se ha generado automáticamente una nueva orden de trabajo preventivo:

ORDEN: {orden.numero_orden}
ACTIVO: {orden.activo.nombre if orden.activo else 'N/A'} ({orden.activo.codigo if orden.activo else 'N/A'})
TIPO: Mantenimiento {plan.tipo_mantenimiento}
PRIORIDAD: {orden.prioridad}
TÉCNICO ASIGNADO: {orden.tecnico.nombre if orden.tecnico else 'Sin asignar'}

DESCRIPCIÓN:
{orden.descripcion}

TIEMPO ESTIMADO: {orden.tiempo_estimado} horas
FECHA PROGRAMADA: {orden.fecha_programada.strftime('%d/%m/%Y') if orden.fecha_programada else 'No programada'}

---
Esta orden fue generada automáticamente por el sistema de mantenimiento preventivo.
Accede al sistema para más detalles: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
"""
        
        msg = Message(
            subject=asunto,
            recipients=destinatarios,
            body=cuerpo
        )
        
        mail.send(msg)
        logger.info(f"Notificación enviada a: {', '.join(destinatarios)}")
        
    except Exception as e:
        logger.error(f"Error enviando notificación: {str(e)}")
        # No fallar si el email falla

@cron_bp.route('/verificar-alertas', methods=['GET', 'POST'])
def verificar_alertas():
    """
    Verifica activos sin mantenimiento reciente y envía alertas
    
    Ejecutado por Cloud Scheduler semanalmente
    """
    if not is_valid_cron_request():
        return jsonify({"error": "Acceso no autorizado"}), 403
    
    try:
        logger.info("=== INICIO: Verificación de alertas ===")
        
        # Fecha límite (activos sin mantenimiento en últimos 90 días)
        fecha_limite = datetime.now(timezone.utc).date() - timedelta(days=90)
        
        # Buscar activos críticos sin órdenes recientes
        from sqlalchemy import or_
        
        activos_sin_mantenimiento = Activo.query.filter(
            and_(
                Activo.estado.in_(['Operativo', 'En Mantenimiento']),
                or_(
                    Activo.fecha_ultimo_mantenimiento == None,
                    Activo.fecha_ultimo_mantenimiento < fecha_limite
                )
            )
        ).all()
        
        alertas_enviadas = []
        
        for activo in activos_sin_mantenimiento:
            # Enviar alerta
            enviar_alerta_mantenimiento(activo)
            alertas_enviadas.append({
                "activo_id": activo.id,
                "codigo": activo.codigo,
                "nombre": activo.nombre,
                "ultimo_mantenimiento": activo.fecha_ultimo_mantenimiento.isoformat() if activo.fecha_ultimo_mantenimiento else None
            })
        
        logger.info(f"=== FIN: {len(alertas_enviadas)} alertas enviadas ===")
        
        return jsonify({
            "fecha": datetime.now(timezone.utc).isoformat(),
            "activos_revisados": Activo.query.count(),
            "alertas_enviadas": len(alertas_enviadas),
            "detalles": alertas_enviadas
        }), 200
        
    except Exception as e:
        logger.error(f"Error en verificación de alertas: {str(e)}")
        return jsonify({"error": str(e)}), 500

def enviar_alerta_mantenimiento(activo):
    """Envía alerta sobre activo que requiere mantenimiento"""
    try:
        if not current_app.config.get('MAIL_SERVER'):
            return
        
        from flask_mail import Message, Mail
        mail = Mail(current_app)
        
        admin_emails = current_app.config.get('ADMIN_EMAILS', '').split(',')
        destinatarios = [e.strip() for e in admin_emails if e.strip()]
        
        if not destinatarios:
            return
        
        msg = Message(
            subject=f"⚠️ Alerta: {activo.nombre} requiere mantenimiento",
            recipients=destinatarios,
            body=f"""
ALERTA DE MANTENIMIENTO

ACTIVO: {activo.nombre} ({activo.codigo})
UBICACIÓN: {activo.ubicacion or 'No especificada'}
ÚLTIMO MANTENIMIENTO: {activo.fecha_ultimo_mantenimiento.strftime('%d/%m/%Y') if activo.fecha_ultimo_mantenimiento else 'Nunca'}

Este activo lleva más de 90 días sin mantenimiento registrado.
Se recomienda programar una inspección o mantenimiento preventivo.

Accede al sistema: {current_app.config.get('SERVER_URL', 'http://localhost:5000')}
"""
        )
        
        mail.send(msg)
        logger.info(f"Alerta enviada para activo {activo.codigo}")
        
    except Exception as e:
        logger.error(f"Error enviando alerta para activo {activo.id}: {str(e)}")

@cron_bp.route('/test', methods=['GET'])
def test_cron():
    """
    Endpoint de prueba para verificar que el cron funciona
    Solo en desarrollo
    """
    if current_app.config.get('FLASK_ENV') != 'development':
        return jsonify({"error": "Solo disponible en desarrollo"}), 403
    
    return jsonify({
        "mensaje": "Endpoint de cron funcionando",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cron_header": request.headers.get('X-Appengine-Cron', 'No presente')
    }), 200
```

**Características:**
- ✅ Protección con `X-Appengine-Cron` header
- ✅ Generación automática de órdenes preventivas
- ✅ Actualización de fechas de planes
- ✅ Notificaciones por email
- ✅ Logging detallado
- ✅ Manejo de errores robusto

---

### **2. Registrar Blueprint en Factory** ⏱️ 5 min

**Archivo:** `app/factory.py`

Agregar al final de la función `create_app()`, antes del return:

```python
    # Registrar blueprint de cron
    from app.routes.cron import cron_bp
    app.register_blueprint(cron_bp)
    
    logger.info("Blueprint de cron registrado")
```

---

### **3. Actualizar Modelo de Orden de Trabajo** ⏱️ 10 min

**Archivo:** `app/models/orden_trabajo.py`

Agregar campo para relacionar con plan de mantenimiento:

```python
# Relación con plan de mantenimiento (opcional)
plan_mantenimiento_id = db.Column(
    db.Integer, 
    db.ForeignKey('plan_mantenimiento.id'),
    nullable=True
)

# Relación
plan_mantenimiento = db.relationship(
    'PlanMantenimiento',
    backref='ordenes_generadas',
    lazy=True
)
```

---

### **4. Configurar Migración de Base de Datos** ⏱️ 10 min

```bash
# Generar migración
flask db migrate -m "Agregar relación orden-plan de mantenimiento"

# Revisar migración generada en migrations/versions/

# Aplicar migración
flask db upgrade
```

---

### **5. Configurar cron.yaml para App Engine** ⏱️ 15 min

**Archivo:** `cron.yaml` (NUEVO en raíz del proyecto)

```yaml
cron:
# Generación diaria de órdenes preventivas
- description: "Generar órdenes de mantenimiento preventivo"
  url: /api/cron/generar-ordenes-preventivas
  schedule: every day 00:00
  timezone: America/Mexico_City
  target: default
  
# Verificación semanal de alertas
- description: "Verificar activos sin mantenimiento reciente"
  url: /api/cron/verificar-alertas
  schedule: every monday 08:00
  timezone: America/Mexico_City
  target: default
```

**Formatos de schedule:**
- `every 1 hours` - Cada hora
- `every day 00:00` - Diario a medianoche
- `every monday 08:00` - Cada lunes a las 8 AM
- `1st,15th of month 09:00` - Día 1 y 15 de cada mes
- `every 30 minutes` - Cada 30 minutos

**Nota:** El archivo `cron.yaml` se despliega junto con `app.yaml`:
```bash
gcloud app deploy cron.yaml
```

---

### **6. Actualizar Variables de Entorno** ⏱️ 5 min

**Archivo:** `.env.example`

```env
# -------------------- EMAIL NOTIFICATIONS --------------------
# Emails de administradores para notificaciones (separados por coma)
ADMIN_EMAILS=admin@ejemplo.com,supervisor@ejemplo.com

# URL del servidor (para enlaces en emails)
SERVER_URL=https://tu-proyecto.appspot.com
```

---

### **7. Script de Testing Local** ⏱️ 30 min

**Archivo:** `scripts/test_cron_local.py` (NUEVO)

```python
"""
Script para probar endpoints de cron localmente
Simula el comportamiento de Cloud Scheduler
"""
import sys
from pathlib import Path

# Añadir path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from datetime import datetime
import requests

def test_generar_ordenes():
    """Test de generación de órdenes preventivas"""
    print("=" * 70)
    print("🧪 TEST: Generar Órdenes Preventivas")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.test_client() as client:
        # Simular petición de cron
        response = client.post('/api/cron/generar-ordenes-preventivas')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(response.get_json())
        print()
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Planes revisados: {data.get('planes_revisados', 0)}")
            print(f"✅ Órdenes creadas: {data.get('ordenes_creadas', 0)}")
            print(f"⚠️  Errores: {data.get('errores', 0)}")
            
            if data.get('detalles', {}).get('ordenes'):
                print("\nÓrdenes generadas:")
                for orden in data['detalles']['ordenes']:
                    print(f"  - {orden['numero_orden']}: {orden['descripcion'][:50]}...")
        else:
            print(f"❌ Error: {response.get_json()}")

def test_verificar_alertas():
    """Test de verificación de alertas"""
    print()
    print("=" * 70)
    print("🧪 TEST: Verificar Alertas")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.test_client() as client:
        response = client.post('/api/cron/verificar-alertas')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(response.get_json())
        print()
        
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Activos revisados: {data.get('activos_revisados', 0)}")
            print(f"⚠️  Alertas enviadas: {data.get('alertas_enviadas', 0)}")

def test_endpoint_simple():
    """Test del endpoint de prueba"""
    print()
    print("=" * 70)
    print("🧪 TEST: Endpoint de Prueba")
    print("=" * 70)
    print()
    
    app = create_app()
    
    with app.test_client() as client:
        response = client.get('/api/cron/test')
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        print(response.get_json())
        print()

def main():
    print()
    print("🚀 TESTING DE ENDPOINTS DE CRON")
    print("================================")
    print()
    
    # Tests
    test_endpoint_simple()
    test_generar_ordenes()
    test_verificar_alertas()
    
    print()
    print("=" * 70)
    print("✅ TESTS COMPLETADOS")
    print("=" * 70)

if __name__ == '__main__':
    main()
```

**Ejecutar:**
```bash
python scripts/test_cron_local.py
```

---

### **8. Script de Verificación** ⏱️ 20 min

**Archivo:** `scripts/verify_fase5.py` (NUEVO)

```python
"""
Verificación de Fase 5: Cloud Scheduler
"""
import os
import sys
from pathlib import Path

# Colores
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check(condition, message):
    """Helper para verificar condición"""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False

def main():
    print("=" * 70)
    print(f"{BLUE}🔍 VERIFICACIÓN FASE 5: CLOUD SCHEDULER{RESET}")
    print("=" * 70)
    print()
    
    checks_passed = 0
    total_checks = 0
    
    # 1. Archivo cron.py existe
    print(f"{BLUE}[1/12] Archivos Core{RESET}")
    total_checks += 1
    cron_route = Path('app/routes/cron.py')
    if check(cron_route.exists(), f"Existe {cron_route}"):
        checks_passed += 1
    print()
    
    # 2. Funciones definidas en cron.py
    if cron_route.exists():
        print(f"{BLUE}[2/12] Endpoints de Cron{RESET}")
        content = cron_route.read_text(encoding='utf-8')
        
        endpoints = [
            ('/api/cron/generar-ordenes-preventivas', 'Generación de órdenes'),
            ('/api/cron/verificar-alertas', 'Verificación de alertas'),
            ('/api/cron/test', 'Endpoint de prueba'),
        ]
        
        for endpoint, desc in endpoints:
            total_checks += 1
            # Buscar la ruta en el decorador
            if check(f"'{endpoint.split('/api/cron/')[1]}'" in content or f'"{endpoint.split("/api/cron/")[1]}"' in content, 
                    f"Endpoint {endpoint} ({desc})"):
                checks_passed += 1
        print()
    
    # 3. Función de protección de cron
    if cron_route.exists():
        print(f"{BLUE}[3/12] Seguridad{RESET}")
        content = cron_route.read_text(encoding='utf-8')
        
        total_checks += 1
        if check('X-Appengine-Cron' in content, "Verificación de header X-Appengine-Cron"):
            checks_passed += 1
        
        total_checks += 1
        if check('is_valid_cron_request' in content, "Función is_valid_cron_request() definida"):
            checks_passed += 1
        print()
    
    # 4. Blueprint registrado en factory
    print(f"{BLUE}[4/12] Integración{RESET}")
    factory_path = Path('app/factory.py')
    if factory_path.exists():
        content = factory_path.read_text(encoding='utf-8')
        
        total_checks += 1
        if check('from app.routes.cron import cron_bp' in content or 'cron_bp' in content, 
                "Blueprint de cron importado en factory"):
            checks_passed += 1
        
        total_checks += 1
        if check('register_blueprint(cron_bp)' in content, "Blueprint registrado"):
            checks_passed += 1
    print()
    
    # 5. Archivo cron.yaml existe
    print(f"{BLUE}[5/12] Configuración GCP{RESET}")
    total_checks += 1
    cron_yaml = Path('cron.yaml')
    if check(cron_yaml.exists(), f"Existe {cron_yaml}"):
        checks_passed += 1
        
        if cron_yaml.exists():
            content = cron_yaml.read_text(encoding='utf-8')
            
            total_checks += 1
            if check('/api/cron/generar-ordenes-preventivas' in content, 
                    "cron.yaml configura generación de órdenes"):
                checks_passed += 1
    print()
    
    # 6. Variables de entorno actualizadas
    print(f"{BLUE}[6/12] Variables de Entorno{RESET}")
    env_example = Path('.env.example')
    if env_example.exists():
        content = env_example.read_text(encoding='utf-8')
        
        total_checks += 1
        if check('ADMIN_EMAILS' in content, ".env.example contiene ADMIN_EMAILS"):
            checks_passed += 1
        
        total_checks += 1
        if check('SERVER_URL' in content, ".env.example contiene SERVER_URL"):
            checks_passed += 1
    print()
    
    # 7. Scripts de testing
    print(f"{BLUE}[7/12] Scripts{RESET}")
    total_checks += 1
    test_script = Path('scripts/test_cron_local.py')
    if check(test_script.exists(), f"Existe {test_script}"):
        checks_passed += 1
    print()
    
    # Resumen
    print("=" * 70)
    percentage = (checks_passed / total_checks * 100) if total_checks > 0 else 0
    
    if percentage == 100:
        print(f"{GREEN}✅ FASE 5 COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    elif percentage >= 80:
        print(f"{YELLOW}⚠️  FASE 5 CASI COMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    else:
        print(f"{RED}❌ FASE 5 INCOMPLETA: {checks_passed}/{total_checks} checks ({percentage:.1f}%){RESET}")
    
    print("=" * 70)
    print()
    
    if percentage >= 80:
        print(f"{GREEN}✅ Implementación completada{RESET}")
        print()
        print("📋 Próximos pasos para activar en producción:")
        print("   1. Asegurar que Flask-Mail está configurado")
        print("   2. Deploy a App Engine:")
        print(f"      {BLUE}gcloud app deploy{RESET}")
        print("   3. Deploy cron jobs:")
        print(f"      {BLUE}gcloud app deploy cron.yaml{RESET}")
        print("   4. Verificar en GCP Console > App Engine > Cron jobs")
        print()
    
    return 0 if percentage == 100 else 1

if __name__ == '__main__':
    sys.exit(main())
```

---

### **9. Instalar Flask-Mail (si no está)** ⏱️ 5 min

```bash
pip install Flask-Mail==0.9.1
pip freeze > requirements.txt
```

---

### **10. Documentación** ⏱️ 20 min

**README de Cron Jobs:** Agregar sección a README.md o crear archivo aparte

```markdown
## 🤖 Automatización con Cloud Scheduler

### Tareas Programadas

El sistema incluye tareas automáticas ejecutadas por Google Cloud Scheduler:

#### 1. Generación de Órdenes Preventivas
- **Frecuencia:** Diaria a las 00:00 AM
- **Endpoint:** `/api/cron/generar-ordenes-preventivas`
- **Función:**
  - Revisa planes de mantenimiento vencidos
  - Genera órdenes de trabajo automáticamente
  - Asigna técnico responsable
  - Envía notificaciones por email
  - Actualiza próxima fecha de ejecución

#### 2. Verificación de Alertas
- **Frecuencia:** Semanal (lunes 08:00 AM)
- **Endpoint:** `/api/cron/verificar-alertas`
- **Función:**
  - Identifica activos sin mantenimiento en 90+ días
  - Envía alertas a administradores

### Testing Local

```bash
# Probar endpoints de cron
python scripts/test_cron_local.py

# Probar manualmente
curl http://localhost:5000/api/cron/test
```

### Deploy de Cron Jobs

```bash
# Deploy de la aplicación
gcloud app deploy

# Deploy de cron jobs
gcloud app deploy cron.yaml

# Ver cron jobs activos
gcloud app services list

# Ver logs de cron
gcloud app logs tail -s default
```

### Seguridad

Los endpoints de cron están protegidos con el header `X-Appengine-Cron`:
- Solo App Engine puede establecer este header
- Peticiones externas son rechazadas (403)
- En desarrollo, la protección está deshabilitada
```

---

## 📊 Checklist de Implementación

### **Código:**
- [ ] Crear `app/routes/cron.py`
- [ ] Registrar blueprint en `app/factory.py`
- [ ] Actualizar modelo `OrdenTrabajo` (relación con plan)
- [ ] Crear migración de BD
- [ ] Instalar Flask-Mail

### **Configuración:**
- [ ] Crear `cron.yaml`
- [ ] Actualizar `.env.example`
- [ ] Configurar variables ADMIN_EMAILS y SERVER_URL

### **Scripts:**
- [ ] Crear `scripts/test_cron_local.py`
- [ ] Crear `scripts/verify_fase5.py`

### **Testing:**
- [ ] Ejecutar `python scripts/test_cron_local.py`
- [ ] Ejecutar `python scripts/verify_fase5.py`
- [ ] Verificar generación de órdenes

### **Deploy (GCP):**
- [ ] Deploy app: `gcloud app deploy`
- [ ] Deploy cron: `gcloud app deploy cron.yaml`
- [ ] Verificar en GCP Console

---

## 🎯 Resultado Esperado

### **Antes de Fase 5:**
```
15/10/2025 - Plan de mantenimiento vencido
↓
❌ Requiere intervención manual
↓
Usuario crea orden manualmente
```

### **Después de Fase 5:**
```
00:00 AM cada día - Cloud Scheduler ejecuta
↓
✅ Sistema detecta planes vencidos automáticamente
↓
✅ Genera órdenes de trabajo
↓
✅ Asigna técnicos
↓
✅ Envía notificaciones por email
↓
✅ Actualiza próxima fecha
```

---

## ⏱️ Timeline

| Tarea | Tiempo | Acumulado |
|-------|--------|-----------|
| Crear endpoint cron | 45 min | 45 min |
| Registrar blueprint | 5 min | 50 min |
| Actualizar modelo | 10 min | 1h |
| Migración BD | 10 min | 1h 10min |
| Configurar cron.yaml | 15 min | 1h 25min |
| Variables entorno | 5 min | 1h 30min |
| Script testing | 30 min | 2h |
| Script verificación | 20 min | 2h 20min |
| Instalar Flask-Mail | 5 min | 2h 25min |
| Documentación | 20 min | 2h 45min |
| **TOTAL** | **2h 45min** | |

---

## 🚀 Comenzar

**¿Listo para empezar Fase 5?** 🚀

Responde con:
- **"sí"** → Comenzamos implementación
- **"plan"** → Solo quiero ver el plan sin implementar aún
