import docker
import json
import time
RAM_LIMITE = "512m"
CPU_LIMITE = "1"

client = docker.from_env() #conecta com docker (precisa estar iniciado)
lista_containers = client.containers.list()

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
    if len(lista_containers) > 0:
        for c in lista_containers:
            container = client.containers.get(c.name)
            container.stop()
            container.remove()
            print(f"CONTAINER {c.name} EXCLUÍDO COM SUCESSO!")



# ----------- FOR PARA DADOS DE HARDWARE CONSUMIDOS DO CONTAINER -----------------
# for container_criado in client.containers.list():
#     cnc = client.containers.get(container_criado.name)
#     for dados_c in cnc.stats(stream=True):
#         stats_data = json.loads(dados_c.decode('utf-8'))
#         # uso_total_cpu = to_mb(stats_data['cpu_stats']['cpu_usage']['total_usage'])
#         print(stats_data)
#         time.sleep(10)
#-------------FOR PARA PROCESSOS-----------------
    # processos_container = cnc.top()
    # for processo in processos_container['Processes']:
    #     print(processo)