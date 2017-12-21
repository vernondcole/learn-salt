#!/usr/bin/env python3
"""generate and print an RFC-4193 compliant random network identification"""
# from [RFC-4193](https://tools.ietf.org/html/rfc4193)
# 3.2.2.  Sample Code for Pseudo-Random Global ID Algorithm
#
#    The algorithm described below is intended to be used for locally
#    assigned Global IDs.  In each case the resulting global ID will be
#    used in the appropriate prefix as defined in Section 3.2.
#
#      1) Obtain the current time of day in 64-bit NTP format [NTP].
#
#      2) Obtain an EUI-64 identifier from the system running this
#         algorithm.  If an EUI-64 does not exist, one can be created from
#         a 48-bit MAC address as specified in [ADDARCH].  If an EUI-64
#         cannot be obtained or created, a suitably unique identifier,
#         local to the node, should be used (e.g., system serial number).
#
#      3) Concatenate the time of day with the system-specific identifier
#         in order to create a key.
#
#      4) Compute an SHA-1 digest on the key as specified in [FIPS, SHA1];
#         the resulting value is 160 bits.
#
#      5) Use the least significant 40 bits as the Global ID.
#
#      6) Concatenate FC00::/7, the L bit set to 1, and the 40-bit Global
#         ID to create a Local IPv6 address prefix.
# VDC -- in other words, 'FD' with 40-bit hex to make FDxx:xxxx:xxxx::/48
#
#    This algorithm will result in a Global ID that is reasonably unique
#    and can be used to create a locally assigned Local IPv6 address
#    prefix.

import time
import datetime
import uuid
import hashlib

# from https://pypi.python.org/pypi/ntplib/ ...
SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
NTP_EPOCH = datetime.date(1900, 1, 1)
NTP_DELTA = (SYSTEM_EPOCH - NTP_EPOCH).days * 24 * 3600


def system_to_ntp_time(timestamp):
    """Convert a system time to a NTP time.

    Parameters:
    timestamp -- timestamp in system time

    Returns:
    corresponding NTP time
    """
    return timestamp + NTP_DELTA
# ... end quote

def make_prefix():
    """Returns a random IPv6 Global ID using the RFC-4193 algorithm"""
    #      1) Obtain the current time of day in 64-bit NTP format [NTP].
    step1 = system_to_ntp_time(time.time())
    #
    #      2) Obtain an EUI-64 identifier from the system running this
    #         algorithm.  If an EUI-64 does not exist, one can be created from
    #         a 48-bit MAC address as specified in [ADDARCH].  If an EUI-64
    #         cannot be obtained or created, a suitably unique identifier,
    #         local to the node, should be used (e.g., system serial number).
    step2 = uuid.getnode()
    #
    #      3) Concatenate the time of day with the system-specific identifier
    #         in order to create a key.
    step3 = '{}{}'.format(step1, step2).encode()
    #
    #      4) Compute an SHA-1 digest on the key as specified in [FIPS, SHA1];
    #         the resulting value is 160 bits.
    step4 = hashlib.sha1(step3).hexdigest()
    #
    #      5) Use the least significant 40 bits as the Global ID.
    step5 = step4[-10:]  # 40 bits / 4 bits per hex digit
    #
    #      6) Concatenate FC00::/7, the L bit set to 1, and the 40-bit Global
    #         ID to create a Local IPv6 address prefix.
    # VDC -- in other words, 'FD' with 40-bit hex to make FDxx:xxxx:xxxx::/48
    step6 = 'fd' + step5
    #
    #    This algorithm will result in a Global ID that is reasonably unique
    #    and can be used to create a locally assigned Local IPv6 address
    #    prefix.
    nibbles = []
    while step6:
        nibbles.append(step6[:4])
        step6 = step6[4:]
    return ':'.join(nibbles)


def make_network():
    """Returns a random IPv6 Global ID /48 network string using RFC-4193"""
    return make_prefix() + '::/48'

if __name__ == '__main__':
    """Print a random IPv6 network string."""
    print(make_network())
