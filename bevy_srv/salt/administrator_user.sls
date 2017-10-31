---
# salt state file for defining a generic administrator username

staff_group:
  group:
    - present
    - name: staff

vagrant:
  group:
    - present
  user:
    - present
    - password: $6$cIiKCbvKbLcXR7FL$N08PF11jBzcRpCKNvwboW/ErEMzJ1l899LDEAbn2frCuS7mzCRDrRwgOAD4iIb9nPw9vxfLHeKxOcl2JDVx3L0
    # the default password is "vagrant"
    - enforce_password: false
    - groups:
      - staff
    - optional_groups:
      - www-data
      - dialout
      - sudo
    - require:
      - group: staff


/etc/defaults/login:
  file.append:
    - text: "UMASK=002  # create files as group-readable by default ## added by Salt"
    - makedirs: true

...
