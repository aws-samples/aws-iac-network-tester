import logging
import botocore
import boto3

ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    inflight_network_test_details = event['pathdetails']

    logging.info("inflight network tests >> " + str(inflight_network_test_details))

    successful_tests = []
    running_tests = []
    failed_tests = []

    if inflight_network_test_details:
        for test_detail in inflight_network_test_details:
            logging.info("test detail >> " + str(test_detail))
            try:
                response = ec2Client.describe_network_insights_analyses(
                    NetworkInsightsAnalysisIds=[
                        test_detail['NetworkInsightsAnalysisId']],
                    NetworkInsightsPathId=test_detail['NetworkInsightsPathId']
                )
            except botocore.exceptions.ClientError as error:
                logging.error("Call to describe_network_insights_analyses failed")
                raise error

            test_status = response['NetworkInsightsAnalyses'][0]['Status']

            if (test_status == 'succeeded'):
                test_detail['NetworkPathFound'] = response['NetworkInsightsAnalyses'][0]['NetworkPathFound']
                if not test_detail['NetworkPathFound']:
                    test_detail['Explanations'] = response['NetworkInsightsAnalyses'][0]['Explanations']
                successful_tests.append(test_detail)
            elif (test_status == 'running'):
                running_tests.append(test_detail)
            else:
                failed_tests.append(test_detail)

        return {
            "succeeded": {
                "testdetail": successful_tests,
                "count": len(successful_tests)
            },
            "running": {
                "testdetail": running_tests,
                "count": len(running_tests)
            },
            "failed": {
                "testdetail": failed_tests,
                "count": len(failed_tests)
            },
        }
