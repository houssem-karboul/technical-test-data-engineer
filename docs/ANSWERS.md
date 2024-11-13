# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

# README: Configuration of Python and Docker Environment

# Introduction
# This guide will set up a Python virtual environment, configure Docker for Airflow, 
# and run services with Docker Compose.

# Prerequisites
# Python 3.3+ : Check installation
python --version

# Docker: Ensure Docker is installed and running

# Steps

# 1. Create a Python Virtual Environment
# Create the environment
python -m venv <env_name>

# Activate the environment
# On Windows:
<env_name>\Scripts\activate

# On macOS/Linux:
source <env_name>/bin/activate

# 2. Prepare Environment for Docker
# Check available memory
docker run --rm "debian:bookworm-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'

# Configure Airflow user (Linux only)
mkdir -p ./dags ./logs ./plugins ./config
echo -e "AIRFLOW_UID=$(id -u)" > .env

# For other systems, ignore the AIRFLOW_UID warning or manually create .env
# with the following content:
# AIRFLOW_UID=50000

# 3. Run Docker Compose
# Navigate to the directory with docker-compose.yml
cd src/data_ingestion

# Start services
docker compose up


# 4.Finally, you would be able to access PostgreSQL and Apache Airflow through the browser using these links:
# Access Airflow at:
http://localhost:8080/home

# Access PostgreSQL at:
http://127.0.0.1:5050/browser/

Ici, nous devons configurer les connexions à la base de données dans PostgreSQL et Apache Airflow. J'enverrai à M. Dave une démonstration de la solution ainsi qu'un guide pour configurer le DAR.

## Questions (étapes 4 à 7)

### Étape 4

Schéma de la Base de Données : Tables Créées 
  
tracks
id (INTEGER, PRIMARY KEY)
name (VARCHAR(255))
artist (VARCHAR(255))
songwriters (VARCHAR(255))
duration (VARCHAR(10))
genres (VARCHAR(255))
album (VARCHAR(255))
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

users
id (INTEGER, PRIMARY KEY)
first_name (VARCHAR(255))
last_name (VARCHAR(255))
email (VARCHAR(255))
gender (VARCHAR(50))
favorite_genres (VARCHAR(255))
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

Table listen_history
id (SERIAL, PRIMARY KEY)
user_id (INTEGER, FOREIGN KEY REFERENCES users(id))
items (INTEGER[])
created_at (TIMESTAMP)
updated_at (TIMESTAMP)

Je recommande PostgreSQL pour sa robustesse, sa flexibilité et ses fonctionnalités avancées. Il assure l'intégrité référentielle et offre de bonnes performances pour gérer efficacement les données musicales et les utilisateurs :

- Robustesse et Flexibilité : PostgreSQL est connu pour sa capacité à gérer des volumes importants de données tout en offrant une grande flexibilité dans la définition des types de données et des relations entre les tables. Cela permet d'adapter le schéma aux besoins spécifiques des données musicales et des utilisateurs.
- Intégrité Référentielle : Grâce aux clés étrangères, PostgreSQL assure l'intégrité référentielle entre les tables, ce qui est crucial pour maintenir la cohérence des données entre les utilisateurs et leur historique d'écoute.
- Performance : PostgreSQL est optimisé pour les opérations complexes et peut gérer efficacement les requêtes sur plusieurs tables grâce à son moteur SQL performant.

### Étape 5

Pour suivre la santé du pipeline de données dans son exécution quotidienne, l'utilisation d'Apache Airflow s'avère très efficace. déja la solution implémenter dans les étapes 1-3 permet cela. 
Airflow permet de gérer et de surveiller les pipelines de données via une interface web intuitive, où vous pouvez suivre l'exécution des DAGs (Directed Acyclic Graphs) qui orchestrent ces pipelines.

