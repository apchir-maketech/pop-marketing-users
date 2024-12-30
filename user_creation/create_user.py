import os
from dotenv import load_dotenv
from datetime import datetime as dt
from datetime import timezone
from datetime import UTC
from eth_account import Account
from cryptography.fernet import Fernet
from google.cloud import storage
from google.oauth2 import service_account
import mysql.connector
import redis
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def encrypt_message(plain_text: str, key: bytes):
    """Encrypt a message using Fernet encryption"""
    try:
        cipher = Fernet(key)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return encrypted_text
    except Exception as e:
        logger.info("encryption failed")
        logger.error(e)
        return None


def upload_string_to_gcs(
    string: str,
    bucket_name: str,
    base_path: str,
    filename: str = None,
    creds_file_path: str = None,
):
    """Upload a string to Google Cloud Storage"""
    current_timestamp = f'{dt.now().strftime("%Y%m%dT%H%M%S")}'
    destination_blob_name = (
        f"{base_path}/{filename}" if filename else f"{base_path}/{current_timestamp}"
    )
    try:
        if creds_file_path:
            credentials = service_account.Credentials.from_service_account_file(
                creds_file_path
            )
            storage_client = storage.Client(credentials=credentials)
        else:
            storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(string)
        return "success", bucket_name, destination_blob_name
    except Exception as e:
        logger.error(e)
        return "failed", bucket_name, destination_blob_name


def create_user_in_db(public_address: str):
    """Create a new user in MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
        )

        cursor = connection.cursor()
        query = """
            INSERT INTO `pop`.`user` 
            (`public_address`, `satisified_requirement`) 
            VALUES (%s, %s)
        """
        cursor.execute(query, (public_address, "MARKETING_USER"))
        connection.commit()
        return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False
    finally:
        if "connection" in locals() and connection.is_connected():
            cursor.close()
            connection.close()


def increment_user_count():
    """Increment user count in Redis"""
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=os.getenv("REDIS_DB"),
        )

        current_date = dt.now(dt.timezone.utc).strftime("%Y-%m-%d UTC")
        key = f"total_users_count:ON_{current_date}"

        redis_client.incr(key)
        return True
    except Exception as e:
        logger.error(f"Redis error: {e}")
        return False


def main():
    try:
        # 1. Generate new Ethereum account
        new_account = Account.create()
        address = new_account.address
        private_key = new_account._private_key.hex()

        # 2. Encrypt private key
        encryption_key = os.getenv("ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("ENCRYPTION_KEY environment variable not set")

        encrypted_private_key = encrypt_message(
            private_key, key=bytes(encryption_key, "ascii")
        )
        if not encrypted_private_key:
            raise ValueError("Failed to encrypt private key")

        # 3. Upload to GCS
        gcs_bucket = os.getenv("GCS_BUCKET_NAME")
        gcs_base_path = os.getenv("GCS_BASE_PATH")
        if not all([gcs_bucket, gcs_base_path]):
            raise ValueError("GCS environment variables not set")

        status, bucket, path = upload_string_to_gcs(
            encrypted_private_key.decode(), gcs_bucket, gcs_base_path, filename=address
        )
        if status != "success":
            raise ValueError("Failed to upload to GCS")

        # 4. Create user in database
        if not create_user_in_db(address):
            raise ValueError("Failed to create user in database")

        # 5. Increment user count in Redis
        if not increment_user_count():
            raise ValueError("Failed to increment user count in Redis")

        logger.info(f"Successfully created user with address: {address}")
        return address

    except Exception as e:
        logger.error(f"Error in user creation process: {e}")
        raise


if __name__ == "__main__":
    main()
