#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

"""
agent_based check for SIP registrations

Authors:    Chris Crosenhain (https://github.com/Crosenhain)
            Roger Ellenberger <roger.ellenberger@wagner.ch>
Version:    0.4

"""

from __future__ import annotations
from typing import NamedTuple, List, Mapping, Any

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Result,
    State,
    Service,
)


HEALTHY_REGISTRY_STATE: str = 'Registered'


class AsteriskRegistry(NamedTuple):
    account: str  # user@host:port
    state: str

    def from_string_table(line: str) -> AsteriskRegistry:
        return AsteriskRegistry(account=line[0], state=line[1])


def parse_asterisk_registry(string_table) -> List[AsteriskRegistry]:
    """
    example output:
        <<<asterisk_registry>>>
        22384668@sip2sip.info:5060	Registered
    """
    return [AsteriskRegistry.from_string_table(line) for line in string_table]


register.agent_section(
    name='asterisk_registry',
    parse_function=parse_asterisk_registry
)


def discover_asterisk_registry(section: List[AsteriskRegistry]) -> DiscoveryResult:
    for registration in section:
        yield Service(item=registration.account)


def check_asterisk_registry(item: str, section: List[AsteriskRegistry]) -> CheckResult:
    for registration in section:
        if registration.account == item:
            yield Result(
                state=State.OK if registration.state == HEALTHY_REGISTRY_STATE else State.CRIT,
                summary=f'State is {registration.state}'
            )
            return
    else:
        yield Result(state=State.UNKNOWN, summary='Registration not found!')


register.check_plugin(
    name='asterisk_registry',
    service_name='Asterisk registry %s',
    discovery_function=discover_asterisk_registry,
    check_function=check_asterisk_registry,
)
