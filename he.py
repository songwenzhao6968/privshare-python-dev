import json
import numpy as np
from Pyfhel import Pyfhel, PyCtxt

def create_he_object():
    HE = Pyfhel()
    bfv_params = {
        'scheme': 'BFV',
        'n': 2**14,      
        't_bits': 18,
        'sec': 128,        
    }
    HE.contextGen(**bfv_params)
    HE.keyGen()
    HE.rotateKeyGen()
    HE.relinKeyGen()
    return HE

def serialize_pub_to_json(HE):
    return

def deserialize_pub_from_json(json_he):
    return

HE = create_he_object()
arr = np.arange(2**14)
ctxt1 = HE.encryptInt(arr)

json_he = {
    "context": HE.to_bytes_context(),
    "public_key": HE.to_bytes_public_key()
}
HE_pub = Pyfhel()
HE_pub.from_bytes_context(json_he["context"])
HE_pub.from_bytes_public_key(json_he["public_key"])
HE_pub.rotateKeyGen()
HE_pub.relinKeyGen()

print(ctxt1)
ctxt2 = PyCtxt(pyfhel=HE_pub)
ctxt1_str = ctxt1.to_bytes().decode('ascii')
ctxt2.from_bytes(bytes(ctxt1_str, "utf-8"))
print(ctxt2)
ctxt3 = PyCtxt(copy_ctxt=ctxt1)
print(ctxt3)

print(HE_pub.decryptInt(ctxt1))