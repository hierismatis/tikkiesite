import hashlib

def password_hasher(password):
	return hashlib.sha256(password.encode('utf-8')).hexdigest()