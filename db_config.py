"""
Database configuration module for CyberPatriot Runbook
"""
import mysql.connector
from mysql.connector import Error

# Database connection parameters
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Update this with your actual password
    'database': 'cyberpatriot_runbook'
}

def get_connection():
    """Establish and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def close_connection(connection):
    """Close the database connection"""
    if connection and connection.is_connected():
        connection.close()
