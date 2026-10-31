import hashlib

def HMAC_SHA256(key, message):
    if len(key) > 64:
        key = hashlib.sha256(key).digest()
    if len(key) < 64:
        key = key + b"\x00" * (64 - len(key))
    ipad = bytes([0x36] * 64)
    opad = bytes([0x5c] * 64)
    inner_key = bytes([k ^ i for k, i in zip(key, ipad)])
    outer_key = bytes([k ^ o for k, o in zip(key, opad)])
    inner_hash = hashlib.sha256(inner_key + message).digest()
    final_hash = hashlib.sha256(outer_key + inner_hash).hexdigest()
    return final_hash
