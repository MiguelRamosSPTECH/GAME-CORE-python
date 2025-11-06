import docker
from docker.errors import NotFound
import os
import json
import pandas as pd
import psutil
from datetime import datetime
import time
import boto3
import glob
#-----------------------------------------------------------
#AREA CONEXAO COM BUCKETS AWS
nome_bucket = "bucket-raw-gamecore"
regiao_bucket = "us-east-1"

#iniciar ambiente s3
s3_client = boto3.client('s3', region_name=regiao_bucket)
#------------------------------------------------------------
RAM_LIMITE = "512m"
CPU_LIMITE = "1"

client = docker.from_env() #conecta com docker (precisa estar iniciado)

def to_mb(x):
    return x / (1024**2)

def to_gb(x):
    return x / (1024**3)




def captura_processos():
    global dados_processos_direto
    for proc in psutil.process_iter():
        proc.cpu_percent(interval=None)

        pid_proc = proc.pid
        nome_proc = proc.name()
        status_proc = proc.status()
        cpu_uso_proc = proc.cpu_percent()
        ram_uso_proc = [proc.memory_percent(), round(to_mb(proc.memory_info().rss),2), round(to_gb(proc.memory_info().rss),2)]
        total_threads = proc.num_threads()
        ppid = proc.ppid()
        tempo_execucao_proc = proc.create_time()
        icp1 = proc.io_counters()
        icp2 = proc.io_counters()
        calcula_throughput = ((icp2.read_bytes - icp1.read_bytes) + (icp2.write_bytes - icp1.write_bytes)) / intervalo_monitoramento
        proc_throughput = [round(to_mb(calcula_throughput),2), round(to_gb(calcula_throughput),2)]
        
        dados_processos_direto['timestamp'].append(timestamp)
        dados_processos_direto['pid'].append(pid_proc)
        dados_processos_direto['ppid'].append(ppid)
        dados_processos_direto['nome_processo'].append(nome_proc)
        dados_processos_direto['status'].append(status_proc)
        dados_processos_direto['cpu_porcentagem'].append(cpu_uso_proc)
        dados_processos_direto['ram_porcentagem'].append(ram_uso_proc[0])
        dados_processos_direto['total_threads'].append(total_threads)
        dados_processos_direto['tempo_execucao'].append(tempo_execucao_proc)
        dados_processos_direto['throughput_mbs'].append(proc_throughput[0])
        dados_processos_direto['throughput_gbs'].append(proc_throughput[1])
        
        
    
    df_proc = pd.DataFrame(dados_processos_direto)
    top10_cpu = df_proc.sort_values(by="cpu_porcentagem", ascending=False).head(50)
    top10_ram = df_proc.sort_values(by="ram_porcentagem", ascending=False).head(50)
    top10_disco = df_proc.sort_values(by="throughput_mbs", ascending=False).head(50)

    top10_geral1 = pd.merge(top10_cpu, top10_ram, on=["pid", "nome_processo"], how="inner")

    top10_geral2 = pd.merge(top10_geral1, top10_disco, on=["pid", "nome_processo"], how="inner")



    arquivo_proc = "dados_processos.csv"

    top10_geral2.to_csv(arquivo_proc, encoding="utf-8", index=False, mode="a", header=not os.path.exists(f"{arquivo_proc}"), sep=";")




    top10_cpu1 = df_proc.sort_values(by="cpu_porcentagem", ascending=False).head(10)


    top10_cpu1.to_csv("dados_processos_cpu.csv", encoding="utf-8", index=False, mode="a", header=not os.path.exists("dados_processos_cpu.csv"), sep=";")


#PARTE DE MANIPULAÇÃO DOS CONTAINERS
def gerencia_containers(acao):
    lista_containers = client.containers.list()
    porta_container = 25565
    identificacao_container = 1
    identificacao_volume = 1

    for loop in range(0,3):
        container = None
        volume = None
        if acao == "excluir" :
            #tenta localizar container
            try:
                container = client.containers.get(f"mc-server-{identificacao_container}")
                container.stop()
                container.remove()
                print(f"✅ Container 'mc-server-{identificacao_container}' removido com sucesso!")  
            except NotFound:
                print(f"Erro: o container 'mc-server-{identificacao_container}' não foi encontrado!")
                continue

            #tenta localizar volume 
            try:
                volume = client.volumes.get(f"mc-data-{identificacao_container}")
                volume.remove(force=True)
                print(f"✅ Volume 'mc-data-{identificacao_container}' removido com sucesso!")
            except NotFound:
                print(f"Erro: O volume 'mc-data-{identificacao_container}' não foi encontrado.")
                continue
        elif acao == "criar" and len(lista_containers) < 3:            
            client.containers.run(
                "itzg/minecraft-server", #imagem
                name=f"mc-server-{identificacao_container}",
                detach=True, #-d
                ports = {f'25565/tcp' : porta_container},
                environment=['EULA=TRUE', 'TZ=America/Sao_Paulo', 'FORCE_IPV4=true'],
                mem_limit=RAM_LIMITE,
                cpuset_cpus=CPU_LIMITE,
                volumes={f'mc-data-{identificacao_container}': {'bind':'/data','mode':'rw'}} #colocar na pasta data tudo do mundo e posso escrever e ler dados
            )
            print(f"CONTAINER {loop+1} CRIADO COM SUCESSO!")
            identificacao_container= identificacao_container+1
            porta_container=porta_container+1
            identificacao_volume=identificacao_volume+1



