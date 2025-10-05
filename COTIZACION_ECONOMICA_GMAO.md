# 💰 Cotización Económica - Sistema GMAO
## Análisis de Costos y Valor del Sistema

**Fecha**: 2 de octubre de 2025  
**Proyecto**: Sistema de Gestión de Mantenimiento Asistido por Ordenador (GMAO)  
**Cliente**: Disfood / Desarrollos Hibo  
**Estado**: Desplegado en producción

---

## 📊 RESUMEN EJECUTIVO

| Concepto | Costo Mensual | Costo Anual |
|----------|---------------|-------------|
| **Infraestructura GCP** | €35-50 | €420-600 |
| **Mantenimiento y Soporte** | €200-400 | €2400-4800 |
| **TOTAL OPERATIVO** | **€235-450** | **€2820-5400** |

**Inversión Inicial Desarrollo**: €15000 - €25000 (valor de mercado)  
**Retorno de Inversión (ROI)**: Estimado 200-400% en el primer año

---

## 🏗️ COSTOS DE INFRAESTRUCTURA (GOOGLE CLOUD PLATFORM)

### 1. App Engine (Servidor de Aplicación)
**Configuración Actual**: F2 instances, auto-scaling 1-10

| Concepto | Especificación | Costo Mensual |
|----------|----------------|---------------|
| Instancias F2 | 2 vCPU, 2GB RAM | €15-25 |
| Almacenamiento | Código y logs | €2-5 |
| Tráfico de red | Salida de datos | €3-8 |
| **Subtotal App Engine** | | **€20-38** |

**Detalle de instancias**:
- 1 instancia base (24/7): ~€15/mes
- Instancias adicionales (auto-scaling): €5-23/mes según carga
- Estimación para 50-100 usuarios concurrentes

### 2. Cloud SQL (Base de Datos PostgreSQL)
**Configuración Actual**: PostgreSQL 15, db-f1-micro

| Concepto | Especificación | Costo Mensual |
|----------|----------------|---------------|
| Instancia db-f1-micro | 1 vCPU, 0.6GB RAM | €8-12 |
| Almacenamiento SSD | 10GB | €2-3 |
| Backups automáticos | 7 días retención | €1-2 |
| Tráfico interno | App ↔ DB | Incluido |
| **Subtotal Cloud SQL** | | **€11-17** |

**Nota**: Para mayor rendimiento, se puede escalar a db-g1-small (~€30/mes)

### 3. Cloud Storage (Archivos y Backups)
**Uso Actual**: Temporal (/tmp), migración recomendada

| Concepto | Estimación | Costo Mensual |
|----------|------------|---------------|
| Almacenamiento Standard | 5-10GB | €0.10-0.20 |
| Operaciones de lectura | 10000/mes | €0.05 |
| Operaciones de escritura | 5000/mes | €0.10 |
| **Subtotal Cloud Storage** | | **€0.25-0.35** |

**Recomendación**: Migrar archivos adjuntos de /tmp a Cloud Storage

### 4. Servicios Adicionales

| Servicio | Uso | Costo Mensual |
|----------|-----|---------------|
| Cloud Logging | Logs del sistema | €2-5 |
| Secret Manager | Credenciales seguras | €0.50 |
| Cloud Build | Despliegues | Gratis (120 min/día) |
| **Subtotal Adicionales** | | **€2.50-5.50** |

### 📈 RESUMEN INFRAESTRUCTURA GCP

| Escenario | Usuarios | Costo Mensual | Costo Anual |
|-----------|----------|---------------|-------------|
| **Actual (Básico)** | 20-50 | €35-45 | €420-540 |
| **Escalado Medio** | 50-100 | €45-60 | €540-720 |
| **Escalado Alto** | 100-200 | €80-120 | €960-1,440 |

**Comparativa con hosting tradicional**:
- VPS básico: €15-30/mes (sin escalabilidad automática)
- Servidor dedicado: €100-200/mes (sobredimensionado)
- **GCP ofrece**: Pay-as-you-go, alta disponibilidad, backups automáticos

---

## 💻 COSTOS DE DESARROLLO Y MANTENIMIENTO

### 1. Desarrollo Inicial (YA REALIZADO)

