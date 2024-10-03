import os

TOKEN = os.environ.get("DISCOTP_TOKEN")

if TOKEN is None:
    print("DISCOTP_TOKEN environment variable is not set. Please set it before running the program.")
    exit(1)