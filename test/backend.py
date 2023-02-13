from dotenv import load_dotenv
import os

# by default .env will be loaded
load_dotenv()
# if we had another file called .env2
# we could load it using
# load_dotenv(".env2")

# now we can use os.getenv as before:
print("***************************************************")
print(os.getenv("access_key"))
print(os.getenv("secret_key"))