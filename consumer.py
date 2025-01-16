from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'test-topic',  # Le nom du topic
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
      # Identifiant du groupe de consommateurs
    key_deserializer=lambda k: k.decode() if k is not None else None,  # Vérification de la clé
    value_deserializer=lambda v: v.decode()  # Désérialisation de la valeur
)

print("En attente de nouveaux messages...")

for message in consumer:
    # Si la clé est None, on affiche une valeur par défaut (par exemple "Aucune clé")
    key = message.key if message.key is not None else "Aucune clé"
    print(f"Message reçu - Clé: {key}, Valeur: {message.value}")
