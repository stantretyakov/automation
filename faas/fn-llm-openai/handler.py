import os
import json
import uuid
from datetime import datetime
import requests
from confluent_kafka import Consumer, Producer

try:
    from delta import configure_spark_with_delta_pip
    from pyspark.sql import SparkSession
except Exception:  # noqa: E722
    configure_spark_with_delta_pip = None
    SparkSession = None

PROVIDER = "openai"


def save_to_delta(record: dict) -> None:
    delta_path = os.getenv("DELTA_PATH")
    if not delta_path or SparkSession is None:
        return
    target_path = os.path.join(delta_path, "llm", "responses", PROVIDER)
    builder = SparkSession.builder.appName(f"fn-llm-{PROVIDER}")
    if configure_spark_with_delta_pip:
        builder = configure_spark_with_delta_pip(builder)
    spark = builder.getOrCreate()
    spark.createDataFrame([record]).write.format("delta").mode("append").save(target_path)
    spark.stop()


def call_openai(prompt: str, api_key: str, model: str) -> tuple[str, int | None]:
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens")
    return text, tokens


def handle(event, context):  # noqa: D401
    """Process one LLM request message from Kafka."""
    broker = os.getenv("KAFKA_BROKER", "kafka:9092")
    model_name = os.getenv("MODEL_NAME", "gpt-4")
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        return json.dumps({"status": "error", "message": "missing API key"})

    consumer = Consumer({
        "bootstrap.servers": broker,
        "group.id": f"fn-llm-{PROVIDER}",
        "auto.offset.reset": "earliest",
    })
    consumer.subscribe(["llm.requests"])
    msg = consumer.poll(1.0)
    if msg is None:
        consumer.close()
        return json.dumps({"status": "no messages"})
    if msg.error():
        consumer.close()
        return json.dumps({"status": "error", "message": str(msg.error())})

    data = json.loads(msg.value().decode("utf-8"))
    if data.get("external_llm") != PROVIDER:
        consumer.commit(msg)
        consumer.close()
        return json.dumps({"status": "skipped"})

    prompt = data.get("prompt", "")
    trace_id = data.get("context", {}).get("trace_id")
    reply_topic = data.get("reply_topic", "")
    job_id = data.get("job_id", str(uuid.uuid4()))

    try:
        text, tokens = call_openai(prompt, api_key, model_name)
    except Exception as err:  # noqa: BLE001
        consumer.commit(msg)
        consumer.close()
        return json.dumps({"status": "error", "message": str(err)})

    result = {
        "trace_id": trace_id,
        "job_id": job_id,
        "llm_response": text,
        "model": model_name,
        "source": f"fn-llm-{PROVIDER}",
        "timestamp": datetime.utcnow().isoformat(),
        "tokens": tokens,
    }

    producer = Producer({"bootstrap.servers": broker})
    producer.produce(reply_topic, json.dumps(result).encode("utf-8"))
    producer.flush()

    record = {"input": data, "output": result}
    save_to_delta(record)

    consumer.commit(msg)
    consumer.close()
    return json.dumps({"status": "processed", "job_id": job_id})
