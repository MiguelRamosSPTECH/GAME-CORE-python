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

    freq_atual_ghz = round(frequenciaCpu.current / 1000,2)

    swap = psutil.swap_memory()

    swap_usado = round(swap.used / (1024 ** 2),2)


    soma = 0

    for valorAtual in mediaLogicasCpu:
        soma += valorAtual

    mediaLogica = round(soma / len(mediaLogicasCpu), 2)
    
    ram = psutil.virtual_memory().percent

    disco = psutil.disk_usage("/").percent

    nucleos_cpu = psutil.cpu_percent(percpu=True, interval=0.5)

    internet =  psutil.net_io_counters(pernic=False, nowrap=True)

    porcentagemErroRecebido = internet.errin * 100 / internet.packets_recv

    porcentagemErroEnviado = internet.errout * 100 / internet.packets_sent

    def processo_maior_cpu():

        psutil.cpu_percent(interval=0) 
        
        # 2. Aguardamos um instante para que o sistema acumule dados de uso de CPU
        time.sleep(0.1)

        maior_cpu_percent = -1.0
        processo_maior_cpu = None

        # 3. Iteramos sobre os processos e coletamos o uso de CPU
        for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_percent']):
            try:
                p = psutil.Process(proc.info['pid'])
                
                # Aqui, chamamos sem 'interval' para obter a taxa acumulada desde o 'reset'
                cpu_uso_atual = p.cpu_percent()
                
                if cpu_uso_atual > maior_cpu_percent:
                    maior_cpu_percent = cpu_uso_atual
                    
                    # Coleta todas as informações do processo vencedor
                    processo_maior_cpu = [
                        proc.info['pid'], 
                        proc.info['name'], 
                        proc.info['status'], 
                        cpu_uso_atual, 
                        proc.info['memory_percent'], # Usamos a leitura já disponível
                        p.num_threads()
                    ]

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
                
        # Se nenhum processo foi encontrado (o que é improvável), retorna valores vazios
        if processo_maior_cpu is None:
            return [0, "N/A", "N/A", 0.0, 0.0, 0]
            
        return processo_maior_cpu

    processo_u_jogo = processo_maior_cpu()
    # print(f"dia e hora: {timestamp}, Média Geral CPU: {mediaGeralCpu}%, Média Lógica CPU: {mediaLogica}%, frequencia_cpu: {frequenciaCpu}, ram: {ram}%, ram_swap: {swap}, disco: {disco}¨% |\n {nucleos_cpu} |\n {processo_u_jogo}")
    


    dados = {
        "user": [user],
        "timestamp": [timestamp],
        "cpu": [mediaGeralCpu],
        "nucleo1":nucleos_cpu[0],
        "nucleo2":nucleos_cpu[1],
        "nucleo3":nucleos_cpu[2],
        "nucleo4":nucleos_cpu[3],
        "nucleo5":nucleos_cpu[4],
        "nucleo6":nucleos_cpu[5],
        "nucleo7":nucleos_cpu[6],
        "nucleo8":nucleos_cpu[7],
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
        "bytesRecebidos" : [internet.bytes_recv],
        "Porcentagem_de_erro_recebido" : [porcentagemErroRecebido],
        "bytesEnviados" : [internet.bytes_sent],
        "Porcentagem_de_erro_enviado" : [porcentagemErroEnviado]
    }

    df = pd.DataFrame(dados)
    
    arquivo = "dados-capturados.csv"

    df.to_csv("dados-capturados.csv", encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo), sep=";")

    time.sleep(2)


    # Verifica se algum recurso passou de 80%
   # if mediaGeralCpu > 85 or ram > 85 or disco > 85:
    #    alerta = (
     #       f"⚠️ *Alerta de uso elevado detectado!*\n"
      #      f"🕒 {timestamp}\n"
       #     f"👤 Servidor: RIOT-SERVER-1B \n"
        #    f"💻 CPU: {mediaGeralCpu}%\n"
         #   f"🧠 RAM: {ram}%\n"
          #  f"💾 Disco: {disco}%"
        #)
#
 #       try:
  #          response = client.chat_postMessage(
   #             channel="#suporte-slack",
    #            text=alerta
     #       )
      #      print("Alerta enviado para o Slack.")
       # except SlackApiError as e:
        #    print("Erro ao enviar alerta:", e.response["error"])
