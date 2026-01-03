from confluent_kafka import Consumer, TopicPartition
import json

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order_tracker_debug",  
    "enable.auto.commit": False,
}

c = Consumer(conf)

c.assign([TopicPartition("orders", 0, 50)])

print("🔊 Listening to ORDERS")

try:
    while True:
        msg = c.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print("🧨 Error:", msg.error())
            continue

        raw = msg.value().decode("utf-8")

        order = json.loads(raw)
        print(f"🍔 Received order: {order['quantity']} x {order['item']} from user {order['user']}")
finally:
    c.close()
