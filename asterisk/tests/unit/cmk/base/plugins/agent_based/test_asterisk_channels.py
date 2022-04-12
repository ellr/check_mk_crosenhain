#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# tails. You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

from typing import Tuple, List

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from cmk.base.plugins.agent_based.asterisk_channels import (
    parse_asterisk_channels,
    check_asterisk_channels,
    AsteriskChannel,
    AsteriskChannelSummary,
)


@pytest.mark.parametrize(
    "channel_summary, result_text, valid_output",
    [
        (
            AsteriskChannelSummary(),
            "None active channels, 0 active calls, 0 calls processed",
            True,
        ),
        (
            AsteriskChannelSummary(
                active_calls=1,
                processed_calls=0,
            ),
            "None active channels, 1 active calls, 0 calls processed",
            True,
        ),
        (
            AsteriskChannelSummary(
                active_channels=1,
            ),
            "1 active channels, 0 active calls, 0 calls processed",
            False,
        ),
        (
            AsteriskChannelSummary(
                active_channels=10,
                active_calls=4,
                processed_calls=76823,
            ),
            "10 active channels, 4 active calls, 76823 calls processed",
            False,
        ),
       
    ],
)
def test_asterisk_channel_summary(channel_summary: AsteriskChannelSummary, result_text: str, valid_output: bool) -> None:
    assert channel_summary.get_result_text() == result_text
    assert channel_summary.incomplete_plugin_output() == valid_output


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            AsteriskChannelSummary(),
        ),
        (
            [
                ['Channel', 'Location', 'State', 'Application(Data)'],
                ['0', 'active', 'channels'],
                ['0', 'active', 'calls'],
                ['0', 'calls', 'processed'],
            ],
            AsteriskChannelSummary(
                active_channels=0,
                active_calls=0,
                processed_calls=0,
            ),
        ),
        (
            [
                ['Channel', 'Location', 'State', 'Application(Data)'],
                ['SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'],
                ['1', 'active', 'channel'],
            ],
            AsteriskChannelSummary(
                channels=[
                    AsteriskChannel('SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'),
                ],
                active_channels=1,
            ),
        ),
        (
            [
                ['Channel', 'Location', 'State', 'Application(Data)'],
                ['SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'],
                ['SIP/trunk_internal', '(None)', 'Up', 'Dial(SIP/+41223344@trunk)'],
                ['Local/1234@anywhere', 'anywhere', 'Down', 'Return()'],
                ['3', 'active', 'channels'],
                ['2', 'active', 'calls'],
                ['15468', 'calls', 'processed'],
            ],
            AsteriskChannelSummary(
                channels=[
                    AsteriskChannel('SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'),
                    AsteriskChannel('SIP/trunk_internal', '(None)', 'Up', 'Dial(SIP/+41223344@trunk)'),
                    AsteriskChannel('Local/1234@anywhere', 'anywhere', 'Down', 'Return()'),
                ],
                active_channels=3,
                active_calls=2,
                processed_calls=15468,
            ),
        ),
    ],
)
def test_parse_asterisk_channels(string_table: List[List[str]], expected_section: AsteriskChannelSummary) -> None:
    assert parse_asterisk_channels(string_table) == expected_section


@pytest.mark.parametrize(
    "section, expected_check_result",
    [
        (
            AsteriskChannelSummary(),
            (
                Result(state=State.UNKNOWN, summary='incomplete check output, channel stats not found!'),
            ),
        ),
        (
            AsteriskChannelSummary(
                active_channels=0,
                active_calls=0,
                processed_calls=0,
            ),
            (
                Result(state=State.OK, summary='0 active channels, 0 active calls, 0 calls processed'),
                Metric('active_channels', 0),
                Metric('active_calls', 0),
                Metric('processed_calls', 0),
            ),
        ),
        (
            AsteriskChannelSummary(
                channels=[
                    AsteriskChannel('SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'),
                    AsteriskChannel('SIP/trunk_internal', '(None)', 'Up', 'Dial(SIP/+41223344@trunk)'),
                    AsteriskChannel('Local/1234@anywhere', 'anywhere', 'Down', 'Return()'),
                ],
                active_channels=3,
                active_calls=2,
                processed_calls=15468,
            ),
            (
                Result(state=State.CRIT, summary='Channel Local/1234@anywhere is Down! 3 active channels, 2 active calls, 15468 calls processed'),
                Metric('active_channels', 3),
                Metric('active_calls', 2),
                Metric('processed_calls', 15468),
            ),
        ),
        (
            AsteriskChannelSummary(
                channels=[
                    AsteriskChannel('SIP/6001-00000001', '(None)', 'Up', 'Playback(demo-congrats)'),
                    AsteriskChannel('SIP/trunk_1984', 'Ministry of Plenty', 'Down', 'Return()'),
                    AsteriskChannel('Local/1234@anywhere', 'anywhere', 'Down', 'Return()'),
                ],
                active_channels=3,
                active_calls=1,
                processed_calls=42,
            ),
            (
                Result(state=State.CRIT, summary='2 Channels are down! 3 active channels, 1 active calls, 42 calls processed'),
                Metric('active_channels', 3),
                Metric('active_calls', 1),
                Metric('processed_calls', 42),
            ),
        ),
    ],
)
def test_check_asterisk_channels(section: AsteriskChannelSummary, expected_check_result: Tuple) -> None:
    assert tuple(check_asterisk_channels(section)) == expected_check_result
