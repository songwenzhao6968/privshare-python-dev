import json
from enum import Enum

class DataType(Enum): # Futher support bool and 64-bit
    UINT8 = "uint8",
    UINT16 = "uint16",
    UINT32 = "uint32",
    INT8 = "int8",
    INT16 = "int16",
    INT32 = "int32",
    STR = "str" 

class DataBase:
    def __init__(self, db_file_path):
        self.tables = {}
        with open(db_file_path) as f:
            db = json.load(f)
        for table_name, table in db.items():
            field = table["schema"]["field"]
            schema = {}
            for name, type in field:
                schema[name] = DataType(type)
            data = table["data"]
            table = schema, data
            self.tables[table_name] = table