import base64
import pickle

def serialize_hll(hll_obj: object) -> str:
    """Serialize HyperLogLog to base64 string"""
    binary = pickle.dumps(hll_obj)
    return base64.b64encode(binary).decode('ascii')

def deserialize_hll(b64_data: str) -> object:
    """Deserialize HyperLogLog from base64 string"""
    binary = base64.b64decode(b64_data)
    return pickle.loads(binary)
