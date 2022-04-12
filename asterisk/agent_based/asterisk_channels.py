#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) 2019 Heinlein Support GmbH
#          Robert Sander <r.sander@heinlein-support.de>

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  This file is distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

"""
Check_MK Checks to use with asterisk datasource

Authors:    Robert Sander <r.sander@heinlein-support.de>
            Roger Ellenberger <roger.ellenberger@wagner.ch>
Version:    0.7

"""

from dataclasses import dataclass, field
from typing import NamedTuple, List, Set, Optional

from .agent_based_api.v1.type_defs import (
    CheckResult,
    DiscoveryResult,
)
from .agent_based_api.v1 import (
    register,
    Metric,
    Result,
    State,
    Service,
)


class AsteriskChannel(NamedTuple):
    name: str
    location: str
    state: str
    application_data: str


@dataclass
class AsteriskChannelSummary:
    channels: List[AsteriskChannel] = field(default_factory=list)
    active_channels: Optional[int] = None
    active_calls: Optional[int] = 0
    processed_calls: Optional[int] = 0

    def parse_call_stats(self, line) -> None:
        if line[1] == 'active' and line[2] in 'channels':
            self.active_channels = int(line[0])
        elif line[1] == 'active' and line[2] in 'calls':
            self.active_calls = int(line[0])
        elif line[1] in 'calls' and line[2] == 'processed':
            self.processed_calls = int(line[0])

    def get_result_text(self) -> str:
        return (f'{self.active_channels} active channels, '
                f'{self.active_calls} active calls, '
                f'{self.processed_calls} calls processed')

    def incomplete_plugin_output(self) -> bool:
        return self.active_channels is None

    def get_down_channels(self) -> List[AsteriskChannel]:
        return [channel for channel in self.channels if channel.state not in HEALTY_CHANNEL_STATES]

    @staticmethod
    def get_down_channels_text(down_channels: List[AsteriskChannel]):
        if len(down_channels) == 1:
            c = down_channels[0]
            return f'Channel {c.name} is {c.state}! '
        else:
            return f'{len(down_channels)} Channels are down! '


CHANNELS_HEADER: Set[str] = {'Channel', 'Location', 'State', 'Application(Data)'}
HEALTY_CHANNEL_STATES: Set[str] = {'Up', 'Ring', 'Ringing'}


def parse_asterisk_channels(string_table) -> AsteriskChannelSummary:
    """
    example output:
        Channel              Location             State   Application(Data)             
        SIP/6001-00000001    (None)               Up      Playback(demo-congrats)
        SIP/trunk_internal   (None)               Up      Dial(SIP/+41223344@trunk)
        Local/1234@anywhere  anywhere             Down    Return()
        3 active channels
        2 active calls
        15468 calls processed
    """
    summary = AsteriskChannelSummary()

    for line in string_table:
        if all(item in CHANNELS_HEADER for item in line):
            continue
        if len(line) == 4:
            summary.channels.append(AsteriskChannel(
                name=line[0],
                location=line[1],
                state=line[2],
                application_data=line[3]
            ))
        elif len(line) == 3:
            summary.parse_call_stats(line)

    return summary


register.agent_section(
    name='asterisk_channels',
    parse_function=parse_asterisk_channels,
)


def discover_asterisk_channels(section: AsteriskChannelSummary) -> DiscoveryResult:
    yield Service()


def check_asterisk_channels(section: AsteriskChannelSummary) -> CheckResult:
    down_channels = section.get_down_channels()

    if section.incomplete_plugin_output():
        yield Result(state=State.UNKNOWN, summary='incomplete check output, channel stats not found!')
        return

    elif down_channels:
        yield Result(state=State.CRIT,
                     summary=AsteriskChannelSummary.get_down_channels_text(down_channels) + section.get_result_text())

    else:
        yield Result(state=State.OK, summary=section.get_result_text())

    yield Metric('active_channels', section.active_channels)
    yield Metric('active_calls', section.active_calls)
    yield Metric('processed_calls', section.processed_calls)


register.check_plugin(
    name='asterisk_channels',
    service_name='Asterisk Channels',
    discovery_function=discover_asterisk_channels,
    check_function=check_asterisk_channels,
)
