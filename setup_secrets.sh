# Configuración de Secret Manager para GMAO
# Ejecutar estos comandos para configurar los secrets en GCP

# 1. Crear secrets
gcloud secrets create gmao-secret-key --data-file=/dev/stdin <<< "tu_clave_secreta_muy_segura_para_gcp_2025"
gcloud secrets create gmao-db-password --data-file=/dev/stdin <<< "tu_password_seguro_para_db"
gcloud secrets create gmao-openai-key --data-file=/dev/stdin <<< "tu_clave_openai_api"

# 2. Otorgar acceso al servicio de App Engine
gcloud secrets add-iam-policy-binding gmao-secret-key \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmao-db-password \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gmao-openai-key \
    --member="serviceAccount:gmao-sistema@appspot.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# 3. Para acceder desde la aplicación (en factory.py):
# from google.cloud import secretmanager
# client = secretmanager.SecretManagerServiceClient()
# secret_key = client.access_secret_version(request={"name": "projects/PROJECT_ID/secrets/gmao-secret-key/versions/latest"}).payload.data.decode("UTF-8")