
## Usage



##  PostgreSQL Setup

Ensure you have a database named `hll_test`, and update credentials in the scripts if needed:

```python
conn = psycopg2.connect(
    dbname="hll_test",
    user="postgres",
    password="AIML",  # <- change this
    host="localhost",
    port=5432
)
```

Tables are auto-created via:

```sql
CREATE TABLE hll_counters (
    label TEXT,
    hll_data TEXT
);
```

---
### `examples/basic_usage.py`

Demonstrates:
- Creating HLLs from labeled datasets.
- Estimating cardinalities.
- Storing and retrieving HLLs from a PostgreSQL table using base64 serialization.
- Validating that estimates remain consistent after database round-trips.

#### To run:
```bash
python -m examples.basic_usage
```

#### Key behavior:
- Four sample datasets (`fruits`, `nuts`, `animals`, `people`) are stored and fetched.
- Estimates before and after storage are compared.
- Uses `serialize_hll()` and `deserialize_hll()` to handle DB-friendly HLL formats.

---

### `examples/database_storage.py`

Demonstrates:
- Creating a high-precision HLL (`b=14`) for 50,000 items.
- Estimating cardinality.
- Creating the necessary PostgreSQL table schema.

#### To run:
```bash
python -m examples.database_storage
```

---


## Notes

- Merge only HLLs with the same `b` value.
- You can inspect the first 10 registers for debug using:
  ```python
  hll.impl.registers[:10]
  ```

---
