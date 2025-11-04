#!/bin/bash

echo "criando uma nova instancia EC2 na AWS"

echo "Pegando informações de VPCs"

echo "Resultado da VPC a ser usada $(aws ec2 describe-vpcs --query "Vpcs[*].[CidrBlock,VpcId]" --output table)"

VPC=$(aws ec2 describe-vpcs --query "Vpcs[0].VpcId" --output text)




echo " Pegando as sub redes"

echo "$(aws ec2 describe-subnets --query "Subnets[*].[SubnetId,CidrBlock,AvailabilityZone,Tags.Name]" --output table)"

echo "Pegando a subnet que sera utilizada"

echo "$(aws ec2 describe-subnets --query "Subnets[0].[SubnetId,CidrBlock,AvailabilityZone,Tags.Name]" --output table)"

SUBNET=$(aws ec2 describe-subnets --query "Subnets[0].SubnetId" --output text)




echo " Pegando os grupos de segurança"

echo "$(aws ec2 describe-security-groups  --query "SecurityGroups[*].[GroupName,GroupId]" --output table)"

echo "Pegando o grupo de segurança que será usado"

echo "$(aws ec2 describe-security-groups  --query "SecurityGroups[0].[GroupName,GroupId]" --output table)"

GRUPOSEGURANCA=$(aws ec2 describe-security-groups  --query "SecurityGroups[0].[GroupName,GroupId]" --output text)




echo " Criando a sua chave com o nome minhachave.pem"


aws ec2 create-key-pair --key-name minhachave --region us-east-1 --query 'KeyMaterial' --output text > minhachave.pem




echo "Criando o grupo de segurança"


aws ec2 create-security-group --group-name launch-wizard-42 --vpc-id "$VPC" --description "grupo de segurança 042" --tag-specifications "ResourceType=security-group,Tags=[{Key=Name,Value=sg-042}]"





echo "Criando as regras de entada do grupo de segurança"

aws ec2 authorize-security-group-ingress --group-id "$GRUPOSEGURANCA" --protocol tcp --port 80 --cidr 0.0.0.0/0






echo "Criando a instância"


aws ec2 run-instances \
 --image-id ami-0360c520857e3138f \
 --count 1 \
 --security-group-ids "$GRUPOSEGURANCA" \
 --instance-type t3.small \
 --subnet-id "$SUBNET" \
 --key-name minhachave \
 --block-device-mappings \
'[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20, \
"VolumeType":"gp3","DeleteOnTermination":true}}]' \
 --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=web-server-01}]'






