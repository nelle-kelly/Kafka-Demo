# Documentation : Installation et Configuration de Kafka

## Introduction
Apache Kafka est une plateforme distribuée de streaming qui permet de publier, stocker, traiter et consommer des flux de données en temps réel. Cette documentation couvre :

1. L'installation de Kafka avec et sans Docker.
2. La configuration de Kafka avec ZooKeeper et Kraft (Kafka Raft).
3. Les réponses aux questions fréquentes sur Kafka pour mieux comprendre son fonctionnement.

---

## 1. Installation de Kafka sans Docker

### Prérequis
- Java 8 ou version supérieure.
- Scala préinstallé.
- Machine Linux ou WSL (Windows Subsystem for Linux).

### Étapes d'installation
1. **Télécharger Kafka** :
   ```bash
   wget https://downloads.apache.org/kafka/<version>/kafka_<scala_version>-<kafka_version>.tgz
   ```
   Exemple :
   ```bash
   wget https://downloads.apache.org/kafka/3.4.0/kafka_2.13-3.4.0.tgz
   ```
  ou vous pouvez simplement installer le fichier Zip sur le cite officiel Kafka

2. **Extraire l'archive** :
   ```bash
   tar -xzf kafka_2.13-3.4.0.tgz
   cd kafka_2.13-3.4.0
   ```

3. 

4. **Lancer ZooKeeper** :
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

5. **Lancer Kafka** :
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

6. **Vérifier l'installation** :
   Créer un topic pour tester :
   ```bash
   bin/kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092
   ```

---

## 2. Installation de Kafka avec Docker

### Prérequis
- Docker installé et fonctionnel.
- Docker Compose installé.

### Création du fichier `docker-compose.yml`
Dans un dossier nommé `kafka-docker` :

```yaml
version: '3.8'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    depends_on:
      - zookeeper

```

### Lancer Kafka avec Docker
1. Démarrer les services :
   ```bash
   docker-compose up -d
   ```

2. Tester l'installation :
   ```bash
   docker exec -it kafka bash
   kafka-topics.sh --create --topic test-topic --bootstrap-server localhost:9092
   ```

---

## 3. Configuration de Kafka

### Configuration avec ZooKeeper
Par défaut, Kafka utilise ZooKeeper pour la gestion des métadonnées du cluster. Les paramètres pertinents sont dans `server.properties` :

```properties
zookeeper.connect=localhost:2181
log.dirs=/tmp/kafka-logs
broker.id=1
offsets.topic.replication.factor=1
```

### Configuration avec Kraft (Kafka Raft)
KRaft est pris en charge à partir de Kafka 2.8, mais la prise en charge complète est stabilisée dans Kafka 3.3 et au-delà. Assurez-vous que vous utilisez une version compatible.

Kraft remplace ZooKeeper pour gérer le consensus et simplifie l’architecture de Kafka. Pour activer Kraft :

1. **Modifier `server.properties`** :
   ```properties
   process.roles=broker,controller
   controller.quorum.voters=1@localhost:9093
   controller.listener.names=CONTROLLER
   listeners=PLAINTEXT://:9092,CONTROLLER://:9093
   log.dirs=/tmp/kraft-logs
   node.id=1
   ```

2. **Initialiser le cluster Kraft** :
   ```bash
   kafka-storage.sh format -t <uuid> -c config/server.properties
   ```

