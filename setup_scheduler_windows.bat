@echo off
echo ===============================================
echo    CONFIGURACION DEL SCHEDULER DE ORDENES
echo         Mantenimiento Automatico GMAO
echo ===============================================
echo.

echo [1/5] Instalando dependencias necesarias...
pip install APScheduler schedule

echo.
echo [2/5] Creando directorio de logs...
if not exist "logs" mkdir logs

echo.
echo [3/5] Creando servicio de Windows...

:: Crear archivo batch para el servicio
echo @echo off > run_scheduler.bat
echo cd /d "%~dp0" >> run_scheduler.bat
echo python scheduler_simple.py >> run_scheduler.bat

:: Crear script de instalacion del servicio
echo import win32serviceutil > install_service.py
echo import win32service >> install_service.py
echo import win32event >> install_service.py
echo import os >> install_service.py
echo import sys >> install_service.py
echo import subprocess >> install_service.py
echo. >> install_service.py
echo class GMAOSchedulerService(win32serviceutil.ServiceFramework): >> install_service.py
echo     _svc_name_ = "GMAOScheduler" >> install_service.py
echo     _svc_display_name_ = "GMAO Ordenes Scheduler" >> install_service.py
echo     _svc_description_ = "Servicio para generar ordenes automaticas a las 11:00 AM" >> install_service.py
echo. >> install_service.py
echo     def __init__(self, args): >> install_service.py
echo         win32serviceutil.ServiceFramework.__init__(self, args) >> install_service.py
echo         self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) >> install_service.py
echo         self.running = True >> install_service.py
echo. >> install_service.py
echo     def SvcStop(self): >> install_service.py
echo         self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) >> install_service.py
echo         win32event.SetEvent(self.hWaitStop) >> install_service.py
echo         self.running = False >> install_service.py
echo. >> install_service.py
echo     def SvcDoRun(self): >> install_service.py
echo         import time >> install_service.py
echo         script_dir = os.path.dirname(os.path.abspath(__file__)) >> install_service.py
echo         os.chdir(script_dir) >> install_service.py
echo         while self.running: >> install_service.py
echo             try: >> install_service.py
echo                 subprocess.run([sys.executable, "scheduler_simple.py"], cwd=script_dir) >> install_service.py
echo             except: >> install_service.py
echo                 time.sleep(60) >> install_service.py
echo. >> install_service.py
echo if __name__ == '__main__': >> install_service.py
echo     win32serviceutil.HandleCommandLine(GMAOSchedulerService) >> install_service.py

echo.
echo [4/5] Creando Task Scheduler (Programador de tareas de Windows)...

:: Crear XML para task scheduler
echo ^<?xml version="1.0" encoding="UTF-16"?^> > scheduler_task.xml
echo ^<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> scheduler_task.xml
echo   ^<RegistrationInfo^> >> scheduler_task.xml
echo     ^<Description^>Genera ordenes de trabajo automaticamente todos los dias a las 11:00 AM^</Description^> >> scheduler_task.xml
echo     ^<Author^>GMAO System^</Author^> >> scheduler_task.xml
echo   ^</RegistrationInfo^> >> scheduler_task.xml
echo   ^<Triggers^> >> scheduler_task.xml
echo     ^<CalendarTrigger^> >> scheduler_task.xml
echo       ^<StartBoundary^>2025-09-29T11:00:00^</StartBoundary^> >> scheduler_task.xml
echo       ^<Enabled^>true^</Enabled^> >> scheduler_task.xml
echo       ^<ScheduleByDay^> >> scheduler_task.xml
echo         ^<DaysInterval^>1^</DaysInterval^> >> scheduler_task.xml
echo       ^</ScheduleByDay^> >> scheduler_task.xml
echo       ^<Repetition^> >> scheduler_task.xml
echo         ^<Interval^>PT24H^</Interval^> >> scheduler_task.xml
echo       ^</Repetition^> >> scheduler_task.xml
echo     ^</CalendarTrigger^> >> scheduler_task.xml
echo   ^</Triggers^> >> scheduler_task.xml
echo   ^<Settings^> >> scheduler_task.xml
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> scheduler_task.xml
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> scheduler_task.xml
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> scheduler_task.xml
echo     ^<AllowHardTerminate^>false^</AllowHardTerminate^> >> scheduler_task.xml
echo     ^<StartWhenAvailable^>true^</StartWhenAvailable^> >> scheduler_task.xml
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> scheduler_task.xml
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> scheduler_task.xml
echo     ^<Enabled^>true^</Enabled^> >> scheduler_task.xml
echo     ^<Hidden^>false^</Hidden^> >> scheduler_task.xml
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> scheduler_task.xml
echo     ^<DisallowStartOnRemoteAppSession^>false^</DisallowStartOnRemoteAppSession^> >> scheduler_task.xml
echo     ^<UseUnifiedSchedulingEngine^>true^</UseUnifiedSchedulingEngine^> >> scheduler_task.xml
echo     ^<WakeToRun^>false^</WakeToRun^> >> scheduler_task.xml
echo     ^<ExecutionTimeLimit^>PT1H^</ExecutionTimeLimit^> >> scheduler_task.xml
echo     ^<Priority^>7^</Priority^> >> scheduler_task.xml
echo   ^</Settings^> >> scheduler_task.xml
echo   ^<Actions^> >> scheduler_task.xml
echo     ^<Exec^> >> scheduler_task.xml
echo       ^<Command^>python^</Command^> >> scheduler_task.xml
echo       ^<Arguments^>scheduler_simple.py --test^</Arguments^> >> scheduler_task.xml
echo       ^<WorkingDirectory^>%cd%^</WorkingDirectory^> >> scheduler_task.xml
echo     ^</Exec^> >> scheduler_task.xml
echo   ^</Actions^> >> scheduler_task.xml
echo ^</Task^> >> scheduler_task.xml

echo.
echo [5/5] Instalando tarea en Task Scheduler...
schtasks /create /tn "GMAO_GenerarOrdenes" /xml scheduler_task.xml /f

echo.
echo ================================================
echo           CONFIGURACION COMPLETADA
echo ================================================
echo.
echo La tarea "GMAO_GenerarOrdenes" ha sido creada y se ejecutara:
echo   - Todos los dias a las 11:00 AM
echo   - Para generar ordenes de mantenimiento preventivo
echo.
echo COMANDOS UTILES:
echo   - Ver estado:     schtasks /query /tn "GMAO_GenerarOrdenes"
echo   - Ejecutar ahora: schtasks /run /tn "GMAO_GenerarOrdenes"  
echo   - Eliminar tarea: schtasks /delete /tn "GMAO_GenerarOrdenes" /f
echo   - Ver logs:       type logs\scheduler_ordenes.log
echo.
echo PRUEBA MANUAL:
echo   python scheduler_simple.py --test
echo.
pause