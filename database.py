import json
from enum import Enum

class DataType(Enum):
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    STR = "str" 

class Schema:
    def __init__(self, fields, key):
        self.fields = {}
        for i, (name, type) in enumerate(fields):
            self.fields[name] = i, DataType(type)
        self.key = key

    def get_id(self, name):
        return dict[name][0]
    
    def get_type(self, name):
        return dict[name][1]

class Table:
    def __init__(self, schema, data):
        self.schema = schema
        self.data = data

class DataBase:
    def __init__(self, db_file_path):
        self.tables = {}
        with open(db_file_path) as f:
            db_json = json.load(f)
        for table_name, table_json in db_json.items():
            schema = Schema(table_json["schema"]["fields"], table_json["schema"]["key"])
            data = table_json["data"]
            self.tables[table_name] = Table(schema, data)

if __name__ == "__main__":
    db = DataBase("./examples/demo/provider_1/db.json")
    print(db.tables["t_deposit"].schema.fields)