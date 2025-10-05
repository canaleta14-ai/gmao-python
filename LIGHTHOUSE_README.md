# 🚀 Scripts de Auditoría Lighthouse - Sistema GMAO

## 📋 Descripción

Scripts automatizados para ejecutar auditorías de Google Lighthouse en el sistema GMAO, analizando:
- ⚡ **Performance** (Rendimiento)
- ♿ **Accessibility** (Accesibilidad)
- ✅ **Best Practices** (Mejores Prácticas)
- 🔍 **SEO** (Optimización para Motores de Búsqueda)

---

## 📦 Requisitos Previos

### 1. Node.js y npm

Lighthouse requiere Node.js instalado.

**Verificar instalación**:
```powershell
node --version
npm --version
```

**Si no están instalados**:
1. Descargar desde: https://nodejs.org/
2. Ejecutar el instalador
3. Reiniciar PowerShell
4. Verificar instalación con comandos anteriores

### 2. Lighthouse CLI

**El script instala Lighthouse automáticamente**, pero también puedes instalarlo manualmente:

```powershell
npm install -g lighthouse
```

**Verificar instalación**:
```powershell
lighthouse --version
```

---

## 🎯 Scripts Disponibles

### 1. `lighthouse_audit.ps1` - Auditoría Completa ⭐ RECOMENDADO

**Características**:
- ✅ Análisis Mobile y Desktop
- ✅ Reportes HTML visuales
- ✅ Archivos JSON para análisis
- ✅ Resumen en pantalla con puntuaciones
- ✅ Resumen guardado en archivo TXT
- ✅ Barras de progreso visuales
- ✅ Recomendaciones automáticas
- ✅ Opción de abrir reportes al finalizar

**Ejecutar**:
```powershell
powershell -ExecutionPolicy Bypass -File .\lighthouse_audit.ps1
```

**Duración**: 3-4 minutos (ambos análisis)

**Archivos generados** (en carpeta `lighthouse-reports/`):
```
lighthouse-reports/
├── gmao-lighthouse_mobile_20251002_223000.html
├── gmao-lighthouse_mobile_20251002_223000.json
├── gmao-lighthouse_desktop_20251002_223000.html
├── gmao-lighthouse_desktop_20251002_223000.json
└── lighthouse_summary_20251002_223000.txt
```

---

### 2. `lighthouse_quick.ps1` - Auditoría Rápida ⚡

**Características**:
- ✅ Solo análisis Mobile
- ✅ Reporte HTML
- ✅ Puntuaciones en consola
- ✅ Abre reporte automáticamente
- ⚡ Más rápido

**Ejecutar**:
```powershell
powershell -ExecutionPolicy Bypass -File .\lighthouse_quick.ps1
```

**Duración**: 1-2 minutos

**Archivos generados** (en directorio actual):
```
lighthouse-report-20251002-223000.html
lighthouse-report-20251002-223000.json
```

---

## 📊 Interpretación de Resultados

### Puntuaciones

| Puntuación | Estado | Color | Acción |
|-----------|--------|-------|--------|
| 90-100 | ✅ Excelente | Verde | Mantener |
| 50-89 | ⚠️ Mejorable | Amarillo | Optimizar |
| 0-49 | ❌ Pobre | Rojo | Acción urgente |

### Categorías

#### ⚡ Performance (Rendimiento)
**Métricas clave**:
- **FCP** (First Contentful Paint): < 1.8s
- **LCP** (Largest Contentful Paint): < 2.5s
- **TBT** (Total Blocking Time): < 200ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **Speed Index**: < 3.4s

**Si < 80**:
- Optimizar imágenes (lazy loading, WebP)
- Minificar CSS/JS
- Habilitar caché del navegador
- Reducir JavaScript no utilizado
- Usar CDN para assets

#### ♿ Accessibility (Accesibilidad)
**Aspectos evaluados**:
- Labels en inputs
- Contraste de colores (WCAG AA: 4.5:1)
- Alt text en imágenes
- ARIA labels en elementos interactivos
- Navegación con teclado

**Si < 90**:
- Agregar labels explícitos a todos los inputs
- Mejorar contraste de colores
- Añadir alt text descriptivo
- Implementar ARIA labels
- Probar navegación solo con teclado

#### ✅ Best Practices (Mejores Prácticas)
**Verifica**:
- HTTPS habilitado
- Bibliotecas actualizadas
- Console errors
- Security headers
- Imágenes con aspect ratio

**Si < 80**:
- Actualizar dependencias
- Configurar security headers
- Resolver errores de consola
- Usar HTTPS para todos los recursos

#### 🔍 SEO
**Factores**:
- Meta tags (title, description)
- Viewport meta tag
- Robots.txt
- Links crawleables
- Structured data

**Si < 90**:
- Agregar meta description
- Optimizar title tags
- Crear sitemap.xml
- Implementar Open Graph tags

---

## 📈 Ejemplo de Salida

