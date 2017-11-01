---
# this salt pillar file will define basic access codes for all bevy machines (including the master)
## This file managed by SaltStack. Any changes may be overwritten.

# linux username to own files and run user jobs on server machines...
my_linux_user: vernoncole
#
my_linux_uid: ''
my_linux_gid: ''
#
# Linux password hash for interactive user
linux_password_hash: "$6$QZC4cUpLjfff/g6s$bVY3t70S06MW22sTkUWF8YlgUxdAv3UQvPFsYi9TjZE9TjYhgW62T8moTxRMVHwP/MVa0VLOe7AAYkpJ6srwM/"
#
force_linux_user_password: True
...
