import hashlib

def int_to_uint(x, bit_width):
    return x + 2**(bit_width-1)
  
def str_to_uint(str):
    # SHA-256 hashing, then use "xor" to reduce to 32 bits
    result = hashlib.sha256(str.encode()).hexdigest()
    ret = 0
    for i in range(0, 64, 8):
        ret ^= int(result[i:i+8], 16)
    return ret

if __name__ == "__main__":
    # test
    print(str_to_uint("sdahjksdsahjkddsadhjksa"))