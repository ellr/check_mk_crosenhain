#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
agent_based check for SIP peers

Authors:    Chris Crosenhain (https://github.com/Crosenhain)
            Roger Ellenberger <roger.ellenberger@wagner.ch>
Version:    0.4

"""

from __future__ import annotations
from typing import NamedTuple, List, Mapping, Any, Tuple

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    check_levels,
    register,
    Result,
    State,
    Service,
)


DEFAULT_LATENCY_LEVELS: Tuple[int] = (1500, 2000)


class Peer(NamedTuple):
    name: str
    host: str
    port: int
    status: str
    latency: int

    def from_string_table(line) -> Peer:
        return Peer(
            name=line[0],
            host=line[1],
            port=int(line[2]),
            status=line[3],
            latency=int(line[4]),
        )


def parse_asterisk_peers(string_table) -> List[Peer]:
    """
    example output:
        <<<asterisk_peers>>>
        100	            (Unspecified)	0	    UNKNOWN             0
        1111	        (Unspecified)	0	    Unmonitored         0
        123-2	        (Unspecified)	0	    UNKNOWN             0
        15/15	        10.52.12.55	    5060	Unmonitored         0
        21-2/21-2	    (Unspecified)	0	    UNKNOWN             0
        50-5/50-5	    10.52.12.87	    5060	OK	                13
        52-1/52-1	    10.52.12.3	    5062	OK	                53
        99010-1         (Unspecified)	0	    UNKNOWN            	0
        linkedPBX_86/87	10.52.25.6	    5060	UNREACHABLE         0
        prSIP_2/600815	10.52.40.38	    5060	OK              	1
    """
    return [Peer.from_string_table(line) for line in string_table]


register.agent_section(
    name='asterisk_peers',
    parse_function=parse_asterisk_peers,
)


def discover_asterisk_peers(section: List[Peer]) -> DiscoveryResult:
    for peer in section:
        yield Service(item=peer.name)


def check_asterisk_peers(item: str, params: Mapping[str, Any], section: List[Peer]) -> CheckResult:
    for peer in section:
        if peer.name == item:
            yield Result(
                state=State.OK if peer.status == 'OK' else State.CRIT,
                summary=f'Peer {peer.name} on host {peer.host}:{peer.port} is {peer.status}'
            )
            yield from check_levels(
                value=peer.latency,
                levels_upper=params['latency'],
                metric_name='latency',
                label='Latency',
                render_func=str,
            )
            return
    else:
        yield Result(state=State.UNKNOWN, summary='UNKNOWN - peer not found')


register.check_plugin(
    name='asterisk_peers',
    service_name='Asterisk peer %s',
    discovery_function=discover_asterisk_peers,
    check_function=check_asterisk_peers,
    check_default_parameters={"latency": DEFAULT_LATENCY_LEVELS},
)
