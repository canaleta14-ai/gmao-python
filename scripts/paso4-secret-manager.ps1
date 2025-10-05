# 🚀 COMANDOS PASO 4 - Secret Manager
# Ejecutar estos comandos cuando Cloud SQL esté listo

# ====================================
# 1. Crear los secretos
# ====================================

# Secret Key (Flask)
echo -n "Ri2CvW-tgBu8D96-i7HeH2Gj85FGGPl2YXQ0D4PLMyY" | gcloud secrets create secret-key --data-file=-

# Database Password (gmao-user)
echo -n "NbQt4EB*3gYjhu*25wemy73yr#IBXKm!" | gcloud secrets create db-password --data-file=-

# OpenAI API Key (opcional - solo si tienes)
# echo -n "sk-tu-api-key-aqui" | gcloud secrets create openai-api-key --data-file=-

# ====================================
# 2. Configurar permisos IAM
# ====================================

# Service Account de App Engine
$SERVICE_ACCOUNT = "gmao-sistema-2025@appspot.gserviceaccount.com"

# Permiso para secret-key
gcloud secrets add-iam-policy-binding secret-key `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/secretmanager.secretAccessor"

# Permiso para db-password
gcloud secrets add-iam-policy-binding db-password `
  --member="serviceAccount:$SERVICE_ACCOUNT" `
  --role="roles/secretmanager.secretAccessor"

# Permiso para openai-api-key (si lo creaste)
# gcloud secrets add-iam-policy-binding openai-api-key `
#   --member="serviceAccount:$SERVICE_ACCOUNT" `
#   --role="roles/secretmanager.secretAccessor"

# ====================================
# 3. Verificar que se crearon
# ====================================

gcloud secrets list

Write-Host "✅ Secret Manager configurado!" -ForegroundColor Green
