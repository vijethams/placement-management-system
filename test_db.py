import psycopg
import os
from dotenv import load_dotenv

load_dotenv()
uri = os.getenv('SQLALCHEMY_DATABASE_URI')
print(f"Testing URI: {uri}")

# Direct psycopg needs postgresql:// not postgresql+psycopg://
if uri:
    direct_uri = uri.replace('postgresql+psycopg://', 'postgresql://')
    print(f"Direct URI: {direct_uri}")

    try:
        conn = psycopg.connect(direct_uri)
        print("Connection successful!")
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")
else:
    print("SQLALCHEMY_DATABASE_URI not found in environment.")
