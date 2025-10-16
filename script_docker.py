import docker
import time
import json
import asyncio
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
    if len(lista_containers) > 0:
        for c in lista_containers:
            container = client.containers.get(c.name)
            container.stop()
            container.remove()
            print(f"CONTAINER {c.name} EXCLUÍDO COM SUCESSO!")
            
# exclui_container()
# cria_containers()

# ----------- FOR PARA DADOS DE HARDWARE CONSUMIDOS DO CONTAINER -----------------
def dados_container(name):
    qtdLoop = 0
    container_monitora = client.containers.get(name)
    container_monitora.exec_run(['rcon-cli', 'perf', 'start'])
    time.sleep(10)
    container_monitora.exec_run(['rcon-cli', 'perf', 'stop']) 
    for dados_container in container_monitora.stats(stream=True): #retorna dados em bytes
        dados_formata = json.loads(dados_container.decode('utf-8')) #le no formato br e transforma em json para poder acessar os dados
        print(dados_formata)
        qtdLoop+=1
        time.sleep(1)
        if qtdLoop == 2 : break 


# dados_container('mc-server-1')
# dados_container('mc-server-2')
dados_container('mc-server-3')


#-------------FOR PARA PROCESSOS-----------------
    # processos_container = cnc.top()
    # for processo in processos_container['Processes']:
    #     print(processo)