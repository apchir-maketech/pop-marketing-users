# User Creation Automation

## Steps

Create a simple python script that does the following:

1. Generate new Ethereum account using `eth_account` library

```python
>>> from eth_account import Account
>>> new_account = Account.create()
>>> new_account.address
'0xF698f4317f94E5dE324cf4d883d675AD005ade20'
>>> new_account._private_key.hex()
'0x12db259f52ee840bb06e9607fa2c2f3c40ed35fb455204191d5917af7e503de7'
```

2. Encrypt the private key using Fernet encryption. Get the `ENCRYPTION_KEY` from the environment variable.

```python
from cryptography.fernet import Fernet

def encrypt_message(plain_text: str, key: bytes):
    try:
        cipher = Fernet(key)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return encrypted_text
    except Exception as e:
        logger.info("encryption failed")
        logger.error(e)
        return None
```

3. Upload the encrypted private key to GCS. Get the `GCS_BUCKET_NAME` and `GCS_BASE_PATH` from the environment variables. Use `address` as the filename.

```python
from google.oauth2 import service_account
from google.cloud import storage
from datetime import datetime as dt
from config.logger_config import custom_logger as logger


def upload_string_to_gcs(
    string: str,
    bucket_name: str,
    base_path: str,
    filename: str = None,
    creds_file_path: str = None,
):
    # destination_blob_name
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

        # Get the GCS bucket
        bucket = storage_client.bucket(bucket_name)

        # Create a new blob and upload the string
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(string)
        return "success", bucket_name, destination_blob_name
    except Exception as e:
        logger.error(e)
        return "failed", bucket_name, destination_blob_name
```

4. Create a new user in the database which is a MySQL database. Get the `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` from the environment variables.

```sql
INSERT INTO `pop`.`user` (`public_address`, `satisified_requirement`) VALUES ('0xF698f4317f94E5dE324cf4d883d675AD005ade20', 'MARKETING_USER');
```

5. Increment the `user_count` in the redis. Get the `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` from the environment variables. The keyname is in the following format: `total_users_count:ON_{Current_Date_In_YYYY-MM-DD_Format}`.

```
Example key: total_users_count:ON_2024-12-30
```
