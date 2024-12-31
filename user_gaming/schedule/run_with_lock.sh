#!/bin/bash
flock -n /tmp/user_gaming.lock python3 /home/augustine_chirra/pop-marketing-users/user_gaming/main.py 
