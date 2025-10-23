dados <- rbind(csv_grupo)


# Filtrando os dados:

dados <- dados[, -c(1,2,7)]






# Vendo relações com a CPU

relacoes_uso_cpu <- cor(dados$cpu_porcentagem, dados[,-1])

names(relacoes_uso_cpu) <- colnames(dados[,-1])

colnames(relacoes_uso_cpu)

correlacoes_significativas_cpu <- relacoes_uso_cpu[abs(relacoes_uso_cpu) >= 0.39]

correlacoes_significativas_cpu


plot(dados$cpu_porcentagem)




# -----------------------------------------------
# Achando as principais metricas a ser exibidas - no caso Usuario Porcentagem e disco_throughput 

correlacao_usuario <- cor(dados$cpu_porcentagem, dados$cpu_usuarios_porcentagem)

print(correlacao_usuario * correlacao_usuario)
# 0.93% - Extremamente relevante

correlacao_sistema <- cor(dados$cpu_porcentagem, dados$cpu_sistema_porcentagem)

print(correlacao_sistema * correlacao_sistema)
# 0.87% - Em casos reais se mantem fixos, no caso, como irá utilizar o mesmo kernel, fica um tanto quanto despresivel

correlacao_partes <- cor(dados$cpu_usuarios_porcentagem, dados$cpu_sistema_porcentagem)

print(correlacao_partes ^2)
#0.66%


correlacao_cpu_disco <- cor(dados$cpu_porcentagem, dados$disco_throughput_mbs)

print(correlacao_cpu_disco ^2)
# 0.1645






# --------------------------------------------------

# Vendo relações com a RAM

relacoes_uso_ram <- cor(dados$ram_porcentagem, dados[,-c(5,6,7,8,9,10)])

names(relacoes_uso_ram) <- colnames(dados[,-c(5,6,7,8,9,10)])

colnames(relacoes_uso_ram)

correlacoes_significativas_ram <- relacoes_uso_ram[abs(relacoes_uso_ram) >= 0.39]

correlacoes_significativas_ram
#Unico significativo, conforme esperado é a quantidade de ram em swap

plot(dados$ram_porcentagem)



# ---------------------

# Definindo os limites de alertas:

box_cpu <- boxplot(dados$cpu_porcentagem)

box_cpu$stats

# Limite da CPU - 18.3, no caso, como terão 3 containers por servidor:

# Limite da CPU - 54,9  ----- mediano     --- + 50% --- 82,35 --- alto

box_ram <- boxplot(dados$ram_porcentagem)

box_ram$stats

# Limite da Ram - 85.4 ---- mediano     - 91.6 ---- alto




# Entendimento das variaveis

box_usuario <- boxplot(dados$cpu_usuarios_porcentagem)
box_usuario$stats


box_sistem <- boxplot(dados$cpu_sistema_porcentagem)
box_sistem$stats

cor(dados$cpu_sistema_porcentagem, dados$cpu_usuarios_porcentagem)

plot(dados$cpu_porcentagem)
lm(dados$cpu_sistema_porcentagem ~ dados$cpu_usuarios_porcentagem)


box_cpu <- boxplot(dados$cpu_porcentagem)

box_cpu$stats
