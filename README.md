
# 🍕 Kafka Order Simulation (Python • Docker • KRaft)

Ce projet est une **simulation simple d’un système de commande de livraison**, inspiré de plateformes comme UberEats..  


Le projet repose sur :
- un **Producer Kafka** qui simule un client envoyant une commande
- un **Consumer Kafka** qui lit cette commande et l’affiche
- un **Kafka local exécuté avec Docker**, en **mode KRaft**




## Objectifs :

Ce projet a pour but de comprendre concrètement :

- ce qu’est un **topic Kafka**
- comment fonctionne un **producer**
- comment fonctionne un **consumer**
- comment Kafka transporte des messages (bytes)
- la sérialisation JSON
- la lecture par **partition** et **offset**
- l’exécution de Kafka avec Docker en **mode KRaft**



## Vue globale du fonctionnement :

Flux de données :

```

producer.py  →  Kafka (topic: orders)  →  consumer.py

```

1. Le producer crée une commande
2. La commande est convertie en JSON
3. Le message est envoyé dans Kafka (topic `orders`)
4. Le consumer lit le message depuis Kafka
5. Le consumer affiche le contenu de la commande



## Structure du projet :

```

.
├── docker-compose.yml
├── producer.py
├── consumer.py
└── README.md

```



## Kafka avec Docker 🐳 :

Kafka est lancé via **Docker Compose**, sans Zookeeper.  
Kafka fonctionne en **mode KRaft**, ce qui signifie que le broker Kafka gère lui-même la coordination du cluster.

Kafka est accessible sur :

```

localhost:9092

````

C’est cette adresse qui est utilisée par le producer et le consumer.

### Configuration Kafka (extrait du `docker-compose.yml`)

```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:7.8.3
    ports:
      - "9092:9092"
    environment:
      KAFKA_KRAFT_MODE: "true"
      KAFKA_PROCESS_ROLES: "broker,controller"
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_LISTENERS: "PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093"
      KAFKA_ADVERTISED_LISTENERS: "PLAINTEXT://localhost:9092"
````

### Explication

* **KAFKA_KRAFT_MODE** : active Kafka sans Zookeeper
* **broker,controller** : Kafka joue les deux rôles
* **9092** : port utilisé par les clients (producer / consumer)



## Producer — Envoi d’une commande (`producer.py`) :

Le producer simule un **client** qui passe une commande.

### Connexion à Kafka

```python
producer_config = {
    "bootstrap.servers": "localhost:9092",
}

producer = Producer(producer_config)
```

Le producer se connecte au broker Kafka exposé par Docker.



### Création de la commande

```python
order = {
    "order_id": str(uuid.uuid4()),
    "user": "SKOURI Youssef",
    "item": "Pizza Pepperoni",
    "quantity": 1,
}
```

Cette commande est un simple dictionnaire Python contenant :

* un identifiant unique (`order_id`)
* l’utilisateur
* le produit commandé
* la quantité



### Sérialisation de la commande

Kafka transporte des **bytes**, pas des objets Python.
La commande est donc convertie en JSON, puis encodée.

```python
value = json.dumps(order).encode("utf-8")
```



### Envoi du message dans Kafka

```python
producer.produce(
    topic="orders",
    value=value,
    callback=delivery_report
)
```

* le message est envoyé dans le topic **`orders`**
* un callback est utilisé pour confirmer la livraison



### Callback de livraison

```python
def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record: {err}")
    else:
        print(
            f"Delivered to {msg.topic()} [{msg.partition()}] "
            f"@ offset {msg.offset()}: {msg.value().decode('utf-8')}"
        )
```

Ce callback affiche :

* le topic
* la partition
* l’offset
* le contenu du message


### Flush final :

```python
producer.flush()
```

Le `flush()` force l’envoi de tous les messages avant la fin du programme.



## Consumer — Lecture des commandes (`consumer.py`) :

Le consumer simule un **service de suivi des commandes**.


### Configuration du consumer :

```python
conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "order_tracker_debug",
    "enable.auto.commit": False,
}
```

* `group.id` identifie le groupe de consommateurs
* le commit automatique des offsets est désactivé



### Assignation manuelle (partition + offset) :

```python
c.assign([TopicPartition("orders", 0, 50)])
```

Cela signifie que le consumer :

* lit le topic **orders**
* uniquement la partition **0**
* à partir de l’offset **50** (J'ai sélectionné 50 juste pour ne pas affiché l'historique complète)

Cette approche permet un contrôle précis de la position de lecture.



### Boucle de consommation :

```python
msg = c.poll(1.0)
```

* attend jusqu’à 1 seconde un message
* retourne `None` si aucun message n’est disponible



### Décodage et parsing JSON :

```python
raw = msg.value().decode("utf-8")
order = json.loads(raw)
```

Le message Kafka est :

1. décodé depuis les bytes
2. transformé en dictionnaire Python



### Affichage de la commande :

```python
print(
    f"🍔 Received order: {order['quantity']} x {order['item']} "
    f"from user {order['user']}"
)
```

Le consumer affiche une version lisible de la commande reçue.



### Fermeture propre :

```python
finally:
    c.close()
```

Le consumer est fermé correctement, même en cas d’arrêt du programme.



## Exécution du projet :

### 1. Démarrer Kafka :

```bash
docker-compose up -d
```

### 2. Lancer le consumer :

```bash
python consumer.py
```

### 3. Lancer le producer :

```bash
python producer.py
```

La commande envoyée par le producer apparaît immédiatement dans le terminal du consumer.
