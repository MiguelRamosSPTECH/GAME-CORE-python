import psutil

for proc in psutil.process_iter(['pid', 'name', 'username']):
    try:
        print(proc.info)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass