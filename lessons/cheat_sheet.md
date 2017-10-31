## SaltStack control cheat-sheet

#### on Linux masters, add "sudo" to all of the following commands

Look at minion keys:
`salt-key -L`

Accept a not-yet-accepted minion:
`salt-key -A <minion_id>`

Test all minions:
`salt \* test.ping`

Create and start a new minion:
`salt-cloud -p <minion_id>`

Destroy a minion:
`salt-cloud --destroy <minion_id>`

Control the salt master on your own workstation (on Linux):

    `sudo salt-call --local service.stop salt-master`
    `sudo salt-call --local service.restart salt-master`

To restart your salt-master on OS-x, rerun the script:

'sh make_my_workstation_a_master.sh'

