import psycopg2
import base64
import pickle
from large_estimates import HyperLogLog  # 👈 Our accurate HLL

def serialize_hll(hll_obj):
    """Serialize HyperLogLog to base64 (Postgres style)"""
    binary = pickle.dumps(hll_obj)  # or struct.pack if you want exact C memory layout
    return base64.b64encode(binary).decode('ascii')

def deserialize_hll(b64_data):
    """Deserialize HyperLogLog from base64"""
    binary = base64.b64decode(b64_data)
    return pickle.loads(binary)

try:
    conn = psycopg2.connect(
        dbname="hll_test",
        user="postgres",
        password="AIML",  
        host="localhost",
        port=5432
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    print(f"Failed to connect to DB: {e}")
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

hll = HyperLogLog(b=14)
for i in range(50_000):
    hll.add(f"item{i}")

estimate_before = hll.estimate()
print("Estimate before storing:", estimate_before)

try:
    b64_data = serialize_hll(hll)
    cur.execute("INSERT INTO hll_counters (label, hll_data) VALUES (%s, %s)",
                ("items", b64_data))
    conn.commit()
    print("HLL stored in DB.")
except psycopg2.Error as e:
    print(f"Failed to insert HLL: {e}")
    raise

try:
    cur.execute("SELECT hll_data FROM hll_counters WHERE label = %s", ("items",))
    row = cur.fetchone()
    if row is None:
        raise ValueError("No data found for label 'items'")
    b64_data_fetched = row[0]
    print("Fetched Base64 data:", b64_data_fetched[:50] + "...")
    hll_fetched = deserialize_hll(b64_data_fetched)
    estimate_after = hll_fetched.estimate()
    print("Estimate after fetching from DB:", estimate_after)
    if abs(estimate_before - estimate_after) > 0.001:
        print(" Warning: Estimate changed after DB round-trip!")
except psycopg2.Error as e:
    print(f" Failed to fetch from DB: {e}")
    raise

cur.close()
conn.close()
