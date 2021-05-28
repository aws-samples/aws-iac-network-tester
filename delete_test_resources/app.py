import logging
import botocore
import boto3

cloudFormationClient = boto3.client('cloudformation')
ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    inflight_network_test_details = event['globalvars']['routedetails']['inflightroutetotest']['inflightroutes']
    logging.info("event >> " + str(event))

    delete_network_insights_resources(inflight_network_test_details)
    updatedTestResult = format_test_output(
        inflight_network_test_details, event)

    return updatedTestResult


def delete_network_insights_resources(inflight_network_test_details):

    if inflight_network_test_details:
        for test_detail in inflight_network_test_details:
            try:
                ec2Client.delete_network_insights_analysis(
                    NetworkInsightsAnalysisId=test_detail['NetworkInsightsAnalysisId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error(
                    "Call to delete_network_insights_analysis failed")
                raise error

            try:
                ec2Client.delete_network_insights_path(
                    NetworkInsightsPathId=test_detail['NetworkInsightsPathId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error("Call to delete_network_insights_path failed")
                raise error


def format_test_output(inflight_network_test_details, event):
    testResult = {}

    successful_tests = []
    timedout_tests = []
    failed_tests = []

    for test_detail in inflight_network_test_details:
        if (test_detail['Status'] == 'succeeded'):
            successful_tests.append(test_detail)
        elif(test_detail['Status'] == 'running'):
            timedout_tests.append(test_detail)
        elif(test_detail['Status'] == 'running'):
            failed_tests.append(test_detail)

    try:
        testResult = event['testresult']
        successful_tests = successful_tests + \
            testResult['succeeded']['testdetail']
        timedout_tests = timedout_tests + testResult['running']['testdetail']
        failed_tests = failed_tests + testResult['failed']['testdetail']

    except KeyError:
        logging.info("first time processing test results")

    updatedTestResult = {
        "succeeded": {
            "testdetail": successful_tests,
            "count": len(successful_tests)
        },
        "timedout": {
            "testdetail": timedout_tests,
            "count": len(timedout_tests)
        },
        "failed": {
            "testdetail": failed_tests,
            "count": len(failed_tests)
        },
    }

    return updatedTestResult
