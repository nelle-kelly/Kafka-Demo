import json
from datetime import datetime
from time import sleep
from random import choice
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    
    key_serializer=lambda k: k.encode(),
    value_serializer=lambda v: v.encode()
)

while True:
    key = input("Entrez la clé du message (ou 'exit' pour quitter) : ")
    if key.lower() == 'exit':
        break
    value = input("Entrez la valeur du message : ")
    
    producer.send('test-topic', key=key, value=value)
    producer.flush()
    print(f"Message envoyé avec clé: {key} et valeur: {value}")

print("Fin de l'envoi des messages")
