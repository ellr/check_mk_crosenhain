#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
agent_based check for IAX2 peers

Authors:    Chris Crosenhain (https://github.com/Crosenhain)
            Roger Ellenberger <roger.ellenberger@wagner.ch>
Version:    0.4

"""

from __future__ import annotations
from typing import List

from .agent_based_api.v1 import register

from .asterisk_peers import (
    Peer,
    discover_asterisk_peers,
    check_asterisk_peers,
)


class IAX2Peer(Peer):

    @staticmethod
    def parse_string_table(line) -> IAX2Peer:
        return IAX2Peer(
            name=line[0],
            host=line[1],
            port=int(line[3]),
            status=line[4],
            latency=int(line[5]),
        )


def parse_asterisk_iax2_peers(string_table) -> List[IAX2Peer]:
    """
    example output:
        <<<asterisk_iax2_peers>>>
        voxlink/pbx27	  195.211.101.70 (S)  	4569	OK	6
    """
    return [IAX2Peer.parse_string_table(line) for line in string_table]


register.agent_section(
    name='asterisk_iax2_peers',
    parse_function=parse_asterisk_iax2_peers,
)


register.check_plugin(
    name='asterisk_iax2_peers',
    service_name='Asterisk IAX2 peer %s',
    discovery_function=discover_asterisk_peers,
    check_function=check_asterisk_peers,
    check_default_parameters={"latency": (1500, 2000)},
)
