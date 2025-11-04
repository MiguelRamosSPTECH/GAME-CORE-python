ARQUIVO_DOCKER=script-docker.sh
DOCKER_COMPOSE_VERSION="v2.24.5"

echo "criando um usuario sysadmin"

echo ""

echo "insira uma senha para o novo usuario"

read -s SENHA

sudo useradd -m -p $(openssl passwd -1 "$SENHA")


echo "dando permissão sudo e de conectar via ssh"


sudo mkdir -p /home/sysadmin/.ssh
sudo chown sysadmin:sysadmin /home/sysadmin/.ssh
sudo chmod 700 /home/sysadmin/.ssh

sudo usermod -aG sudo sysadmin


#------------BAIXANDO O DOCKER-----------------#
echo "BAIXANDO DOCKER NA INSTÂNCIA..."
sudo touch $ARQUIVO_DOCKER
sudo cat "$ARQUIVO_DOCKER" << EOF
#!/bin/bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
EOF
echo "EXECUTANDO ARQUIVO DE INSTALAÇÃO DO DOCKER"
sudo bash $ARQUIVO_DOCKER

echo "DOCKER baixado e configurado com sucesso!!!"

#----------------BAIXANDO DOCKER COMPOSE-----------------#
echo "Instalando o docker compose...."

#garante que seja pro LINUX na arquitetura correta (x64, x86) e salva no diretório padrão do sistema p poder usar o comando em todo o SO
sudo curl -L "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

#permissao de execucao (precaucao)
sudo chmod +x /usr/local/bin/docker-compose

echo "Versão do docker compose:"
/usr/local/bin/docker-compose version

#-------------------------------------------------------------#


