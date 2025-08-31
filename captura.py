import pandas as pd
import psutil
import os
from datetime import datetime
import time

while True:

    user = psutil.users()[0].name

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mediaGeralCpu = psutil.cpu_percent(interval=1, percpu=False)

    mediaLogicasCpu = psutil.cpu_percent(interval=1, percpu=True)

    soma = 0

    for valorAtual in mediaLogicasCpu:
        soma += valorAtual

    mediaLogica = round(soma / len(mediaLogicasCpu), 2)
    
    ram = psutil.virtual_memory().percent

    disco = psutil.disk_usage("/").percent

    print(f"dia e hora: {timestamp}, Média Geral: {mediaGeralCpu}%, Média Lógica: {mediaLogica}%, ram: {ram}%, disco: {disco}¨%")

    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [mediaGeralCpu],
        "logicas_cpu": [mediaLogica],
        "ram": [ram],
        "disco": [disco]
    }

    df = pd.DataFrame(dados)
    
    arquivo = "dados-capturados.csv"

    df.to_csv("dados-capturados.csv", encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo))

    time.sleep(10)
