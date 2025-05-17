import os
import json
from faas.common import db


def handle(event, context):
    """Dummy crawler function.

    This skeleton simulates a data crawler which would receive crawl
    requests from Kafka or the orchestration layer. It simply returns a
    placeholder response.
    """
    body = event.body.decode("utf-8")
    try:
        pipeline_id = int(body)
    except ValueError:
        return json.dumps({"status": "error", "message": "invalid pipeline id"})

    metadata = db.get_pipeline_metadata(pipeline_id)
    return json.dumps({"status": "fetched", "pipeline": metadata})
