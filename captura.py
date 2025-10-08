#baixar essa livraria pip install slack_sdk
import pandas as pd
import psutil
import os
from datetime import datetime
import time
#from slack_sdk import WebClient
#from slack_sdk.errors import SlackApiError

#   client = WebClient(token="COLOQUE O TOKEN AQUI")

while True:

    user = psutil.users()[0].name

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    mediaGeralCpu = psutil.cpu_percent(interval=1, percpu=False)

    mediaLogicasCpu = psutil.cpu_percent(interval=1, percpu=True)

    frequenciaCpu = psutil.cpu_freq()
    print(frequenciaCpu)
    freq_atual_ghz = round(frequenciaCpu.current / 1000,2)

    swap = psutil.swap_memory()

    swap_usado = round(swap.used / (1024 ** 2),2)
    
    ram = psutil.virtual_memory().percent

    disco = psutil.disk_usage("/").percent

    nucleos_cpu = psutil.cpu_percent(percpu=True, interval=0.5)

    internet =  psutil.net_io_counters(pernic=False, nowrap=True)

    porcentagemErroRecebido = internet.errin * 100 / internet.packets_recv

    porcentagemErroEnviado = internet.errout * 100 / internet.packets_sent

    def processo_jogo_cpu():
        for proc in psutil.process_iter(['pid','name','status','cpu_percent','memory_percent']):
            if proc.name() == "Code.exe":
                return [proc.pid, proc.name(), proc.status(), psutil.Process(proc.pid).cpu_percent(interval=1), 
                        psutil.Process(proc.pid).memory_percent(), 
                        psutil.Process(proc.pid).num_threads()]

<<<<<<< HEAD
    
    processo_u_jogo = processo_jogo()
=======

    processo_u_jogo = processo_jogo_cpu()
>>>>>>> 2f56f527af2caed7e7891a0b0d53bc0913747ef9
    # print(f"dia e hora: {timestamp}, Média Geral CPU: {mediaGeralCpu}%, Média Lógica CPU: {mediaLogica}%, frequencia_cpu: {frequenciaCpu}, ram: {ram}%, ram_swap: {swap}, disco: {disco}¨% |\n {nucleos_cpu} |\n {processo_u_jogo}")
    

    # Ordenando a lista de nucleos
    for i in range(0,len(nucleos_cpu),1):
        maior = i
        for j in range (i + 1, len(nucleos_cpu),1):
            if(nucleos_cpu[j] > nucleos_cpu[maior]):
                maior = j
        
        aux = nucleos_cpu[i]
        nucleos_cpu[i] = nucleos_cpu[maior]
        nucleos_cpu[maior] = aux



    qtd_processos =  len(psutil.pids ())



    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [mediaGeralCpu],
        "nucleo1":nucleos_cpu[0],
        "nucleo2":nucleos_cpu[1],
        "nucleo3":nucleos_cpu[2],
        "nucleo4":nucleos_cpu[3],
        "frequencia_cpu_ghz": [freq_atual_ghz],
        "ram_uso": [ram],
        "ram_swap": [swap_usado],
        "disco": [disco],
        "pid_processo":[processo_u_jogo[0]],
        "nome_processo":[processo_u_jogo[1]],
        "status_processo":[processo_u_jogo[2]],
        "uso_cpu_processo":[processo_u_jogo[3]],
        "uso_ram_processo":[processo_u_jogo[4]],
        "qtd_threads_processo":[processo_u_jogo[5]],
        "total_processos": [qtd_processos],
        "bytesRecebidos" : [internet.bytes_recv],
        "Porcentagem_de_erro_recebido" : [porcentagemErroRecebido],
        "bytesEnviados" : [internet.bytes_sent],
        "Porcentagem_de_erro_enviado" : [porcentagemErroEnviado]
    }

    df = pd.DataFrame(dados)
    
    arquivo = "dados-capturados.csv"

    df.to_csv("dados-capturados.csv", encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo), sep=";")

    time.sleep(2)
