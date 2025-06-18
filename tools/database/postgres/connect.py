# Importing Libraries.
import os
# Importing DB Libraries.
from sqlalchemy import create_engine, text, and_
from sqlalchemy.orm import sessionmaker, declarative_base
# Loading the environment variables.
from config import load_env_vars
load_env_vars()

# Define your PostgreSQL database URL
host = os.getenv("host").replace("/", "%2F").replace("@", "%40")
database = os.getenv("database").replace("/", "%2F").replace("@", "%40")
username = os.getenv("username").replace("/", "%2F").replace("@", "%40")
password = os.getenv("password").replace("/", "%2F").replace("@", "%40")
port = os.getenv("port")

__DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create an engine
__engine = create_engine(__DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(bind=__engine, autocommit=False, autoflush=False)

# Define a base class for models
Base = declarative_base()