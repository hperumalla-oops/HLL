'''to run without moving the hyerloglog folder use command
python -m examples.basic_usage'''
import psycopg2
import base64
import pickle
from hyperloglog.core import HyperLogLog
from hyperloglog.serialization import *



fruits = ["apple", "banana", "orange", "grape", "mango", "banana", "apple"]
nuts = ["almond", "cashew", "walnut", "almond", "pistachio", "pecan", "walnut"]
animals = ["cat", "dog", "elephant", "tiger", "lion", "dog", "cat"]
people = ["alice", "bob", "charlie", "alice", "dave", "eve", "bob"]

datasets = {
    "fruits": fruits,
    "nuts": nuts,
    "animals": animals,
    "people": people
}

try:
    conn = psycopg2.connect(
        dbname="hll_test", #change
        user="postgres", #change
        password="AIML", #change
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    print(f"Failed to connect to database: {e}")
    raise

try:
    cur.execute("DROP TABLE IF EXISTS hll_counters")
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

for label, items in datasets.items():
    hll = HyperLogLog(b=14)  # Use high precision
    for item in items:
        hll.add(item)

    estimate_before = hll.estimate()
    print(f"\n[{label.upper()}] Estimate before storing: {estimate_before}")
    print("Registers before:", hll.impl.registers[:10], "...")  # Print first 10 for brevity

    try:
        b64_data = serialize_hll(hll)
        cur.execute("INSERT INTO hll_counters (label, hll_data) VALUES (%s, %s)",
                    (label, b64_data))
        conn.commit()
        print(f"Stored HLL for {label} in DB.")
    except psycopg2.Error as e:
        print(f"Failed to insert {label}: {e}")
        raise

for label in datasets.keys():
    try:
        cur.execute("SELECT hll_data FROM hll_counters WHERE label = %s", (label,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"No data found for label '{label}'")
        b64_data_fetched = row[0]
        print(f"\n[{label.upper()}] Fetched base64 data (first 50 chars): {b64_data_fetched[:50]}...")
        hll_fetched = deserialize_hll(b64_data_fetched)
        estimate_after = hll_fetched.estimate()
        print(f"Estimate after fetching from DB: {estimate_after}")
        if abs(estimate_before - estimate_after) > 0.001:
            print("Warning: Estimate changed after DB round-trip!")
    except (psycopg2.Error, ValueError, Exception) as e:
        print(f"Error for {label}: {e}")

try:
    cur.close()
    conn.close()
except psycopg2.Error as e:
    print(f"Failed to close DB connection: {e}")
    raise