-Méthode de Surveillance
Interface Web : Airflow offre un tableau de bord complet qui permet de visualiser en temps réel l'état des tâches, les dates d'exécution, la durée et les journaux générés lors de l'exécution des tâches. Cela facilite le dépannage rapide et l'optimisation des performances25.
Journaux et Notifications : Chaque tâche possède ses propres journaux accessibles depuis l'interface, ce qui est crucial pour identifier les échecs ou les goulets d'étranglement dans le pipeline. De plus, Airflow permet de configurer des alertes et des notifications en cas de succès ou d'échec des tâches, garantissant ainsi une réponse rapide aux problèmes12.

- Métriques Clés à Surveiller
Taux de Succès des Tâches : Suivre le pourcentage de tâches réussies par rapport aux tâches échouées.
Durée d'Exécution des Tâches : Mesurer le temps pris par chaque tâche pour s'assurer qu'il n'y a pas de retards significatifs.
État des DAGs : Vérifier régulièrement l'état global des DAGs pour s'assurer qu'ils s'exécutent comme prévu.
Utilisation des Ressources : Surveiller l'utilisation CPU et mémoire pour anticiper les besoins en scalabilité.
En résumé, Apache Airflow fournit une plateforme robuste pour surveiller la santé des pipelines de données, avec une visibilité complète sur leur exécution grâce à ses fonctionnalités avancées de journalisation et de notification.

### Étape 6 + 7 

Pour une automatisation complète du calcul des recommandations ainsi que de son réentraînement, je propose une architecture en plusieurs couches, chacune dédiée à une étape clé du processus :

1. Stockage des Données :

Base de Données Opérationnelle : Utiliser une base de données dédiée (par exemple, PostgreSQL) pour stocker les données brutes issues de l'API (chansons, utilisateurs, historiques d'écoute) qui alimente en continu le système.
Data Lake : Créer un data lake (ex. S3 ou Google Cloud Storage) pour stocker les données transformées et enrichies, prêtes à être utilisées pour l'entraînement et la prédiction des recommandations.
2. Traitement des Données :

Nettoyage et Transformation : Mettre en place un pipeline de nettoyage (gestion des valeurs manquantes, correction d'anomalies, etc.) et de transformation (feature engineering) avec un outil comme Spark ou Pandas pour préparer les données.
Enrichissement : Ajouter des métadonnées (par ex., sur les chansons et les utilisateurs) pour augmenter la pertinence des recommandations.
Feature Store : Intégrer un feature store (ex. Feast) pour stocker les caractéristiques calculées, permettant leur réutilisation sur plusieurs modèles et réduisant les coûts de traitement.
3. Entraînement du Modèle :

Orchestration : Automatiser le processus d’entraînement avec un orchestrateur de machine learning tel que Kubeflow Pipelines ou MLflow pour gérer les workflows de bout en bout.
Retrainage Régulier : Configurer un retraitement périodique du modèle (par ex. quotidien ou hebdomadaire) pour s’ajuster aux évolutions des données et aux préférences des utilisateurs.
4. Serveur de Recommandations :

Déploiement : Déployer le modèle sur un serveur de prédiction (comme TensorFlow Serving ou TorchServe) pour des recommandations en temps réel.
API : Exposer une API pour que les recommandations soient accessibles instantanément par l'application client.
5. Suivi et Optimisation :

Monitoring : Mettre en place des métriques de performance (precision, recall, NDCG) pour évaluer et surveiller la qualité des recommandations.
Expérimentation : Utiliser A/B testing pour tester et comparer différentes versions du modèle, permettant d’optimiser continuellement les performances.
Outils Recommandés :

Orchestration : Apache Airflow, Kubeflow Pipelines, MLflow
Stockage : Data Lake (S3, Google Cloud Storage), Base de données relationnelle (PostgreSQL, MySQL), Feature Store (Feast)
Traitement : Spark, Dask, Pandas
Machine Learning : Scikit-learn, TensorFlow, PyTorch
Serveur de Prédiction : TensorFlow Serving, TorchServe