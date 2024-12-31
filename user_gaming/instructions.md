# User Game-Play Automation

## Steps

1. Get the list of users from the database. Get the `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` from the environment variables.

```sql
select public_address as username FROM pop.user where satisified_requirement = 'MARKETING_USER';
```

2. For each user, send a message to the websocket server

Example code for user `0x3180c3E3996FA66bD8e70b557A051D997Aa853Bf`:

```python
import asyncio
import websockets
import json

headers = {"Origin": "https://www.popcoin.game/"}
uri = "wss://pop-backend-3sca73pgwa-uc.a.run.app/?token=aaba08f8a5e7c436d0639b5a085395687effe620&username=0x3180c3E3996FA66bD8e70b557A051D997Aa853Bf"

message = {"type": "markPop","value": json.dumps({"count":100,"username": "0x3180c3E3996FA66bD8e70b557A051D997Aa853Bf"})}
message_json = json.dumps(message)
headers = {"Origin": "https://www.popcoin.game"}

async def send_pop_message():
     async with websockets.connect(uri, additional_headers=headers) as websocket:
             await websocket.send(str(message_json))
             print("Message sent")
             response = await websocket.recv()
             print("Response received: ", response)

asyncio.get_event_loop().run_until_complete(send_pop_message())
```

Sample response:

```json
{
  "username": "0x3180c3E3996FA66bD8e70b557A051D997Aa853Bf",
  "markPop": { "userPops": { "popCountToday": 200, "remainingPopCountToday": { "todaysPops": 200, "remainingPops": 100, "dailyFreeBubbleQuota": 300, "extraBubbles": 0 } } },
  "redeemableCountUpdate": { "redeemableCount": 200 },
  "globalPopCountUpdate": { "globalPopCount": 1945851 },
  "userCountsUpdate": { "userCounts": { "alltimeUsersCount": 1475, "currentRollingDayActiveUsersCount": 131, "currentActiveUsersCount": 17 } }
}
```

3. Add a delay of minimum 0.5 seconds between each user. Maxium delay should be based on the number of users. The goal is to fit all the users in 24 hours while avoiding overwhelming the websocket server. If the websocket server is overwhelmed, the script should log the error and continue with the next user.

4. Create a cron job to run the script once daily at 00:00 UTC.

5. We need a way to make sure:

   - a. The job restarts if it fails.
   - b. The job does not run if it is already running.

6. Important considerations:

   - It is okay to NOT cover all the users in a day if there are a lot of users.
   - But it is not okay to be idle for the entire day if the job fails for any reason.
   - It is okay to run the job for the same user multiple times in a day, if needed.
   - No need to check if the user has already been processed.
