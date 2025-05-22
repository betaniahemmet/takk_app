# test_env.py
import os

from dotenv import load_dotenv

load_dotenv(".env.development")

print("BASE_URL =", os.getenv("BASE_URL"))
