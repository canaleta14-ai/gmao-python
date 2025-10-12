# Configuración de CI/CD para GMAO Sistema

## Secrets Requeridos en GitHub

Para que los workflows de CI/CD funcionen correctamente, necesitas configurar los siguientes secrets en tu repositorio de GitHub:

### 1. Ir a Settings > Secrets and variables > Actions

### 2. Agregar los siguientes Repository secrets:

```
GCP_PROJECT_ID
- Valor: mantenimiento-470311

GCP_SA_KEY
- Valor: [Clave JSON completa de la service account de Google Cloud]
- Para obtener: gcloud iam service-accounts keys create key.json --iam-account=gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com
```

### 3. Variables de entorno adicionales (opcional):

```
FLASK_ENV=production
SECRET_KEY=[Clave secreta para producción]
DATABASE_URL=[URL de conexión a base de datos de producción]
```

## Service Account de Google Cloud

### Crear service account para CI/CD:

```bash
# Crear service account
gcloud iam service-accounts create gmao-ci-cd \
    --description="Service Account para CI/CD de GMAO" \
    --display-name="GMAO CI/CD"

# Asignar roles necesarios
gcloud projects add-iam-policy-binding mantenimiento-470311 \
    --member="serviceAccount:gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com" \
    --role="roles/appengine.appAdmin"

gcloud projects add-iam-policy-binding mantenimiento-470311 \
    --member="serviceAccount:gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding mantenimiento-470311 \
    --member="serviceAccount:gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

# Generar clave JSON
gcloud iam service-accounts keys create gmao-ci-cd-key.json \
    --iam-account=gmao-ci-cd@mantenimiento-470311.iam.gserviceaccount.com
```

## Configuración de Entornos

### Environment: production

Para deployments a producción, crear un environment llamado "production" en:
Settings > Environments > New environment

Configurar:

- Required reviewers (opcional): usuarios que deben aprobar deployments
- Wait timer (opcional): tiempo de espera antes del deployment
- Deployment branches: solo main

## Badges para README

Agregar estos badges al README.md:

```markdown
[![CI/CD Pipeline](https://github.com/TU_USUARIO/gmao-sistema/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/TU_USUARIO/gmao-sistema/actions/workflows/ci-cd.yml)
[![Tests Nocturnos](https://github.com/TU_USUARIO/gmao-sistema/actions/workflows/nightly-tests.yml/badge.svg)](https://github.com/TU_USUARIO/gmao-sistema/actions/workflows/nightly-tests.yml)
[![codecov](https://codecov.io/gh/TU_USUARIO/gmao-sistema/branch/main/graph/badge.svg)](https://codecov.io/gh/TU_USUARIO/gmao-sistema)
```

## Webhooks (Opcional)

Para notificaciones en Slack/Discord/Teams:

```yaml
- name: Notificar en Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    channel: "#deployments"
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
  if: always()
```

## Monitoring y Alertas

Los workflows incluyen:

1. **Tests automáticos** en cada push/PR
2. **Quality gates** (95% tests passing mínimo)
3. **Coverage reports** enviados a Codecov
4. **Security scanning** de dependencias
5. **Production monitoring** diario
6. **Automatic cleanup** de versiones antiguas

## Flujo de Branches

```
develop -> Staging deployment
main    -> Production deployment
```

### Para usar:

1. Desarrollo en feature branches
2. PR a develop -> Deploy automático a staging
3. PR de develop a main -> Deploy a producción (con aprobación)

## Troubleshooting

### Error común: "Invalid service account key"

- Verificar que GCP_SA_KEY contenga la clave JSON completa
- Verificar que la service account tenga los permisos correctos

### Error: "App Engine application not found"

- Verificar que el proyecto tenga App Engine habilitado
- `gcloud app create --region=europe-west1`

### Tests fallando en CI

- Verificar que DATABASE_URL apunte a PostgreSQL en CI
- Verificar variables de entorno específicas para testing
