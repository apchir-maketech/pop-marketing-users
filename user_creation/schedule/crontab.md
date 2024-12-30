# Here are a few crontab configurations you can use (choose one)

## Option A - Run every 7-8 minutes (approximately 200 times per day):

```sh
# Run approximately every 7-8 minutes (*/7 would be 205 times/day)
*/7 * * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1
```

## Option B - Run with different frequencies during peak/off-peak hours:

```sh
# Run every 5 minutes during peak hours (8 AM - 8 PM)
*/5 8-20 * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1

# Run every 10 minutes during off-peak hours
*/10 0-7,21-23 * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1
```

## Option C - Run with varying frequencies throughout the day:

```sh
# Every 5 minutes during business hours
*/5 9-17 * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1

# Every 8 minutes during evening
*/8 18-23 * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1

# Every 10 minutes during early morning
*/10 0-8 * * * /home/augustine_chirra/pop-marketing-users/user_creation/schedule/run_with_random_delay.sh >> /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log 2>&1
```

# Setup crontab

```sh
crontab -e
```

Then paste your chosen configuration.

# Monitor

```sh
tail -f /home/augustine_chirra/pop-marketing-users/user_creation/schedule/cron.log
```
