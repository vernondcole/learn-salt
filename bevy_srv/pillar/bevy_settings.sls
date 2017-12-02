---
# salt pillar file for common values for a bevy

{% set ubuntu_version = 'xenial' %}  {# version of Ubuntu to install #}
{% set bevymaster_ip = '192.168.88.2' %}  {# main IP address of bevy master #}
{% set pxe_network_cidr = '192.168.88.0/24' %}

{# define module functions which will each minion will run periodically to send data to Salt Mine #}
mine_functions:
  network.ip_addrs: '[]'
  grains.item:
    - fqdn

#change to agree with your actual saltify test hardware machine
wol_test_machine_ip: 192.168.88.8  # the ip address of the minion machine
wol_test_mac: '00-1a-4b-7c-2a-b2'  # ethernet address of minion machine
wol_test_sender_id: bevymaster  # Salt node id of WoL transmitter

bevymaster_external_ip: {{ bevymaster_ip }}
bevymaster_vagrant_ip: 172.17.2.2  # vagrant host-only IP address of master

bevy_host_id: 'vc-ddell'  # Salt node id of Vagrant host machine
bevy_dir: '/projects/learn-salt'  # path to learn-salt directory tree
vagrant_bridge_target_network: '192.168.88.0/24'
#

dhcp_pxe_range: {{ pxe_network_cidr.split('/')[0] }}  # network for dnsmasq PXE server replies
{% set pxe_server_ip = salt['network.ip_addrs'](cidr=pxe_network_cidr)[0] %}
pxe_server_ip: {{ pxe_server_ip }}

# the pxe boot server needs a Python program to run to keep auto installed machines from looping
pxe_clearing_daemon_life_minutes: 30
pxe_clearing_port: 4545  # TCP port to sent html control to pxe_clearing_daemon

# download source of base operating system to be booted by PXE.
pxe_netboot_subdir: '{{ ubuntu_version }}'  # name for tftp server subdirectory
pxe_netboot_download_url: http://archive.ubuntu.com/ubuntu/dists/{{ ubuntu_version }}/main/installer-amd64/current/images

ubuntu_version: {{ ubuntu_version }}
# This is a list of dicts of machines to be PXE booted.
#  each should have a "tag" matching the Netboot Tags below.
pxe_netboot_configs:
  - mac: '00-1a-4b-7c-2a-b2'
    subdir: '{{ ubuntu_version }}/'  # include a trailing "/"
    tag: install
    kernel: ubuntu-installer/amd64/linux
    append: 'vga=788 initrd=ubuntu-installer/amd64/initrd.gz auto-install/enable=true preseed/url=tftp://{{ pxe_server_ip }}/preseed.files/'
#  - mac: '01-02-03-04-05-06'
#    kernel: ubuntu_image
#
# Netboot Tags...
#  This is a list of dnsmasq configuration commands.
#  Each entry is a pxe-service line to match one or more of the configs above.
#  The parameters are: tag, client system type, menu text, file to boot.
#  Client system type is one of: x86PC, IA32_EFI, X86-64_EFI, or others
# see http://www.thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html
pxe_netboot_tags:
  -  pxe-service=tag:install,x86PC,"Network install {{ ubuntu_version }}","{{ ubuntu_version }}/pxelinux"
  -  pxe-service=tag:!known,x86PC,"Default PXE menu","/pxelinux"

salt-api:  {# the api server is located using the "master" grain #}
  port: 4507  # other examples use port 8000
  eauth: pam
  username: vagrant
  password: vagrant

  tls_organization: 'My Company Name'
  tls_location: 'Somewhere, UT'
  tls_emailAddress: 'me@mycompany.test'
...
