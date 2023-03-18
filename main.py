import sys
import os
import json
from database import DataBase, Schema
from sql_parser import Query
from secure_query import SecureQuery
import he

def run_secure_query(db: DataBase, secure_query: SecureQuery):
    pass

example_dir = "./examples/demo"
with open(os.path.join(example_dir, "config.json")) as f:
    config = json.load(f)

# Client View
sql = ""
schema = Schema() # ?
query = Query(sql)

HE = he.create_he_object(config["he"])
secure_query = SecureQuery(query, schema, HE, config["execution"])
pub_keys_bytes = he.save_public_to_bytes(HE)
secure_query_dump, ciphers_bytes = secure_query.dumps()

# Data Provider View
db = DataBase(config["servers"]["provider_1"]["database_file_loc"])

HE_pub = he.load_public_from_bytes(pub_keys_bytes)
secure_query = SecureQuery.from_dump(secure_query_dump, ciphers_bytes, HE_pub)
run_secure_query(db, secure_query)
