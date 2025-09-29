import psutil

internet =  psutil.net_io_counters(pernic=False, nowrap=True)

porcentagemErroRecebido = internet.errin * 100 / internet.packets_recv

porcentagemErroEnviado = internet.errout * 100 / internet.packets_sent



print(internet)

print("aaaaaaaa")

print(internet.bytes_sent)

    dados = {
        "bytesRecebidos" : [internet.bytes_recv],
        "Porcentagem_de_erro_recebido" : [porcentagemErroRecebido]
        "bytesEnviados" : [internet.bytes_sent],
        "Porcentagem_de_erro_enviado" : [porcentagemErroEnviado]
    }