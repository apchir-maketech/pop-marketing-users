#!/bin/bash
flock -n /tmp/user_gaming.lock /home/augustine_chirra/pop-marketing-users/user_gaming/venv/bin/python /home/augustine_chirra/pop-marketing-users/user_gaming/main.py 
