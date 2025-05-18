from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import uuid
from datetime import datetime
from confluent_kafka import Producer

try:
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
except Exception:  # noqa: E722
    configure_spark_with_delta_pip = None
    SparkSession = None

app = FastAPI()


class AskRequest(BaseModel):
    prompt: str
    context: dict | None = None
    external_llm: str
    reply_topic: str


def save_to_delta(record: dict, external_llm: str) -> None:
    delta_path = os.getenv("DELTA_PATH")
    if not delta_path or SparkSession is None:
        return
    target_path = os.path.join(delta_path, "llm", "requests", external_llm)
    builder = SparkSession.builder.appName("bridge-llm-proxy")
    if configure_spark_with_delta_pip:
        builder = configure_spark_with_delta_pip(builder)
    spark = builder.getOrCreate()
    spark.createDataFrame([record]).write.format("delta").mode("append").save(target_path)
    spark.stop()


def publish_kafka(record: dict) -> None:
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    producer = Producer({"bootstrap.servers": broker})
    producer.produce("llm.requests", json.dumps(record).encode("utf-8"))
    producer.flush()


@app.post("/llm/ask")
async def llm_ask(req: AskRequest):
    if not req.prompt or not req.external_llm or not req.reply_topic:
        raise HTTPException(status_code=400, detail="prompt, external_llm, reply_topic required")

    job_id = str(uuid.uuid4())
    ctx = req.context or {}
    ctx["timestamp"] = datetime.utcnow().isoformat()

    record = req.dict()
    record["job_id"] = job_id
    record["context"] = ctx
    record["sender_id"] = os.getenv("SERVICE_ID", "bridge-llm-proxy")

    save_to_delta(record, req.external_llm)
    publish_kafka(record)

    return {
        "status": "submitted",
        "trace_id": ctx.get("trace_id"),
        "job_id": job_id,
        "external_llm": req.external_llm,
    }
