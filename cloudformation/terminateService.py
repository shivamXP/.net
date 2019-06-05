import json
import boto3
import os
def lambda_handler(event, context):
    elbvclient = boto3.client('elbv2')
    client = boto3.client('ecs')
    servicename = os.environ["servicename"]
    clustername = os.environ["clustername"]   
    loadbalancerarn = os.environ["loadbalancerarn"] 
            
    response_servicedetails = client.describe_services(
        cluster=clustername,
        services=[
            servicename
        ]
    )
    
    for x in range(0, len(response_servicedetails['services']) ):
        targetgroupservice = response_servicedetails['services'][0]['loadBalancers'][0]['targetGroupArn']
    
    response_tgdescription = elbvclient.describe_target_groups(
        TargetGroupArns=[
            targetgroupservice
        ]
    )
    
    response_albinfo = elbvclient.describe_listeners(
        LoadBalancerArn=loadbalancerarn
    )
    
    for x in range(0, len(response_albinfo['Listeners']) ):
        thisarn = response_albinfo['Listeners'][x]['ListenerArn']
        response_ListARNinfo = elbvclient.describe_rules(
            ListenerArn = thisarn
        )

        for y in range(0, len(response_ListARNinfo['Rules']) ):
            if(response_ListARNinfo['Rules'][y]['Priority']=="default"):
                default_rulearn = response_ListARNinfo['Rules'][y]['RuleArn']
                response_modifylistfordr  = elbvclient.modify_listener(
                    ListenerArn = thisarn,
                    DefaultActions=[
                        {
                            'Type':  'fixed-response',    
                            'FixedResponseConfig': {
                                'MessageBody': 'Sorry! This page has been moved!',
                                'StatusCode': '400',
                                'ContentType': 'text/html'
                            }
                        }
                    ]
                        
                )
            else:
                rule1arn = response_ListARNinfo['Rules'][y]['RuleArn']
                tgarnfromruleextraction = response_ListARNinfo['Rules'][y]['Actions'][0]['TargetGroupArn']
                if(targetgroupservice == tgarnfromruleextraction ):
                    response_ruledeletion = elbvclient.delete_rule(
                        RuleArn=rule1arn
                    )
                    response_tgdeletion = elbvclient.delete_target_group(
                        TargetGroupArn=tgarnfromruleextraction
                    ) 