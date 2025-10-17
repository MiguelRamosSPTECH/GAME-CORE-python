import docker
import time
import json
import os
RAM_LIMITE = "512m"
CPU_LIMITE = "1"

client = docker.from_env() #conecta com docker (precisa estar iniciado)

def to_mb(x):
    return x / (1024*1024)

def cria_containers():
    porta_container = 25565
    identificacao_container = 1
    identificacao_volume = 1

    for loop in range(0,3):
        client.containers.run(
            "itzg/minecraft-server", #imagem
            name=f"mc-server-{identificacao_container}",
            detach=True, #-d
            ports = {f'25565/tcp' : porta_container},
            environment=['EULA=TRUE'],
            mem_limit=RAM_LIMITE,
            cpuset_cpus=CPU_LIMITE,
            volumes={f'mc-data-{identificacao_container}': {'bind':'/data','mode':'rw'}} #colocar na pasta data tudo do mundo e posso escrever e ler dados
        )
        print(f"CONTAINER {loop+1} CRIADO COM SUCESSO!")
        identificacao_container= identificacao_container+1
        porta_container=porta_container+1
        identificacao_volume=identificacao_volume+1

def exclui_container():
    lista_containers = client.containers.list()
    if len(lista_containers) < 3:
        for c in lista_containers:
            container = client.containers.get(c.name)
            container.stop()
            container.remove()
            print(f"CONTAINER {c.name} EXCLUÍDO COM SUCESSO!")
            
# exclui_container()
# cria_containers()

dados_anteriores = {
    'read_bytes': None,
    'write_bytes': None,
}

def dados_container(name):
    dados_anteriores['read_bytes'] = None
    dados_anteriores['write_bytes'] = None
    container_monitora = client.containers.get(name)
    container_monitora.exec_run(['mkdir','-p','/arquivos_descompactados/']) #cria diretório para gravar o arquivo descompactado

    container_monitora.exec_run(['rcon-cli', 'perf', 'start']) #gerar dados de desempenho do servidor
    time.sleep(0.5)
    container_monitora.exec_run(['rcon-cli', 'perf', 'stop'])
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
            dados_anteriores['read_bytes'] = soma_read_bytes
            dados_anteriores['write_bytes'] = soma_write_bytes
        else:
            cpu_total = dados_formata['cpu_stats']['cpu_usage']['total_usage'] - dados_formata['precpu_stats']['cpu_usage']['total_usage']
            throughput_container = round(to_mb(((soma_read_bytes - dados_anteriores['read_bytes']) + (soma_write_bytes - dados_anteriores['write_bytes'])) / 0.5),2)
            ram_uso = round(((dados_formata['memory_stats']['usage'] / dados_formata['memory_stats']['limit']) * 100),2)
            throttled_time = (dados_formata['cpu_stats']['throttling_data']['throttled_time'] / 1000000000) / 60
            return [cpu_total, throughput_container, ram_uso, throttled_time, tps_container]

        time.sleep(0.5)



dc1 = dados_container('mc-server-1')
# dc2 = dados_container('mc-server-2')
# dc3 = dados_container('mc-server-3')
# print(dc1,'\n',dc2,'\n',dc3)
