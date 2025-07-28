'''to run without moving the hyerloglog folder use command
python -m examples.database_storage'''
import psycopg2
import base64
import pickle
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import *


try:
    conn = psycopg2.connect(
        dbname="hll_test", # change
        user="postgres", #change
        password="AIML",   #change
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    print(f"Failed to connect to DB: {e}")
    raise

try:
    cur.execute("DROP TABLE IF EXISTS hll_counters") # change
    cur.execute("""
        CREATE TABLE hll_counters (
            label TEXT,
            hll_data TEXT
        )
    """)
    conn.commit()
except psycopg2.Error as e:
    print(f"Failed to create table: {e}")
    raise

hll = HyperLogLog(b=14)
for i in range(50_000):
    hll.add(f"item{i}")

estimate = hll.estimate()
print("Estimate:", estimate)
