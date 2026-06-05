import psycopg2

try:
    print("Connecting to Supabase Connection Pooler...")
    conn = psycopg2.connect(
        "postgresql://postgres.mtnqaokypypsjhoxmcch:P6UffnvAQpvccvUI@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres", 
        connect_timeout=10
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
