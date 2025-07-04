from werkzeug.security import generate_password_hash
import json

# Cambia estos valores:
username = "admin"
password = "admin123"

password_hash = generate_password_hash(password)

user_data = [{
    "id": 1,
    "username": username,
    "password_hash": password_hash
}]

with open("users.json", "w", encoding="utf-8") as f:
    json.dump(user_data, f, indent=4)

print("Usuario creado:", username)
print("Password hash:", password_hash)
