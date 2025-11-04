
echo "instalando o node"

sudo apt update && sudo apt upgrade -y

sudo apt install nodejs -y



echo "instalando o mysql"

echo "Insira a senha do root do mysql"

sudo apt install mysql-server


echo "criando um usuario sysadmin"

echo ""

echo "insira uma senha para o novo usuario"

read -s SENHA

sudo useradd -m -p $(openssl passwd -1 "$SENHA")


echo "dando permissão sudo  e de conectar via ssh"


sudo mkdir -p /home/sysadmin/.ssh
sudo chown sysadmin:sysadmin /home/sysadmin/.ssh
sudo chmod 700 /home/sysadmin/.ssh

sudo usermod -aG sudo sysadmin

# Partes novas:

echo "clonando o repositorio do site no git"

git clone https://github.com/MiguelRamosSPTECH/GAME-CORE-site.git



echo "Iniciando e habilitando o serviço MySQL"

sudo systemctl start mysql # Inicia o serviço o mysql
sudo systemctl enable mysql # Faz o mysql começar quando der o boot na EC2


sudo mysql < Game Core/GAME-CORE-site/src/database/script-tabelas.sql

echo "Mysql configurado"

echo "Terminando a configuração do ambiente" 