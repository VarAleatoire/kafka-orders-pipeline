import uuid
import json
from confluent_kafka import Producer

producer_config = {
    "bootstrap.servers": "localhost:9092",
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record: {err}")
    else:
        print(f"Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}: {msg.value().decode('utf-8')}")

order = {
    "order_id": str(uuid.uuid4()),
    "user": "SKOURI Youssef",
    "item": "Pizza peperoni",
    "quantity": 1,
}

value = json.dumps(order).encode("utf-8")

producer.produce(topic="orders", 
                 value=value, 
                 callback=delivery_report

)



producer.flush()