```
============================================================================
  RESULTADOS DEL ANALISIS
============================================================================

  MOBILE (Smartphone)
  ──────────────────────────────────────────────────────────────────────
  Performance:    88/100  ████████░░
  Accessibility:  95/100  █████████░
  Best Practices: 92/100  █████████░
  SEO:            100/100 ██████████

  DESKTOP (Ordenador)
  ──────────────────────────────────────────────────────────────────────
  Performance:    98/100  █████████░
  Accessibility:  95/100  █████████░
  Best Practices: 92/100  █████████░
  SEO:            100/100 ██████████

============================================================================

ESTADO MOBILE: BUENO - Algunas mejoras recomendadas

RECOMENDACIONES MOBILE:
  - Performance: Optimizar imagenes, lazy loading, minificar CSS/JS

ARCHIVOS GENERADOS:
  Mobile:
    - HTML: .\lighthouse-reports\gmao-lighthouse_mobile_20251002_223000.html
    - JSON: .\lighthouse-reports\gmao-lighthouse_mobile_20251002_223000.json
  Desktop:
    - HTML: .\lighthouse-reports\gmao-lighthouse_desktop_20251002_223000.html
    - JSON: .\lighthouse-reports\gmao-lighthouse_desktop_20251002_223000.json
```

---

## 🔧 Solución de Problemas

### Error: "Lighthouse no encontrado"

**Solución 1**: Instalar manualmente
```powershell
npm install -g lighthouse
```

**Solución 2**: Verificar PATH de npm
```powershell
npm config get prefix
# Agregar al PATH: C:\Users\TuUsuario\AppData\Roaming\npm
```

### Error: "No se puede ejecutar scripts"

**Solución**: Permitir ejecución de scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Error: "npm no reconocido"

**Solución**: Instalar Node.js
1. Ir a https://nodejs.org/
2. Descargar versión LTS
3. Instalar
4. Reiniciar PowerShell

### Chrome no encontrado

**Solución**: Especificar ruta de Chrome
```powershell
# Editar script, agregar:
--chrome-flags="--chrome-path=C:\Program Files\Google\Chrome\Application\chrome.exe"
```

---

## 📅 Frecuencia Recomendada

| Frecuencia | Cuándo | Por qué |
|-----------|--------|---------|
| **Después de cada deploy** | Siempre | Detectar regresiones |
| **Semanal** | Lunes | Seguimiento continuo |
| **Antes de releases** | Siempre | Validación de calidad |
| **Tras optimizaciones** | Inmediato | Medir impacto |

---

## 📊 Tracking de Progreso

### Crear baseline inicial:
```powershell
# Primera ejecución
.\lighthouse_audit.ps1

# Renombrar reportes como baseline
Move-Item lighthouse-reports\gmao-lighthouse_mobile_*.html lighthouse-reports\baseline_mobile.html
Move-Item lighthouse-reports\gmao-lighthouse_desktop_*.html lighthouse-reports\baseline_desktop.html
```

### Comparar con baseline:
```powershell
# Ejecutar nueva auditoria
.\lighthouse_audit.ps1

# Abrir ambos reportes y comparar puntuaciones
```

---

## 🎯 Objetivos Recomendados

### Fase 1 (Actual)
- ✅ Performance Mobile: > 80
- ✅ Performance Desktop: > 90
- ✅ Accessibility: > 90
- ✅ Best Practices: > 80
- ✅ SEO: > 90

### Fase 2 (Optimización)
- 🎯 Performance Mobile: > 90
- 🎯 Performance Desktop: > 95
- 🎯 Accessibility: > 95
- 🎯 Best Practices: > 90
- 🎯 SEO: > 95

### Fase 3 (Excelencia)
- 🏆 Todas las métricas: > 95
- 🏆 Core Web Vitals: Todas en verde
- 🏆 PWA Ready
- 🏆 Certificación Google Lighthouse

---

## 📝 Exportar Resultados

### Crear reporte ejecutivo (manual):
1. Abrir reporte HTML
2. Click en "Export Report" (esquina superior derecha)
3. Seleccionar formato (PDF, CSV, JSON)
4. Guardar en carpeta de documentación

### Integración CI/CD (futuro):
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse
        run: |
          npm install -g @lhci/cli
          lhci autorun
```

---

## 🔗 Recursos Adicionales

- [Documentación Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Core Web Vitals](https://web.dev/vitals/)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Web.dev Metrics](https://web.dev/metrics/)

---

## 📞 Soporte

Si encuentras problemas:
1. Verificar requisitos previos
2. Revisar sección "Solución de Problemas"
3. Consultar logs de error
4. Ejecutar en modo verbose: `lighthouse --verbose`

---

## 📄 Changelog

### v1.0 (2025-10-02)
- ✅ Script completo con Mobile + Desktop
- ✅ Script rápido solo Mobile
- ✅ Extracción automática de puntuaciones
- ✅ Reportes HTML y JSON
- ✅ Resumen en consola y archivo
- ✅ Recomendaciones automáticas
- ✅ Instalación automática de Lighthouse

---

**¿Listo para empezar?** 🚀

```powershell
# Ejecución rápida (recomendada para primera vez)
.\lighthouse_quick.ps1

# Ejecución completa (Mobile + Desktop)
.\lighthouse_audit.ps1
```

---

**Fecha de creación**: 2 de octubre de 2025  
**Versión**: 1.0  
**Autor**: Sistema GMAO  
**URL**: https://gmao-sistema-2025.ew.r.appspot.com