#PARTE DE CAPTURAR OS DADOS DO CONTAINER
dados_anteriores = {    
    'read_bytes': None,
    'write_bytes': None,
    'total_usage': None,
    'system_cpu_usage': None
}

def dados_container(name):
    #zerar valores men
    dados_anteriores['read_bytes'] = None
    dados_anteriores['write_bytes'] = None
    dados_anteriores['total_usage'] = None
    dados_anteriores['system_cpu_usage'] = None

    container_monitora = client.containers.get(name)


    container_monitora.exec_run(['mkdir','-p','/arquivos_descompactados/']) #cria diretório para gravar o arquivo descompactado
    
    #exec_run só executa comando no CMD, sem forçar o shell do container, por isso tava dando b.o
    #/sh -> mais leve que o /bash, é para comandos mais simples e diretos.
    #sem -c ele acha que é um arquivo ou caminho de arquivo para tentar executar
    container_monitora.exec_run(['rcon-cli', 'perf start']) #gerar dados de desempenho do servidor
    time.sleep(0.5)
    container_monitora.exec_run(['rcon-cli', 'perf stop'])
    time.sleep(0.25) #esperar pra realmente pegar o ultimo arquivo

    exit_code, output_bytes = container_monitora.exec_run(['ls','-t', '/data/debug/profiling'])
    arq_zip = output_bytes.decode('utf-8').split('\n')[0]
    conteudo_arq_zip = os.path.join('/data/debug/profiling/', arq_zip) #garantir o caminho absoluto correto
    
    container_monitora.exec_run(['unzip','-o',conteudo_arq_zip, '-d', '/arquivos_descompactados/']) #descompacta
    codigo_saida, saida_bytes = container_monitora.exec_run(['cat','/arquivos_descompactados/server/metrics/ticking.csv'])
    soma_ticktime = 0.0
    
    for linha in saida_bytes.decode('utf-8').split('\n')[1:]:
        if len(linha) > 0:
            tick = float(linha.split(',')[1])
            soma_ticktime+=tick

    #pega valor minimo entre tps_real e 20.0 (maximo) e dps arredonda para 2 (tendo os ticks por segundo)
    tps_container = round(min(1000000000 / (soma_ticktime / (len(saida_bytes.decode('utf-8').split('\n')) - 2)), 20.0),2)

    for dados_container in container_monitora.stats(stream=True): #retorna dados em bytes
        dados_formata = json.loads(dados_container.decode('utf-8')) #le no formato br e transforma em json para poder acessar os dados
        soma_read_bytes = 0
        soma_write_bytes = 0
        for blkio in dados_formata['blkio_stats']['io_service_bytes_recursive']: 
            if(blkio['op'].lower() == 'read'):
                soma_read_bytes+=blkio['value']
            elif(blkio['op'].lower() == 'write'):
                soma_write_bytes+=blkio['value']
        
        if dados_anteriores['read_bytes'] is None: 
            dados_anteriores['total_usage'] = dados_formata['cpu_stats']['cpu_usage']['total_usage']
            dados_anteriores['system_cpu_usage'] = dados_formata['cpu_stats']['system_cpu_usage']
            
            dados_anteriores['read_bytes'] = soma_read_bytes
            dados_anteriores['write_bytes'] = soma_write_bytes
        else:

            cpu_total_delta = dados_formata['cpu_stats']['cpu_usage']['total_usage'] - dados_anteriores['total_usage']
            system_total_delta = dados_formata['cpu_stats']['system_cpu_usage'] - dados_anteriores['system_cpu_usage']

            cpu_uso_docker = 0.0
            if system_total_delta > 0:
                cpu_uso_docker = round((cpu_total_delta / system_total_delta) * 1 * 100, 2)
            
            throughput_container = round(to_mb(((soma_read_bytes - dados_anteriores['read_bytes']) + (soma_write_bytes - dados_anteriores['write_bytes'])) / intervalo_monitoramento),2)
            ram_uso = round(((dados_formata['memory_stats']['usage'] / dados_formata['memory_stats']['limit']) * 100),2)
            throttled_time = (dados_formata['cpu_stats']['throttling_data']['throttled_time'] / 1000000000) / 60
            return [cpu_uso_docker, throughput_container, ram_uso, throttled_time, tps_container]



