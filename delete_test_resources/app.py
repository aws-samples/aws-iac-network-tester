import logging
import botocore
import boto3

cloudFormationClient = boto3.client('cloudformation')
ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    inflight_network_test_details = event['pathdetails']
    logging.info("event >> " + str(event))

    if inflight_network_test_details:
        for test_detail in inflight_network_test_details:
            try:
                ec2Client.delete_network_insights_analysis(
                    NetworkInsightsAnalysisId=test_detail['NetworkInsightsAnalysisId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error("Call to delete_network_insights_analysis failed")
                raise error
            
            try:
                ec2Client.delete_network_insights_path(
                    NetworkInsightsPathId=test_detail['NetworkInsightsPathId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error("Call to delete_network_insights_path failed")
                raise error

    return
