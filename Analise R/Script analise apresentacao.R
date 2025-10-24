install.packages("ggplot2")
library(ggplot2)


dados <- rbind(csv_grupo)


# Filtrando os dados numericos:

dados <- dados[, -c(1,2,7)]


# Vendo relações com a CPU

relacoes_uso_cpu <- cor(dados$cpu_porcentagem, dados[,-1])

names(relacoes_uso_cpu) <- colnames(dados[,-1])

colnames(relacoes_uso_cpu)

correlacoes_significativas_cpu <- relacoes_uso_cpu[abs(relacoes_uso_cpu) >= 0.39]

correlacoes_significativas_cpu

#    cpu_usuarios_porcentagem  cpu_sistema_porcentagem     disco_throughput_mbs 
#           0.9655547                0.9346501                0.4057711 

#    disco_throughput_gbs 
#           0.3987123 



# Com isso temos as correlações relevantes



# -----------------------------------------------

# Achando as principais metricas a ser exibidas - no caso Usuario Porcentagem e disco_throughput 



  # Relação usuario e SO com o total:


  correlacao_usuario <- cor(dados$cpu_porcentagem, dados$cpu_usuarios_porcentagem)
  
  print(correlacao_usuario * correlacao_usuario)
  # 93% - Extremamente relevante
  
  correlacao_sistema <- cor(dados$cpu_porcentagem, dados$cpu_sistema_porcentagem)
  
  print(correlacao_sistema * correlacao_sistema)
  # 87% - Extremamente relevante
  
  
  correlacao_partes <- cor(dados$cpu_usuarios_porcentagem, dados$cpu_sistema_porcentagem)
  
  print(correlacao_partes ^2)
  # 66%
  
  # Com isso temos 66% do uso do SO é explicado pelo uso do usuario e vice e versa.
  
    #Escolhendo a mais adequada:
    

    
    boxplot(dados$cpu_usuarios_porcentagem,
            dados$cpu_sistema_porcentagem,
            names = c("CPU Usuário", "CPU Sistema"), 
            col = c("#1f77b4", "#ff7f0e"),           
            border = "black",                        
            main = "Comparação de oscilação",
            ylab = "CPU (%)")       
       
    # Com todos esses dados, podemos concluir que a CPU sistema oscila menos que a CPU usuario, que
    # como uma influencia em 66% a outra, concluimos que a mais relevante para exibição é a CPU USUARIO
    
    
    plot(dados$cpu_porcentagem, dados$cpu_usuarios_porcentagem,
         main = "Relação entre Uso de CPU e Disco Throughput",
         xlab = "CPU (%)",
         ylab = "Disco Throughput (MB/s)",
         col = "blue")
    
    abline(lm(cpu_usuarios_porcentagem ~ cpu_porcentagem, data = dados))
    
    
    

correlacao_cpu_disco <- cor(dados$cpu_porcentagem, dados$disco_throughput_mbs)

print(correlacao_cpu_disco ^2)
# 16.45% - 


plot(dados$cpu_porcentagem, dados$disco_throughput_mbs,
     main = "Relação entre Uso de CPU e Disco Throughput",
     xlab = "CPU (%)",
     ylab = "Disco Throughput (MB/s)",
     col = "blue")

abline(lm(disco_throughput_mbs ~ cpu_porcentagem, data = dados))




# --------------------------------------------------



# Vendo relações com a RAM

relacoes_uso_ram <- cor(dados$ram_porcentagem, dados[,-c(5,6,7,8,9,10)])

names(relacoes_uso_ram) <- colnames(dados[,-c(5,6,7,8,9,10)])

colnames(relacoes_uso_ram)

correlacoes_significativas_ram <- relacoes_uso_ram[abs(relacoes_uso_ram) >= 0.39]

correlacoes_significativas_ram

#Unico significativo, conforme esperado é a quantidade de ram em swap

#  ram_swap_porcentagem
#         0.5566794

print(0.5566794 ^2)
# 30.9892%



plot(dados$ram_porcentagem, dados$ram_swap_porcentagem,
     main = "Relação entre RAM Total e RAM Swap",
     xlab = "RAM Total (%)",
     ylab = "RAM Swap (%)",
     col = "green")

abline(lm(ram_swap_porcentagem ~ ram_porcentagem, data = dados))





# ---------------------

# Definindo os limites de alertas:

box_cpu <- boxplot(dados$cpu_porcentagem,
                   main = "Distribuição do Uso de CPU (%)")

box_cpu$stats

# Limite da CPU - 18.3 (valor maximo sem ser outlieier) , no caso, como terão 3 containers por servidor:

# Limite da CPU - 54,9  ----- mediano     --- + 50% --- 82,35 --- alto

box_ram <- boxplot(dados$ram_porcentagem,
                   main = "Distribuição do Uso de RAM (%)")

box_ram$stats

# Limite da Ram - 85.4 (3 quartil, topo da caixa) ---- mediano     - 91.6 ---- alto




# Entendimento das variaveis


plot(dados$cpu_porcentagem, main = "Percentual de Utilização da CPU")

plot(dados$ram_porcentagem, main = "Percentual de Utilização da Memória (RAM)")


# Isso justifica a desconsideração de algumas variaveis, pois como é possível reparar, os dados foram capturados
# de maquinas com utilizações diversas, logo, faz sentido desconsiderar a relação forte entre ram e uso disco
# por exemplo