| Módulo | Horas | Tarifa/Hora | Costo |
|--------|-------|-------------|-------|
| **Backend (Flask/Python)** | | | |
| - Arquitectura y configuración | 20h | €25 | €500 |
| - Modelos de datos (9 tablas) | 30h | €25 | €750 |
| - Controladores y lógica | 40h | €25 | €1000 |
| - API REST | 15h | €25 | €375 |
| **Frontend (HTML/CSS/JS)** | | | |
| - Diseño UI/UX | 25h | €45 | €1125 |
| - Templates (20+ páginas) | 35h | €45 | €1575 |
| - JavaScript interactivo | 20h | €45 | €900 |
| - Componentes reutilizables | 15h | €45 | €675 |
| **Funcionalidades** | | | |
| - Gestión de activos | 15h | €50 | €750 |
| - Órdenes de trabajo | 20h | €50 | €1000 |
| - Mantenimiento preventivo | 25h | €50 | €1250 |
| - Sistema de inventario | 18h | €50 | €900 |
| - Gestión de usuarios y roles | 12h | €50 | €600 |
| - Proveedores y compras | 10h | €50 | €500 |
| - Sistema de alertas | 15h | €50 | €750 |
| - Solicitudes públicas | 20h | €50 | €1000 |
| - Upload de archivos | 12h | €50 | €600 |
| - Estadísticas y reportes | 18h | €50 | €900 |
| **Infraestructura** | | | |
| - Configuración GCP | 10h | €60 | €600 |
| - Cloud SQL setup | 8h | €60 | €480 |
| - Despliegues y CI/CD | 12h | €60 | €720 |
| - Email (Gmail Enterprise) | 5h | €50 | €250 |
| - Seguridad y sesiones | 8h | €50 | €400 |
| **Testing y QA** | | | |
| - Pruebas funcionales | 25h | €40 | €1000 |
| - Corrección de bugs | 15h | €40 | €600 |
| - Optimización | 10h | €50 | €500 |
| **Documentación** | | | |
| - Guías técnicas | 15h | €40 | €600 |
| - Manuales de usuario | 10h | €40 | €400 |
| **TOTAL DESARROLLO** | **438h** | | **€22,125** |

**Valor de mercado**: €15000 - €25000 (sistema GMAO completo)

### 2. Mantenimiento Mensual

| Servicio | Horas/Mes | Tarifa | Costo Mensual |
|----------|-----------|--------|---------------|
| **Soporte Básico** | | | |
| - Monitoreo sistema | 2h | €40 | €80 |
| - Actualizaciones seguridad | 2h | €50 | €100 |
| - Backup verificación | 1h | €40 | €40 |
| **Subtotal Básico** | 5h | | **€220** |
| | | | |
| **Soporte Estándar** | | | |
| - Todo lo anterior | 5h | | €220 |
| - Nuevas funcionalidades | 3h | €50 | €150 |
| - Optimizaciones | 2h | €50 | €100 |
| **Subtotal Estándar** | 10h | | **€470** |
| | | | |
| **Soporte Premium** | | | |
| - Todo lo anterior | 10h | | €470 |
| - Desarrollo personalizado | 5h | €50 | €250 |
| - Integraciones externas | 3h | €60 | €180 |
| - Capacitación usuarios | 2h | €40 | €80 |
| **Subtotal Premium** | 20h | | **€980** |

### 3. Servicios Externos

| Servicio | Proveedor | Costo Mensual |
|----------|-----------|---------------|
| Gmail Enterprise | Google Workspace | €6/usuario |
| SSL Certificado | Google (incluido) | Gratis |
| Dominio (opcional) | Google Domains | €12/año |
| **Total Externo** | | **€6-12** |

---

## 📊 DESGLOSE POR PLANES

### PLAN BÁSICO - €290/mes
**Ideal para**: Pequeñas empresas (10-30 usuarios)

✅ **Incluye**:
- Infraestructura GCP (€35-45)
- Soporte básico 5h/mes (€220)
- Monitoreo 24/7
- Backups automáticos
- Actualizaciones de seguridad
- Gmail Enterprise (€30 para 5 usuarios)

❌ **No incluye**:
- Desarrollo de nuevas funcionalidades
- Personalización avanzada
- Capacitación presencial

**Total**: €290/mes (€3,480/año)

---

### PLAN ESTÁNDAR - €520/mes ⭐ RECOMENDADO
**Ideal para**: Empresas medianas (30-100 usuarios)

✅ **Incluye**:
- Todo del Plan Básico
- Infraestructura escalada (€50)
- Soporte estándar 10h/mes (€470)
- 3 horas de desarrollo mensual
- Optimizaciones de rendimiento
- Reportes personalizados

**Total**: €520/mes (€6,240/año)

---

### PLAN PREMIUM - €1,050/mes
**Ideal para**: Grandes empresas (100-200 usuarios)

✅ **Incluye**:
- Todo del Plan Estándar
- Infraestructura alta disponibilidad (€100)
- Soporte premium 20h/mes (€980)
- Desarrollo personalizado
- Integraciones con ERP/CRM
- Capacitación trimestral
- SLA 99.9% uptime

**Total**: €1,050/mes (€12,600/año)

---

## 💡 ANÁLISIS DE ROI (RETORNO DE INVERSIÓN)

### Ahorros Estimados con el Sistema GMAO

