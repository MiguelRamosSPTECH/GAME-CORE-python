#baixar essa livraria pip install slack_sdk
import pandas as pd
import psutil
import os
from datetime import datetime
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


client = WebClient(token="COLOQUE AQUI O TOKEN DO SLACK")

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

    # Verifica se algum recurso passou de 80%
    if mediaGeralCpu > 85 or ram > 85 or disco > 85:
        alerta = (
            f"⚠️ *Alerta de uso elevado detectado!*\n"
            f"🕒 {timestamp}\n"
            f"👤 Usuário: {user}\n"
            f"💻 CPU: {mediaGeralCpu}%\n"
            f"🧠 RAM: {ram}%\n"
            f"💾 Disco: {disco}%"
        )

        try:
            response = client.chat_postMessage(
                channel="#suporte-jira",
                text=alerta
            )
            print("Alerta enviado para o Slack.")
        except SlackApiError as e:
            print("Erro ao enviar alerta:", e.response["error"])

    time.sleep(10)
