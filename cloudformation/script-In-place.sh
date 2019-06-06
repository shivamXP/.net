#!/bin/bash 
dt=`date '+%d-%m-%Y-%H-%M-%S'`
git clone https://github.com/shivamXP/.net.git
cd .net
sudo docker build -t i25077 .
sudo $(sudo aws ecr get-login --no-include-email --region us-east-1)
sudo docker tag i25077:latest 063114128614.dkr.ecr.us-east-1.amazonaws.com/i25077:$dt
sudo docker push 063114128614.dkr.ecr.us-east-1.amazonaws.com/i25077:$dt
sudo sed -i "s/xxxx/$dt/g" "./cloudformation/prodServiceParameters.properties"
sudo aws cloudformation deploy --template-file ./cloudformation/service.yaml  --stack-name $stackName --parameter-overrides $(cat ./cloudformation/prodServiceParameters.properties) --capabilities CAPABILITY_IAM --region us-east-1 --profile saml
cd ..
rm -rf .net