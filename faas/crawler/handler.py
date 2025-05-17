import os
import json


def handle(event, context):
    """Dummy crawler function.

    This skeleton simulates a data crawler which would receive crawl
    requests from Kafka or the orchestration layer. It simply returns a
    placeholder response.
    """
    request = event.body.decode('utf-8')
    return json.dumps({"status": "fetched", "request": request})