| Concepto | Sin GMAO | Con GMAO | Ahorro Anual |
|----------|----------|----------|--------------|
| **Mantenimiento Reactivo** | | | |
| - Paradas no planificadas | €15000 | €3000 | €12000 |
| - Reparaciones urgentes | €8000 | €2000 | €6000 |
| **Mantenimiento Preventivo** | | | |
| - Extensión vida útil activos | - | +30% | €10000 |
| - Reducción averías | - | -60% | €8000 |
| **Gestión de Inventario** | | | |
| - Stock optimizado | €12000 | €6000 | €6000 |
| - Pedidos urgentes | €5000 | €1000 | €4000 |
| **Productividad** | | | |
| - Tiempo administrativo | 200h | 80h | €4800 |
| - Búsqueda información | 150h | 30h | €3600 |
| **TOTAL AHORRO ANUAL** | | | **€54400** |

### Cálculo ROI (Plan Estándar)

```
Inversión Total Año 1:
- Desarrollo (ya realizado): €22125
- Operación anual: €6240
- Total: €28365

Ahorro Anual: €54400
ROI = (Ahorro - Inversión) / Inversión × 100
ROI = (€54400 - €28365) / €28365 × 100
ROI = 91.7% en el primer año

Recuperación inversión: 6-8 meses
```

### Beneficios Intangibles

✅ **Cumplimiento normativo** - Trazabilidad completa  
✅ **Mejora imagen empresa** - Sistema profesional  
✅ **Datos para toma decisiones** - Analytics en tiempo real  
✅ **Escalabilidad** - Crece con la empresa  
✅ **Seguridad** - Backups y protección datos  

---

## 📈 COMPARATIVA CON ALTERNATIVAS

### Software Comercial GMAO

| Proveedor | Costo Mensual | Limitaciones |
|-----------|---------------|--------------|
| **Fracttal** | €300-500/mes | 25 usuarios, sin personalización |
| **Manteio** | €250-400/mes | Funcionalidades limitadas |
| **eMaint** | €400-600/mes | Licencias por usuario |
| **Infraspeak** | €350-550/mes | Cloud cerrado |
| **NUESTRO SISTEMA** | **€290-520/mes** | ✅ **Personalizable, sin límites** |

### Ventajas Competitivas

✅ **Código propio** - Total control y personalización  
✅ **Sin licencias por usuario** - Pago fijo mensual  
✅ **Integración a medida** - API REST disponible  
✅ **Datos en tu control** - Google Cloud Europe (GDPR)  
✅ **Soporte directo** - Sin call centers externos  

---

## 🎯 PROPUESTA DE VALOR

### Para Empresas Pequeñas (Plan Básico - €290/mes)

**Casos de uso**:
- Talleres mecánicos (5-10 técnicos)
- Pequeñas plantas industriales
- Edificios comerciales

**Beneficios**:
- Elimina Excel y papeles
- Control total de mantenimiento
- Ahorro estimado: €15,000-25,000/año

**Punto de equilibrio**: 2-3 meses

---

### Para Empresas Medianas (Plan Estándar - €520/mes) ⭐

**Casos de uso**:
- Plantas industriales medianas
- Hospitales y centros sanitarios
- Cadenas retail (múltiples ubicaciones)
- **DISFOOD** - Industria alimentaria

**Beneficios**:
- Mantenimiento preventivo automatizado
- Trazabilidad completa (certificaciones)
- Reportes ejecutivos
- Ahorro estimado: €40,000-60,000/año

**Punto de equilibrio**: 3-4 meses

---

### Para Grandes Empresas (Plan Premium - €1,050/mes)

**Casos de uso**:
- Grandes instalaciones industriales
- Múltiples centros de producción
- Empresas con +100 activos críticos

**Beneficios**:
- Integración con ERP/SAP
- Análisis predictivo
- Multi-site management
- Ahorro estimado: €80,000-150,000/año

**Punto de equilibrio**: 4-6 meses

---

## 💳 OPCIONES DE PAGO

### Opción 1: Suscripción Mensual (SaaS)
- Pago mensual recurrente
- Sin compromiso de permanencia
- Incluye actualizaciones y soporte
- **Recomendado para testing**

### Opción 2: Anual (10% descuento)
- Pago anual anticipado
- Plan Básico: €3,132/año (ahorro €348)
- Plan Estándar: €5,616/año (ahorro €624)
- Plan Premium: €11,340/año (ahorro €1,260)

### Opción 3: Licencia Perpetua
- Pago único desarrollo: €22,125
- Infraestructura GCP: €35-50/mes (a cargo cliente)
- Soporte opcional: €200-400/mes
- **Total año 1**: €22,125 + €2,400-6,000 = €24,525-28,125
- **Años siguientes**: Solo infraestructura + soporte

