import logging


def lambda_handler(event, context):
    logging.info("event>>> " + str(event))

    numberOfTimesToWait = event['analysisWaitCount']
    index = event['iterator']['index']
    step = event['analysisDuration']

    totalWait = numberOfTimesToWait * step
    index += step

    return {
        "index": index,
        "continue": index < totalWait
    }
