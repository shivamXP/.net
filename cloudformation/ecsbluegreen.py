import json
import boto3
import os
def lambda_handler(event, context):
    elbclient = boto3.client('elbv2')
    ecsclient = boto3.client('ecs')
    clustername = event["clustername"]
    service_green = event["servicegreenname"]
    service_blue = event["servicebluename"]
    albarn = event["albarn"]
    response_servicedetails = ecsclient.describe_services(
        cluster=clustername,
        services=[service_green]
    )
    targetgroup1arn = response_servicedetails['services'][0]['loadBalancers'][0]['targetGroupArn']
    response_tgdescription = elbclient.describe_target_groups(
        TargetGroupArns=[
            targetgroup1arn
        ]
    )
    # -  - - -  - - -  - - - - - - - 
    response_service2details = ecsclient.describe_services(
        cluster=clustername,
        services=[service_blue]
    )
    targetgroupbluearn = response_service2details['services'][0]['loadBalancers'][0]['targetGroupArn']
    response_tgbluedescription = elbclient.describe_target_groups(
        TargetGroupArns=[
            targetgroupbluearn
        ]
    )
    # -  - - -  - - -  - - - - - - - 
    response_albinfo = elbclient.describe_listeners(
        LoadBalancerArn=albarn
    )
    tg1 = None
    tg2 = None
    new_rule_1 = None
    new_rule_2 = None
    for x in range(0, len(response_albinfo['Listeners']) ):
        this_listener_arn = response_albinfo['Listeners'][x]['ListenerArn']
        response_ListARNinfo = elbclient.describe_rules(
            ListenerArn = this_listener_arn
        )
        for y in range(0, len(response_ListARNinfo['Rules']) ):
            rulearnfromjson = response_ListARNinfo['Rules'][y]['RuleArn']
            if(response_ListARNinfo['Rules'][y]['Priority']!="default"):
                new_rule_priority = int(response_ListARNinfo['Rules'][y]['Priority'])
                if(new_rule_priority > 1):
                    new_rule_priority = new_rule_priority - 1 
                else:
                    break
                testrulefortarggroup = str(response_ListARNinfo['Rules'][y]['Actions'][0])
                if("TargetGroupArn" in testrulefortarggroup):
                    tgarnfromruleextraction = response_ListARNinfo['Rules'][y]['Actions'][0]['TargetGroupArn']
                    if(targetgroup1arn == tgarnfromruleextraction ):
                        rulegreenarn = rulearnfromjson
                        tg1 = tgarnfromruleextraction
                        response_newrule1creation = elbclient.create_rule(
                            Actions=[
                                {
                                    'TargetGroupArn': tg1,
                                    'Type': 'forward',
                                },
                            ],
                            Conditions=[
                                {
                                    'Field': 'path-pattern',
                                    'Values': [
                                        '*',
                                    ],
                                },
                            ],
                            ListenerArn=this_listener_arn,
                            Priority=new_rule_priority
                        )
                        
                        new_rule_1 = response_newrule1creation['Rules'][0]['RuleArn']
                        
                        response_oldrule1deletion = elbclient.delete_rule(
                            RuleArn=rulegreenarn
                        )
                        break
                    
                    elif(targetgroupbluearn == tgarnfromruleextraction):
                        rulebluearn = rulearnfromjson
                        tg2 = tgarnfromruleextraction
                        response_newrule2creation = elbclient.create_rule(
                            Actions=[
                                {
                                    'TargetGroupArn': tg2,
                                    'Type': 'forward',
                                },
                            ],
                            Conditions=[
                                {
                                    'Field': 'path-pattern',
                                    'Values': [
                                        '*',
                                    ],
                                },
                            ],
                            ListenerArn=this_listener_arn,
                            Priority=new_rule_priority
                        )
                        new_rule_2 = response_newrule2creation['Rules'][0]['RuleArn']
                        
                        response_oldrule2deletion = elbclient.delete_rule(
                            RuleArn=rulebluearn
                        )
                        
                        break
    
    if(tg1 is not None and tg2 is not None and new_rule_1 is not None and new_rule_2 is not None):     
        response1 = elbclient.modify_rule(
                        Actions= [
                            {
                                'TargetGroupArn': tg2, 
                                'Type': "forward"
                            }
                        ],
                        RuleArn = new_rule_1
                    )
        response2 = elbclient.modify_rule(
                        Actions= [
                            {
                                'TargetGroupArn': tg1, 
                                'Type': "forward"
                            }
                        ],
                        RuleArn = new_rule_2
                    )
    else:
        print("One or more resources required for the blue green implementation is missing or is inaccurate.")