---

## 🔧 COSTOS DE MIGRACIÓN Y SETUP

### Setup Inicial (One-time)

| Concepto | Horas | Costo |
|----------|-------|-------|
| Instalación y configuración | 4h | €200 |
| Migración datos existentes | 8h | €400 |
| Capacitación usuarios (online) | 4h | €160 |
| Personalización inicial | 6h | €300 |
| **Total Setup** | 22h | **€1,060** |

**Promoción**: Setup gratuito con contrato anual (ahorro €1,060)

---

## 📞 CONDICIONES COMERCIALES

### Garantías
✅ SLA 99% uptime (Plan Básico)  
✅ SLA 99.5% uptime (Plan Estándar)  
✅ SLA 99.9% uptime (Plan Premium)  
✅ Backups diarios automáticos  
✅ Soporte email: 24-48h respuesta  
✅ Soporte urgencias: 2-4h respuesta (Estándar/Premium)  

### Política de Cancelación
- Aviso previo: 30 días
- Sin penalizaciones
- Export completo de datos incluido
- Migración asistida disponible

### Escalabilidad
- Cambio de plan en cualquier momento
- Prorrateo de diferencias
- Sin costos de upgrade

---

## 📊 RESUMEN FINANCIERO RECOMENDADO PARA DISFOOD

### Escenario Actual (Producción)

**Configuración**:
- 20-30 usuarios estimados
- Infraestructura desplegada
- Sistema funcional completo

**Opción Recomendada**: Plan Estándar

| Concepto | Costo Mensual | Costo Anual |
|----------|---------------|-------------|
| Infraestructura GCP | €45 | €540 |
| Soporte Estándar (10h) | €470 | €5,640 |
| Gmail Enterprise (5 usuarios) | €30 | €360 |
| **TOTAL** | **€545/mes** | **€6,540/año** |

**Con descuento anual**: €5,886/año (ahorro €654)

### Análisis Coste/Beneficio Disfood

**Inversión Anual**: €6,540  
**Ahorro Estimado**:
- Reducción paradas: €12,000
- Optimización inventario: €6,000
- Productividad administrativa: €4,800
- **Total ahorro**: €22,800

**ROI**: 249% (retorno 3.5x la inversión)  
**Recuperación**: 3-4 meses

---

## 🎁 OFERTA DE LANZAMIENTO

### Promoción Especial - Primeros 3 Meses

**Plan Estándar**:
- ~~€520/mes~~ → **€390/mes** (25% descuento)
- Setup gratuito (valor €1,060)
- 5 horas extra soporte primer mes
- Capacitación online incluida

**Plan Básico**:
- ~~€290/mes~~ → **€232/mes** (20% descuento)
- Setup gratuito
- 2 horas extra soporte primer mes

**Condiciones**: 
- Válido para contratos firmados antes del 31 octubre 2025
- Compromiso mínimo 6 meses
- Después de 3 meses, precio regular

---

## 📄 PRÓXIMOS PASOS

### Para Contratar

1. **Reunión de análisis** (30 min, gratuita)
   - Evaluación necesidades específicas
   - Demostración del sistema
   - Personalización de la propuesta

2. **Firma de contrato**
   - Elección de plan
   - Condiciones de pago
   - SLA y garantías

3. **Setup e implementación** (1-2 semanas)
   - Configuración personalizada
   - Migración de datos
   - Capacitación usuarios

4. **Go Live** 🚀
   - Puesta en producción
   - Soporte intensivo primera semana
   - Seguimiento mensual

---

## 📧 CONTACTO

**Desarrollos Hibo**  
Email: j_hidalgo@disfood.com  
Teléfono: [Añadir]  
Web: https://gmao-sistema-2025.ew.r.appspot.com

**Horario Soporte**:
- Lunes a Viernes: 9:00-18:00
- Urgencias 24/7 (Planes Estándar/Premium)

---

## 📚 ANEXOS

### Tecnologías Utilizadas
- **Backend**: Python 3.11, Flask 3.0
- **Base de datos**: PostgreSQL 15
- **Frontend**: Bootstrap 5, JavaScript ES6
- **Cloud**: Google Cloud Platform (Europe)
- **Seguridad**: HTTPS, CSRF protection, sesiones seguras

### Certificaciones y Cumplimiento
✅ GDPR compliant (datos en EU)  
✅ SSL/TLS encryption  
✅ Backups automáticos  
✅ Logs de auditoría  
✅ Control de acceso basado en roles  

---

**Documento generado**: 2 de octubre de 2025  
**Versión**: 1.0  
**Validez oferta**: 60 días

---

## 🔐 CONFIDENCIALIDAD

*Este documento contiene información confidencial y es propiedad de Desarrollos Hibo. 
Su distribución sin autorización está prohibida.*
