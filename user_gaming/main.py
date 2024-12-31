import asyncio
import json
import logging
import os
import random
import sys
from datetime import datetime
from dotenv import load_dotenv
import mysql.connector
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def send_pop_message(username):
    """Send pop message to websocket server for a given user"""
    uri = f"{os.getenv('WEBSOCKET_URI')}/?token={os.getenv('WEBSOCKET_TOKEN')}&username={username}"
    headers = {"Origin": "https://www.popcoin.game"}
    message = {
        "type": "markPop",
        "value": json.dumps({"count": os.getenv("POP_COUNT"), "username": username}),
    }

    try:
        async with websockets.connect(uri, additional_headers=headers) as websocket:
            await websocket.send(json.dumps(message))
            logger.info(f"Message sent for user {username}")
            response = await websocket.recv()
            # logger.info(f"Response received for user {username}: {response}")
            logger.info(f"Successfully processed user {username}")
            return True
    except Exception as e:
        logger.error(f"Error processing user {username}: {str(e)}")
        return False


def get_users():
    """Get list of users from database"""
    try:
        conn = mysql.connector.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT public_address as username FROM pop.user WHERE satisified_requirement = 'MARKETING_USER'"
            )
            users = [row[0] for row in cur.fetchall()]

        conn.close()
        return users
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        sys.exit(1)


def calculate_delay(user_count):
    """Calculate delay between requests based on user count"""
    # 24 hours in seconds
    total_time = 24 * 60 * 60
    # Maximum delay is total time divided by user count
    max_delay = min(total_time / user_count, 60)  # Cap at 60 seconds
    # Get a random delay between 0.5 and max_delay
    return random.uniform(0.5, max_delay)


async def process_users(users):
    """Process all users with appropriate delays"""
    for user in users:
        # Send message to websocket
        success = await send_pop_message(user)

        if success:
            # Calculate and apply delay only after successful processing
            delay = calculate_delay(len(users))
            logger.info(f"Waiting {delay:.2f} seconds before next user")
            await asyncio.sleep(delay)
        else:
            # Shorter delay for failed attempts
            await asyncio.sleep(0.5)


async def main():
    """Main function to orchestrate the process"""
    try:
        logger.info("Starting user gaming automation")

        # Get users from database
        users = get_users()
        logger.info(f"Found {len(users)} users to process")

        if not users:
            logger.warning("No users found to process")
            return

        # Process users
        await process_users(users)

        logger.info("Completed user gaming automation")
    except Exception as e:
        logger.error(f"Fatal error in main process: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
