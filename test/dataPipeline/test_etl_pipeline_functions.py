import pytest
from unittest.mock import patch, Mock
import requests
import pandas as pd
import psycopg2
from airflow.models import DagBag
from data_ingestion.dags.data_ingestion_dag import extract_data, transform_data, load_data

# Fixture pour initialiser le DAG
@pytest.fixturecl
def dag():
    # Chargement du DAG depuis Airflow
    return DagBag().get_dag('moovitamix_etl')

# Test pour vérifier que l'extraction de données depuis l'API fonctionne correctement
@patch('requests.get')
def test_extract_data_success(mock_get):
    """
    Teste que les données sont extraites correctement depuis l'API FastAPI.
    """
    # Simulation de la réponse de l'API
    mock_get.return_value.json.return_value = {
        'items': [
            {'id': 1, 'name': 'test_track', 'artist': 'test_artist', 'songwriters': 'test_songwriter', 'duration': '3:30'},
        ]
    }
    # Appel de la fonction extract_data
    data = extract_data()
    # Vérifications que les données extraites contiennent les informations attendues
    assert 'tracks' in data
    assert len(data['tracks']) == 1
    assert data['tracks'][0]['name'] == 'test_track'

# Test pour vérifier la gestion des erreurs réseau lors de l'extraction des données
@patch('requests.get')
def test_extract_data_network_error(mock_get):
    """
    Teste que extract_data gère les exceptions réseau correctement.
    """
    # Simulation d'une exception réseau
    mock_get.side_effect = requests.exceptions.RequestException("Network error")
    # Vérifie que l'exception est bien levée
    with pytest.raises(requests.exceptions.RequestException, match="Network error"):
        extract_data()

# Test pour vérifier que la transformation des données fonctionne correctement
@patch('airflow.models.TaskInstance.xcom_pull', return_value={
    'tracks': [{'id': 1, 'name': 'test_track', 'artist': 'test_artist', 'songwriters': 'test_songwriter', 'duration': '3:30'}],
    'users': [{'id': 1, 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'}],
    'listen_history': [{'user_id': 1, 'items': [1], 'created_at': "2024-01-01T00:00:00"}]
})
def test_transform_data(mock_xcom_pull):
    """
    Teste la transformation des données extraites.
    """
    # Création d'un mock pour TaskInstance et configuration de xcom_pull
    mock_ti = Mock()
    mock_ti.xcom_pull.return_value = mock_xcom_pull.return_value
    # Transformation des données
    transformed_data = transform_data(mock_ti)
    # Vérifications que les données transformées correspondent à ce qui est attendu
    assert len(transformed_data['tracks']) == 1
    assert transformed_data['tracks'][0]['name'] == 'test_track'
    assert len(transformed_data['users']) == 1
    assert transformed_data['listen_history'][0]['user_id'] == 1

# Test pour vérifier que le chargement des données dans PostgreSQL fonctionne correctement
@patch('psycopg2.connect')
@patch('airflow.models.TaskInstance.xcom_pull', return_value={
    'tracks': [{'id': 1, 'name': 'test_track', 'artist': 'test_artist', 'songwriters': 'test_songwriter', 'duration': '3:30'}],
    'users': [{'id': 1, 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'}],
    'listen_history': [{'user_id': 1, 'items': [1], 'created_at': "2024-01-01T00:00:00"}]
})
def test_load_data_success(mock_xcom_pull, mock_connect):
    """
    Teste que les données transformées sont correctement chargées dans PostgreSQL.
    """
    # Création de mocks pour la connexion et le curseur de base de données
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Création d'un mock pour TaskInstance avec xcom_pull configuré
    mock_ti = Mock()
    mock_ti.xcom_pull.return_value = mock_xcom_pull.return_value

    # Chargement des données
    load_data(mock_ti)

    # Vérifications que les exécutions SQL et le commit ont bien été appelés
    assert mock_cursor.execute.call_count == 3
    mock_conn.commit.assert_called_once()

# Test pour vérifier la gestion des erreurs de connexion à la base de données
@patch('psycopg2.connect', side_effect=psycopg2.OperationalError("Connection error"))
def test_load_data_connection_error(mock_connect):
    """
    Teste que load_data lève une erreur OperationalError en cas d'erreur de connexion à la base de données.
    """
    # Création d'un mock pour TaskInstance
    mock_ti = Mock()
    # Vérifie que l'exception OperationalError est levée
    with pytest.raises(psycopg2.OperationalError, match="Connection error"):
        load_data(mock_ti)

if __name__ == "__main__":
    pytest.main()
