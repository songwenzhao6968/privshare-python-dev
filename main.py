import json
import myutil
from database import DataBase
from sql_parser import Query
from secure_query import SecureQuery
import he

config_dir = "./examples/demo/config.json"
with open(config_dir) as f:
    config = json.load(f)
debug = config["debug"]

# Client: Encrypt and send the query to the data provider
sql = "SELECT SUM(deposit) FROM t_deposit WHERE amount < 18 OR user_name = \"Alice\""
query = Query(sql)
with open(config["tables"][query.concerned_table]["schema_file_loc"]) as f:
    null_data_db = DataBase.deserialize_from_json(json.load(f))
    schema = null_data_db[query.concerned_table].schema

HE = he.create_he_object(config["he"])
secure_query = SecureQuery(query, schema, HE, config["compile"], debug)
pub_keys_bytes = he.save_public_to_bytes(HE)
secure_query_dump, ciphers_bytes = secure_query.dump()
if debug["output_secure_execution_tree"]: 
    print(secure_query_dump)

# Data Provider: Process encrypted query
with open(config["servers"]["provider_1"]["database_file_loc"]) as f:
    db = DataBase.deserialize_from_json(json.load(f))

HE_pub = he.load_public_from_bytes(pub_keys_bytes)
secure_query = SecureQuery.from_dump(secure_query_dump, ciphers_bytes, HE_pub)
secure_result = secure_query.process(db, HE_pub, debug)

# Client: Receive encrypted query result and decrypt
ind = HE.decryptInt(secure_result[0])
print("Result rows:", ind.nonzero())

if debug["timing"]:
    myutil.write_event_times()
