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

from typing import Dict, Tuple, List

import pytest

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State, Metric
from cmk.base.plugins.agent_based.asterisk_peers import (
    parse_asterisk_peers,
    check_asterisk_peers,
    Peer,
    DEFAULT_LATENCY_LEVELS,
)


@pytest.mark.parametrize(
    "string_table, expected_section",
    [
        (
            [],
            [],
        ),
        (
            [
                ['100', '(Unspecified)', '0', 'UNKNOWN', '0'],
            ],
            [
                Peer('100', '(Unspecified)', 0, 'UNKNOWN', 0),
            ],
        ),
        (
            [
                ['100', '(Unspecified)', '0', 'UNKNOWN', '0'],
                ['15/15', '10.52.12.55', '5060', 'Unmonitored', '0'],
                ['21-2/21-2', '(Unspecified)', '0', 'UNKNOWN', '0'],
                ['50-5/50-5', '10.52.12.87', '5060', 'OK', '13'],
            ],
            [
                Peer('100', '(Unspecified)', 0, 'UNKNOWN', 0),
                Peer('15/15', '10.52.12.55', 5060, 'Unmonitored', 0),
                Peer('21-2/21-2', '(Unspecified)', 0, 'UNKNOWN', 0),
                Peer('50-5/50-5', '10.52.12.87', 5060, 'OK', 13),
            ],
        ),
    ],
)
def test_parse_asterisk_peers(string_table: List[List[str]], expected_section: List[Peer]) -> None:
    assert parse_asterisk_peers(string_table) == expected_section


CHECK_ASTERISK_PEER: Dict[str, Tuple] = {"latency": DEFAULT_LATENCY_LEVELS}


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            "42",
            [],
            (
                Result(state=State.UNKNOWN, summary='UNKNOWN - peer not found'),
            ),
        ),
        (
            "42",
            [
                Peer('100', '(Unspecified)', 0, 'UNKNOWN', 0),
            ],
            (
                Result(state=State.UNKNOWN, summary='UNKNOWN - peer not found'),
            ),
        ),
        (
            "100",
            [
                Peer('100', '(Unspecified)', 0, 'UNKNOWN', 0),
            ],
            (
                Result(state=State.CRIT, summary='Peer 100 on host (Unspecified):0 is UNKNOWN'),
                Result(state=State.OK, summary='Latency: 0'),
                Metric('latency', 0, levels=DEFAULT_LATENCY_LEVELS),
            ),
        ),
        (
            "15/15",
            [
                Peer('15/15', '10.52.12.55', 5060, 'Unmonitored', 0),
                Peer('21-2/21-2', '(Unspecified)', 0, 'UNKNOWN', 0),
                Peer('50-5/50-5', '10.52.12.87', 5060, 'OK', 13),
            ],
            (
                Result(state=State.CRIT, summary='Peer 15/15 on host 10.52.12.55:5060 is Unmonitored'),
                Result(state=State.OK, summary='Latency: 0'),
                Metric('latency', 0, levels=DEFAULT_LATENCY_LEVELS),
            ),
        ),
        (
            "50-5/50-5",
            [
                Peer('15/15', '10.52.12.55', 5060, 'Unmonitored', 0),
                Peer('21-2/21-2', '(Unspecified)', 0, 'UNKNOWN', 0),
                Peer('50-5/50-5', '10.52.12.87', 5060, 'OK', 13),
            ],
            (
                Result(state=State.OK, summary='Peer 50-5/50-5 on host 10.52.12.87:5060 is OK'),
                Result(state=State.OK, summary='Latency: 13'),
                Metric('latency', 13, levels=DEFAULT_LATENCY_LEVELS),
            ),
        ),
        (
            "prSIP_2",
            [
                Peer('prSIP_2', '10.52.12.87', 5061, 'OK', 1584),
                Peer('prSIP_3', '10.52.12.87', 5062, 'OK', 2039),
            ],
            (
                Result(state=State.OK, summary='Peer prSIP_2 on host 10.52.12.87:5061 is OK'),
                Result(state=State.WARN, summary='Latency: 1584 (warn/crit at 1500/2000)'),
                Metric('latency', 1584, levels=DEFAULT_LATENCY_LEVELS),
            ),
        ),
        (
            "prSIP_3",
            [
                Peer('prSIP_2', '10.52.12.87', 5061, 'OK', 1600),
                Peer('prSIP_3', '10.52.12.87', 5062, 'OK', 2039),
            ],
            (
                Result(state=State.OK, summary='Peer prSIP_3 on host 10.52.12.87:5062 is OK'),
                Result(state=State.CRIT, summary='Latency: 2039 (warn/crit at 1500/2000)'),
                Metric('latency', 2039, levels=DEFAULT_LATENCY_LEVELS),
            ),
        ),
    ],
)
def test_check_asterisk_peers(item: str, section: List[Peer], expected_check_result: Tuple) -> None:
    assert tuple(check_asterisk_peers(item, CHECK_ASTERISK_PEER, section)) == expected_check_result
