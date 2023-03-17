import sys
import os
import json
from database import DataBase
from secure_query import SecureQuery
import he

example_dir = "./examples/demo"

HE = he.create_he()
HE_pub = he.get_he_pub(key_file_loc)
secure_query = SecureQuery()

with open(os.path.join(example_dir, "config.json")) as f:
    config = json.load(f)
db = DataBase(config["servers"]["provider_1"]["database_file_loc"])
secure_result = run_secure_query(db, secure_query)
