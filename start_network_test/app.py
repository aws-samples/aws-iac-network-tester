import logging
import botocore
import boto3

cloudFormationClient = boto3.client('cloudformation')
ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    try:
        response = ec2Client.create_network_insights_path(
            Source=event['Source'],
            Destination=event['Destination'],
            Protocol='tcp'
        )
    except botocore.exceptions.ClientError as error:
        logging.error("Call to create_network_insights_path failed")
        raise error

    networkInsightPath = response['NetworkInsightsPath']
    networkInsightPathId = networkInsightPath['NetworkInsightsPathId']
    logging.info("networkInsight Path Id >> " + str(networkInsightPathId))

    try:
        response = ec2Client.start_network_insights_analysis(
            NetworkInsightsPathId=networkInsightPathId
        )
    except botocore.exceptions.ClientError as error:
        logging.error("Call to start_network_insights_analysis failed")
        raise error

    networkInsightAnalysis = response['NetworkInsightsAnalysis']
    networkInsightAnalysisId = networkInsightAnalysis['NetworkInsightsAnalysisId']
    logging.info("networkInsight Analysis Id >> " + str(networkInsightAnalysisId))

    inflight_network_test_detail = {
        'Source': event['Source'],
        'Destination': event['Destination'],
        'RouteTag': event['RouteTag'],
        'NetworkInsightsPathId': networkInsightPathId,
        'NetworkInsightsAnalysisId': networkInsightAnalysisId
    }
    return inflight_network_test_detail
