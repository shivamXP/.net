#!/bin/bash 
git clone https://github.com/shivamXP/.net.git
cd .net
sudo sed -i "s/xxxx/$greenService/g" "./cloudformation/event.json"
sudo aws lambda invoke --function-name shivamBlueGreen --invocation-type RequestResponse --payload  file://cloudformation/event.json  outfile.txt --region us-east-1 --profile saml
cd ..
rm -rf .net

