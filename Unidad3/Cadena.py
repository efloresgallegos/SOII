import hashlib
data = "Transacción A -> B"
prev_hash = "0000"
hash = hashlib.sha256((data + prev_hash).encode()).hexdigest()
print(hash)
