# """Share
# """

# # as per https://github.com/Luzifer/ots
# # this script is pure python and connects to server to create a secret
# # or use ots executable to do this job

# import requests
# import base64
# from typing import Optional

# def encrypt(key: str, pwd: str):
#     print("\n🔒 Encrypting the secret...")
#     import pycryptodome
#     AES = __import__("Crypto", fromlist=["Cipher"]).Cipher.AES
#     MD5 = __import__("Crypto", fromlist=["Hash"]).Hash.MD5
#     pwd_enc = pwd.encode("utf-8")
#     hash_object = MD5.new(key.encode("utf-8"))
#     key_digest = hash_object.digest()
#     iv = b'\x00' * 16
#     cipher = AES.new(key_digest, AES.MODE_CBC, iv)
#     pad = 16 - (len(pwd_enc) % 16)
#     pwd_enc += bytes([pad] * pad)
#     encrypted_password = cipher.encrypt(pwd_enc)
#     print("✅ Encryption completed successfully!\n")
#     return base64.b64encode(encrypted_password).decode("utf-8")

# def share(secret: str, password: Optional[str]):
#     print("\n🚀 Initiating the sharing process...")
#     if password is not None:
#         print("🔑 Password provided. Encrypting the secret...")
#         encoded_secret = encrypt(password, secret)
#     else:
#         print("🔓 No password provided. Sharing the secret as is.")
#         encoded_secret = secret

#     url = "https://ots.fyi/api/create"

#     payload = {"secret": encoded_secret}
#     headers = {'Content-Type': 'application/json'}

#     print("\n🌐 Sending request to the server...")
#     response = requests.post(url, json=payload, headers=headers, timeout=10)

#     if response.status_code == 201:
#         res = response.json()
#         print("✅ Request successful! Response received.")
#         assert res["success"] is True, "❌ Request failed."
#         share_url = fm.P(f"https://ots.fyi/#{res['secret_id']}") + (f"|{password}" if password is not None else "")
#         print(f"\n🔗 Share URL: {repr(share_url)}\n")
#         return share_url
#     else:
#         print("❌ Request failed. Server returned an error.")
#         raise RuntimeError(response.text)

# if __name__ == "__main__":
#     print("\n" + "=" * 50)
#     print("🔐 Welcome to the One-Time Secret Sharing Tool")
#     print("=" * 50 + "\n")

#     sc = input("📝 Enter the secret to share: ")
#     pwdd = input("🔑 Enter a password (optional): ") or None

#     print("\n📤 Sharing the secret...")
#     share(secret=sc, password=pwdd)
#     print("🎉 Secret shared successfully!\n")
