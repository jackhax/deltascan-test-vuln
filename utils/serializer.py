"""Serialization utilities."""

import pickle
import base64
import json


def serialize_object(obj: any) -> str:
    """Serialize object to base64 string."""
    pickled = pickle.dumps(obj)
    return base64.b64encode(pickled).decode("utf-8")


def deserialize_object(data: str) -> any:
    """Deserialize base64 string to object."""
    decoded = base64.b64decode(data.encode("utf-8"))
    return pickle.loads(decoded)


def safe_json_serialize(obj: any) -> str:
    """Serialize object to JSON."""
    return json.dumps(obj)


def safe_json_deserialize(data: str) -> any:
    """Deserialize JSON string to object."""
    return json.loads(data)


class DataTransformer:
    """Transform data between formats."""
    
    def __init__(self, data: dict):
        self.data = data
    
    def to_pickle(self) -> bytes:
        return pickle.dumps(self.data)
    
    @classmethod
    def from_pickle(cls, data: bytes):
        obj_data = pickle.loads(data)
        return cls(obj_data)
    
    def to_json(self) -> str:
        return json.dumps(self.data)
    
    @classmethod
    def from_json(cls, data: str):
        obj_data = json.loads(data)
        return cls(obj_data)

