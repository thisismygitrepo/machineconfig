
"""Share
"""

# as per https://github.com/Luzifer/ots
# this script is pure python and connects to server to create a secret
# or use ots executable to do this job


import requests
import crocodile.file_management as fm
from crocodile.core import install_n_import
import base64
from typing import Optional


def encrypt(key: str, pwd: str):
    install_n_import(library="Crypto.Cipher", package="pycryptodome")
    # from Crypto.Cipher import AES
    # from Crypto.Hash import MD5
    AES = __import__("Crypto", fromlist=["Cipher"]).Cipher.AES
    MD5 = __import__("Crypto", fromlist=["Hash"]).Hash.MD5
    pwd_enc = pwd.encode("utf-8")
    hash_object = MD5.new(key.encode("utf-8"))
    key_digest = hash_object.digest()
    iv = b'\x00' * 16
    cipher = AES.new(key_digest, AES.MODE_CBC, iv)
    pad = 16 - (len(pwd_enc) % 16)
    pwd_enc += bytes([pad] * pad)
    encrypted_password = cipher.encrypt(pwd_enc)
    return base64.b64encode(encrypted_password).decode("utf-8")


def share(secret: str, password: Optional[str]):
    if password is not None: encoded_secret = encrypt(password, secret)
    else: encoded_secret = secret

    url = "https://ots.fyi/api/create"

    payload = {"secret": encoded_secret}
    headers = {'Content-Type': 'application/json'}

    response = requests.post(url, json=payload, headers=headers, timeout=10)

    if response.status_code == 201:
        res = response.json()
        print(res)
        assert res["success"] is True, "Request have failed"
        share_url = fm.P(f"https://ots.fyi/#{res['secret_id']}") + (f"|{password}" if password is not None else "")
        print(repr(share_url))
        return share_url
    else:
        print("Request failed")
        raise RuntimeError(response.text)


if __name__ == "__main__":
    sc = input("Secret: ")
    pwdd = input("Password: ") or None
    share(secret=sc, password=pwdd)
