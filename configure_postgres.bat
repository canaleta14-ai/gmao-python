@echo off
REM Script para configurar PostgreSQL para desarrollo local
REM Detener PostgreSQL
net stop postgresql-x64-16

REM Modificar pg_hba.conf para permitir conexiones locales sin contraseña
echo # Configuración para desarrollo local >> "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
echo local   all             all                                     trust >> "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
echo host    all             all             127.0.0.1/32            trust >> "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"
echo host    all             all             ::1/128                 trust >> "C:\Program Files\PostgreSQL\16\data\pg_hba.conf"

REM Reiniciar PostgreSQL
net start postgresql-x64-16

echo PostgreSQL configurado para desarrollo local
pause