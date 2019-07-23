#!/bin/bash 
dt=`date '+%d-%m-%Y-%H-%M-%S'`
commit=$(git log --oneline --format=%B -n 1 HEAD | head -n 1)
sudo docker build -t i25077 .
sudo $(sudo aws ecr get-login --no-include-email --region us-east-1)
sudo docker tag i25077:latest 063114128614.dkr.ecr.us-east-1.amazonaws.com/i25077:$dt
sudo docker push 063114128614.dkr.ecr.us-east-1.amazonaws.com/i25077:$dt
sudo sed -i "s/xxxx/$dt/g" "./cloudformation/preProdServiceParameters.json"
sudo sed -i "s/yyyy/$commit/g" "./cloudformation/preProdServiceParameters.json"
sudo aws cloudformation create-stack --stack-name SequelDemoService-$commit --template-body file://cloudformation/service.yaml --parameters=file://cloudformation/preProdServiceParameters.json  --capabilities CAPABILITY_IAM --profile saml --region us-east-1
