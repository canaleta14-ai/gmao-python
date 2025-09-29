import win32serviceutil 
import win32service 
import win32event 
import os 
import sys 
import subprocess 
 
class GMAOSchedulerService(win32serviceutil.ServiceFramework): 
    _svc_name_ = "GMAOScheduler" 
    _svc_display_name_ = "GMAO Ordenes Scheduler" 
    _svc_description_ = "Servicio para generar ordenes automaticas a las 11:00 AM" 
 
    def __init__(self, args): 
        win32serviceutil.ServiceFramework.__init__(self, args) 
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None) 
        self.running = True 
 
    def SvcStop(self): 
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        win32event.SetEvent(self.hWaitStop) 
        self.running = False 
 
    def SvcDoRun(self): 
        import time 
        script_dir = os.path.dirname(os.path.abspath(__file__)) 
        os.chdir(script_dir) 
        while self.running: 
            try: 
                subprocess.run([sys.executable, "scheduler_simple.py"], cwd=script_dir) 
            except: 
                time.sleep(60) 
 
if __name__ == '__main__': 
    win32serviceutil.HandleCommandLine(GMAOSchedulerService) 
