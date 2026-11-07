import os

os.environ["CLOTHMATE_ENV"] = "dev"
os.environ.pop("CLOTHMATE_API_KEY", None)