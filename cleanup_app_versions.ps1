# Script para eliminar todas las versiones de App Engine excepto madrid-fix44
Write-Host "Eliminando versiones antiguas de App Engine..."

# Lista de todas las versiones a eliminar (todas excepto madrid-fix44)
$versions = @(
    "20251007t192338", "20251007t200221", "20251007t203010", "20251008t002632", "20251008t003236",
    "20251008t003413", "20251008t004144", "20251008t004803", "20251008t010510", "20251008t010701",
    "20251008t010901", "20251008t011201", "20251008t011402", "20251008t011550", "20251008t011957",
    "20251008t090443", "20251008t090902", "20251008t091233", "20251008t091410", "20251008t091819",
    "20251008t092348", "20251008t092529", "20251008t092713", "20251008t093529", "20251008t093938",
    "20251008t173626", "20251008t174353", "20251008t175033", "20251009t104022", "20251009t104519",
    "20251009t110717", "20251009t111500", "20251009t112016", "20251009t114032", "20251009t114445",
    "20251009t115553", "20251009t115856", "20251009t121409", "20251009t121731", "20251009t122140",
    "20251009t122602", "20251009t140531", "20251009t141611", "20251009t142019", "20251009t144939",
    "20251009t145645", "20251009t145924", "20251009t150321", "20251009t150640", "20251009t150957",
    "20251009t151314", "20251009t151751", "20251009t152028", "20251009t152417", "20251009t152652",
    "20251009t153125", "20251009t154001", "20251009t154849", "20251009t155345", "20251009t160641",
    "20251009t161731", "20251009t162512", "20251009t163156", "20251009t165518", "20251009t170829",
    "20251009t171123", "20251011t084825", "20251011t085723", "20251011t090432", "20251011t091105",
    "20251011t091402", "20251011t091917", "clean", "fix-activos-csv", "fix-cloudsql-connector",
    "fix-cloudsql-region", "fix-csv-activos-v2", "fix-db-password", "fix-permissions", "fix-project-id",
    "madrid-fix", "madrid-fix10", "madrid-fix11", "madrid-fix12", "madrid-fix13", "madrid-fix14",
    "madrid-fix15", "madrid-fix16", "madrid-fix17", "madrid-fix18", "madrid-fix19", "madrid-fix2",
    "madrid-fix20", "madrid-fix21", "madrid-fix22", "madrid-fix23", "madrid-fix24", "madrid-fix25",
    "madrid-fix26", "madrid-fix27", "madrid-fix28", "madrid-fix29", "madrid-fix3", "madrid-fix30",
    "madrid-fix31", "madrid-fix32", "madrid-fix33", "madrid-fix34", "madrid-fix35", "madrid-fix36",
    "madrid-fix37", "madrid-fix38", "madrid-fix39", "madrid-fix4", "madrid-fix40", "madrid-fix41",
    "madrid-fix42", "madrid-fix43", "madrid-fix5", "madrid-fix6", "madrid-fix7", "madrid-fix8",
    "madrid-fix9", "manuales-auth-fix-2025-10-07", "spain-madrid"
)

# Eliminar cada versión
foreach ($version in $versions) {
    try {
        Write-Host "Eliminando versión: $version"
        gcloud app versions delete $version --quiet
        Write-Host "✅ $version eliminada"
    }
    catch {
        Write-Host "❌ Error eliminando $version : $_"
    }
}

Write-Host "Limpieza de versiones completada."