intervalo_monitoramento = 0.5
# gerencia_containers("excluir")
# gerencia_containers("criar")
while True: 
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_arquivos = timestamp.split(" ")[1][0:len(timestamp.split(" ")[1])-3]

    # LIMPAR CSV PARA NOVO DIA
    dia_antes = None
    caminho_busca = os.path.join("/", "*.csv") #caminho absoluto de qualquer arquivo que termine com .csv
    arquivos_csv = glob.glob(caminho_busca) #pega e transforma em uma lista 

    if (dia_antes != None) and (timestamp.split(" ")[0] != dia_antes):
        for arquivo in arquivos_csv:
            try:
                with open(arquivo, "w", encoding="utf-8") as f:
                    pass
            except IOError as e:
                print(f"Erro ao limpar o(s) arquivo(s): {e}")
            print("Processo de limpeza de arquivos CSV concluído.")


    macadress = psutil.net_if_addrs()['Wi-Fi'][0].address

    #---------------------------------------------------------------------------------------
    #USO DA CPU DE FORMA GERAL (% e em segundos)
    cpu_porcentagem_geral = psutil.cpu_times_percent(interval=intervalo_monitoramento, percpu=False)
    cpu_uso = [round(100 - cpu_porcentagem_geral.idle,2), round((((100 - cpu_porcentagem_geral.idle)/100) * intervalo_monitoramento),2)]

    #USO DA CPU DE FORMA DETALHADA (% e em segundos)
    cpu_idle = [cpu_porcentagem_geral.idle, round((cpu_porcentagem_geral.idle / 100) * intervalo_monitoramento,2)]

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

    #REDE

    rede_io_counters = psutil.net_io_counters()
    bytes_enviados = to_mb(rede_io_counters.bytes_sent)
    bytes_recebidos = to_mb(rede_io_counters.bytes_recv)
    #----------------------------------------------------------------------------------------
    df_container = {
        "identificacao_container":[],
        "timestamp":[],
        "cpu_container":[],
        "throughput_container":[],
        "ram_container":[],
        "throttled_time_container":[],
        "tps_container":[]
    }

    for i in range(1,4):
        dcm = dados_container(f"mc-server-{i}")
        df_container['identificacao_container'].append(f"mc-server-{i}")
        df_container['timestamp'].append(timestamp)
        df_container['cpu_container'].append(dcm[0])
        df_container['throughput_container'].append(dcm[1])
        df_container['ram_container'].append(dcm[2])
        df_container['throttled_time_container'].append(dcm[3])
        df_container['tps_container'].append(dcm[4])

    #PROCESSOS
    dados_processos_direto = {
        'timestamp': [],
        'pid': [],
        'ppid': [],
        'nome_processo': [],
        'status': [],
        'cpu_porcentagem': [],
        'ram_porcentagem': [],
        'total_threads': [],
        'tempo_execucao': [],
        'throughput_mbs': [],
        'throughput_gbs': []
    }
    captura_processos()
    dados = {
        "macadress": [macadress],
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
        "disco_throughput_gbs":[disco_throughput[1]],
        "rede_enviados_mb_":[bytes_enviados],
        "rede_recebidos_mb":[bytes_recebidos]
    }
    #CONTAINER
    df_c = pd.DataFrame(df_container)
    arquivo_c = "dados_containers.csv"
    df_c.to_csv(arquivo_c, encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo_c), sep=";")

    #SERVIDOR
    df = pd.DataFrame(dados)
    arquivo = "dados_capturados.csv"
    df.to_csv(arquivo, encoding="utf-8", index=False, mode="a", header=not os.path.exists(arquivo), sep=";")
    try:
        data_formatada = timestamp.replace(" ", "-")
        s3_client.upload_file(arquivo, nome_bucket, f"{timestamp.split(" ")[0]}/{arquivo}")
        s3_client.upload_file(arquivo_c, nome_bucket, f"{timestamp.split(" ")[0]}/{arquivo_c}")
        s3_client.upload_file("dados_processos_cpu.csv", nome_bucket, f"{timestamp.split(" ")[0]}/dados_processos_cpu.csv")
        s3_client.upload_file("dados_processos.csv", nome_bucket, f"{timestamp.split(" ")[0]}/dados_processos.csv")
        print(f"✅ [{data_formatada}] - UPLOAD DOS CSV'S no BUCKET RAW bem sucedido!")
    except Exception as e:
        print(f"Erro para fazer upload para o S3: {e}")
    dia_antes = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time.sleep(5)