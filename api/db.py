import mysql.connector

def get_db_connection():
    from config import Config
    
    config = {
        'host': Config.DB_HOST,
        'port': Config.DB_PORT,
        'user': Config.DB_USER,
        'password': Config.DB_PASSWORD,
        'database': Config.DB_NAME,
        'time_zone': '+05:30'
    }
    
    # TiDB Cloud requires SSL
    if Config.DB_SSL:
        config['ssl_disabled'] = False
        config['ssl_ca'] = None # mysql-connector-python will use system CA if possible
        
    return mysql.connector.connect(**config)