3. **Démarrer Kafka** :
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```


---

## 4. Questions Fréquentes

### Un consumer peut-il supprimer un événement après l’avoir reçu ?
Non, les messages dans Kafka sont immuables. Cependant, vous pouvez configurer des durées de rétention ou supprimer un topic entièrement.

### Le producer a-t-il le contrôle sur l’ordre des événements ?
Un producer Kafka ne peut pas explicitement définir l'offset d'un message ou forcer Kafka à assigner un offset particulier comme 0 ou 1.
Cependant, il a une certaine influence sur l'ordre d'envoi des messages et sur la manière dont les offsets sont attribués grâce à la gestion des partitions.

### la clé du message doit-elle etre obligatoirement spécifier?

La clé du message dans Kafka n'est pas strictement obligatoire. Cependant, elle joue un rôle important dans la gestion de la distribution des messages entre les partitions du topic.

#### Rôle de la clé :
Partitionnement : Kafka utilise la clé pour déterminer la partition du topic dans laquelle le message sera envoyé. Si tu fournis une clé, Kafka appliquera un hachage sur cette clé pour déterminer dans quelle partition du topic le message sera placé. Cela permet de garantir que les messages avec la même clé seront toujours envoyés à la même partition, ce qui peut être utile si tu veux conserver l'ordre des messages par clé.

Uniqueness : La clé n'a pas besoin d'être unique au niveau global du topic. Par exemple, plusieurs messages peuvent avoir la même clé (ce qui signifie qu'ils iront tous dans la même partition). En revanche, chaque message est unique grâce à son offset (identifiant dans la partition), même si les clés sont identiques.



---

### Un consumer a la possibilité de supprimer un message apres l'avoir reçu?

Dans Kafka, un consommateur ne peut pas directement supprimer un événement après l'avoir reçu ou traité.
Kafka est conçu comme un système de journal distribué immuable, ce qui signifie que les événements (messages) restent dans le journal (topic) jusqu'à ce qu'ils expirent ou soient supprimés selon les configurations définies au niveau du broker.





# zookeeper avec kafka
ZooKeeper agit comme un "chef d’orchestre" pour les clusters Kafka. Voici son rôle expliqué étape par étape :

### Élection du contrôleur Kafka
Lorsqu’un cluster Kafka démarre, ZooKeeper choisit un broker pour être le contrôleur.

* Lorsque Kafka démarre, tous les brokers tentent de créer un nœud éphémère dans ZooKeeper pour devenir contrôleur.
* ZooKeeper permet à un seul broker de créer ce nœud. Celui qui réussit devient le contrôleur.
* Si ce broker tombe en panne, ZooKeeper détecte la perte du nœud éphémère et lance une nouvelle élection.

### Gestion des partitions et des réplicas
ZooKeeper stocke les métadonnées des partitions :
- Combien de partitions existent pour chaque topic ?
- Quels brokers détiennent les réplicas pour chaque partition ?
- Quel broker est le leader d’une partition ?

### Répartition des responsabilités
Lorsque ZooKeeper détecte qu’un broker rejoint ou quitte le cluster :
- Il notifie le contrôleur Kafka.
- Le contrôleur redistribue alors les partitions et réplicas de manière équilibrée.
- Par exemple, si un broker tombe, les partitions qu'il gérait sont attribuées à d'autres brokers.






# comment la latence diminue avec kraft par rapport à zookeeper

### Architecture centralisée et intégrée :

- Avec KRaft, Kafka gère directement le contrôle du cluster et les métadonnées (rôles de contrôleur et de broker combinés), éliminant la dépendance à ZooKeeper.
- Moins de communication inter-systèmes réduit le délai dans la propagation des métadonnées et la coordination des brokers.
### Propagation des métadonnées optimisée :

- KRaft utilise un log Raft dédié pour synchroniser les métadonnées entre les brokers.
- Cette synchronisation est plus rapide et évite les limitations inhérentes au modèle de ZooKeeper.

### Réduction des délais de synchronisation :

- ZooKeeper nécessite un échange de métadonnées via des watchers entre le broker et ZooKeeper, ce qui peut entraîner des latences dans des clusters avec des volumes de données élevés.

### Tolérance aux pannes améliorée :

- KRaft permet une récupération plus rapide après une panne, minimisant l'impact sur la latence des requêtes.



# Cas d'utilisation 

1. Traitement des paiements et transactions financières en temps réel :
Contexte : Utilisé dans les banques, les assurances, et la bourse.
Exemple : Lorsqu'un client effectue un paiement par carte ou une transaction boursière, les systèmes doivent traiter ces opérations immédiatement pour éviter les fraudes ou refléter les changements de marché.

2. Suivi en temps réel des véhicules et expéditions :
Contexte : Employé dans la logistique et l'industrie automobile.
Exemple : Une entreprise de livraison suit la position de ses camions en temps réel pour optimiser les itinéraires ou informer les clients de l'heure exacte de la livraison.

3. Analyse continue des données de capteurs (IoT) :
Contexte : Utilisé dans les usines, les parcs éoliens, et d'autres infrastructures industrielles.
Exemple : Un capteur dans une turbine éolienne envoie des données en temps réel pour détecter des anomalies et éviter les pannes coûteuses.

4. Réaction immédiate aux interactions des clients :
Contexte : Courant dans le commerce de détail, les hôtels, les voyages, et les applications mobiles.
Exemple : Lorsqu'un client commande un produit sur une application, le système met à jour les stocks en temps réel, déclenche la préparation de la commande, et envoie une confirmation instantanée.

5. Surveillance des patients hospitalisés :
Contexte : Utilisé dans les soins de santé pour assurer une surveillance continue.
Exemple : Les capteurs connectés aux patients en soins intensifs détectent tout changement de rythme cardiaque ou de respiration, alertant immédiatement le personnel médical en cas de problème.

6. Connexion et mise à disposition des données d’entreprise :
Contexte : Optimise la collaboration entre différentes divisions d'une organisation.
Exemple : Les données des ventes, de la logistique et du marketing sont centralisées et accessibles en temps réel pour des analyses ou décisions communes.

7. Base pour les architectures pilotées par les événements et microservices :
Contexte : Structure logicielle moderne pour les applications complexes.
Exemple : Lorsqu'un utilisateur ajoute un produit à son panier dans une application e-commerce, cet événement déclenche d'autres actions, comme la mise à jour du stock ou une suggestion personnalisée.