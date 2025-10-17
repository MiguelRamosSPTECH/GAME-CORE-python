#baixar essa livraria pip install slack_sdk
import pandas as pd
import psutil
import os
from datetime import datetime
import time
# import boto3
# nome_bucket = "s3-raw-lab-12-10-2025-mrl"
# s3_file_name = "dados_capturados.csv"
# regiao_bucket = "us-east-1"

#iniciar ambiente s3
# s3_client = boto3.client('s3', region_name=regiao_bucket)

#AREA SLACK
#from slack_sdk import WebClient
#from slack_sdk.errors import SlackApiError
#   client = WebClient(token="COLOQUE O TOKEN AQUI")


def to_mb(x):
    return x / (1024**2)

def to_gb(x):
    return x / (1024**3)

def captura_processos():
    for proc in psutil.process_iter():
        pid_proc = proc.pid
        nome_proc = proc.name()
        status_proc = proc.status()
        cpu_uso_proc = proc.cpu_percent()
        ram_uso_proc = [proc.memory_percent(), round(to_mb(proc.memory_info().rss),2), round(to_gb(proc.memory_info().rss),2)]
        total_threads = proc.num_threads()
        ppid = proc.ppid()
        tempo_execucao_proc = proc.create_time()
        icp1 = proc.io_counters()
        time.sleep(intervalo_monitoramento)
        icp2 = proc.io_counters()
        calcula_throughput = ((icp2.read_bytes - icp1.read_bytes) + (icp2.write_bytes - icp1.write_bytes)) / intervalo_monitoramento
        proc_throughput = [round(to_mb(calcula_throughput),2), round(to_gb(calcula_throughput),2)]

intervalo_monitoramento = 0.5
while True:

    user = psutil.users()[0].name

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    #---------------------------------------------------------------------------------------
    #USO DA CPU DE FORMA GERAL (% e em segundos)
    cpu_porcentagem_geral = psutil.cpu_times_percent(interval=intervalo_monitoramento, percpu=False)
    cpu_uso = [round(100 - cpu_porcentagem_geral.idle,2), round((((100 - cpu_porcentagem_geral.idle)/100) * intervalo_monitoramento),2)]

    #USO DA CPU DE FORMA DETALHADA (% e em segundos)
    cpu_idle = [cpu_porcentagem_geral.idle, round((cpu_porcentagem_geral.idle / 100) * intervalo_monitoramento,2)]

    #DESCOMENTAR QUANDO FOR LINUX
    # cpu_iowait = [cpu_porcentagem_geral.iowait, (cpu_porcentagem_geral.iowait / 100) * intervalo_monitoramento]

    cpu_user = [cpu_porcentagem_geral.user, round((cpu_porcentagem_geral.user / 100) * intervalo_monitoramento,2)]

    cpu_system = [cpu_porcentagem_geral.system, round((cpu_porcentagem_geral.system / 100) * intervalo_monitoramento,2)]

    #PROCESSOS ATIVOS + EM FILA (LOADAVG)
    cpu_loadavg = psutil.getloadavg() #ultimos 1, 5 e 15 minutos

    #---------------------------------------------------------------------------------------

    #RAM
    ram_uso_geral = psutil.virtual_memory()
    ram_swap_geral = psutil.swap_memory()

    ram_uso = [round(ram_uso_geral.percent,2), round(to_mb(ram_uso_geral.total - ram_uso_geral.available),2), round(to_gb(ram_uso_geral.total - ram_uso_geral.available),2)]

    ram_disponivel = [ round((ram_uso_geral.available / ram_uso_geral.total) * 100, 2) ,round(to_gb(ram_uso_geral.available),2), round(to_mb(ram_uso_geral.available),2)]

    ram_swap = [ round(ram_swap_geral.percent,2), round(to_mb(ram_swap_geral.used),2), round(to_gb(ram_swap_geral.used),2)  ]
    
    #DESCOMENTAR QUANDO FOR LINUX
    # ram_cached = [ round((ram_uso_geral.cached / ram_uso_geral.total) * 100), round(to_mb(ram_uso_geral.cached),2), round(to_gb(ram_uso_geral.cached),2)]
    #---------------------------------------------------------------------------------------

    #DISCO
    disco_uso_geral = psutil.disk_usage('/')

    disco_io = psutil.disk_io_counters()
    time.sleep(intervalo_monitoramento)
    disco_io2 = psutil.disk_io_counters()
    calcula_throughput = (((disco_io2.read_bytes - disco_io.read_bytes) + (disco_io2.write_bytes - disco_io.write_bytes))/ intervalo_monitoramento)

    disco_uso = [disco_uso_geral.percent, round(to_mb(disco_uso_geral.used),2), round(to_gb(disco_uso_geral.used),2)]
    disco_livre = [round((disco_uso_geral.free/disco_uso_geral.total) * 100,2), round(to_mb(disco_uso_geral.free),2), round(to_gb(disco_uso_geral.free),2)]
    disco_throughput = [round(to_mb(calcula_throughput),2), round(to_gb(calcula_throughput),2)]
    #----------------------------------------------------------------------------------------

    #PROCESSOS
    # captura_processos() NAO DESCOMENTA AINDA

    dados = {
        "servidor": [user],
        "timestamp": [timestamp],
        "cpu_porcentagem": [cpu_uso[0]],
        "cpu_ociosa_porcentagem": [cpu_idle[0]],
        "cpu_usuarios_porcentagem":[cpu_user[0]],
        "cpu_sistema_porcentagem":[cpu_system[0]],
        "cpu_loadavg":[cpu_loadavg],
        "ram_porcentagem":[ram_uso[0]],
        "ram_mb":[ram_uso[1]],
        "ram_gb":[ram_uso[2]],
        "ram_disp_porcentagem":[ram_disponivel[0]],
        "ram_disp_mb":[ram_disponivel[2]],
        "ram_disp_gb":[ram_disponivel[1]],
        "ram_swap_porcentagem":[ram_swap[0]],
        "ram_swap_mb":[ram_swap[1]],
        "ram_swap_gb":[ram_swap[2]],
        "disco_porcentagem":[disco_uso[0]],
        "disco_mb":[disco_uso[1]],
        "disco_gb":[disco_uso[2]],
        "disco_livre_porcentagem":[disco_livre[0]],
        "disco_livre_mb":[disco_livre[1]],
        "disco_livre_gb":[disco_livre[2]],
        "disco_throughput_mbs":[disco_throughput[0]],
        "disco_throughput_gbs":[disco_throughput[1]]

    }

    df = pd.DataFrame(dados)
    
    arquivo = "dados_capturados.csv"

    df.to_csv("dados_capturados.csv", encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo), sep=";")
    # try:
    #     s3_client.upload_file("dados_capturados.csv", nome_bucket, s3_file_name)
    #     print("UPLOAD NO S3 BEM SUCEDIDO")
    # except  Exception as e:
    #     print(f"Erro para fazer upload para o S3: {e}")
    time.sleep(5)

