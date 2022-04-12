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

from cmk.base.plugins.agent_based.agent_based_api.v1 import Result, State
from cmk.base.plugins.agent_based.asterisk_registry import (
    parse_asterisk_registry,
    check_asterisk_registry,
    AsteriskRegistry,
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
                ['22384668@sip2sip.info:5060', 'Registered'],
            ],
            [
                AsteriskRegistry('22384668@sip2sip.info:5060', 'Registered'),
            ]
        ),
        (
            [
                ['22384668@sip2sip.info:5060', 'Registered'],
                ['supersip@sip.example.com:1234', 'Unknown'],
            ],
            [
                AsteriskRegistry('22384668@sip2sip.info:5060', 'Registered'),
                AsteriskRegistry('supersip@sip.example.com:1234', 'Unknown')
            ]
        ),
    ],
)
def test_parse_asterisk_registry(string_table: List[List[str]], expected_section: List[AsteriskRegistry]) -> None:
    assert parse_asterisk_registry(string_table) == expected_section


@pytest.mark.parametrize(
    "item, section, expected_check_result",
    [
        (
            '22384668@sip2sip.info:5060',
            [
                AsteriskRegistry('sipsip@hurray.local', 'Registered'),
            ],
            (
                Result(state=State.UNKNOWN, summary='Registration not found!'),
            ),
        ),
        (
            '22384668@sip2sip.info:5060',
            [
                AsteriskRegistry('22384668@sip2sip.info:5060', 'Registered'),
            ],
            (
                Result(state=State.OK, summary='State is Registered'),
            ),
        ),
        (
            'supersip@sip.example.com:1234',
            [
                AsteriskRegistry('22384668@sip2sip.info:5060', 'Registered'),
                AsteriskRegistry('supersip@sip.example.com:1234', 'Unknown')
            ],
            (
                Result(state=State.CRIT, summary='State is Unknown'),
            ),
        ),
    ],
)
def test_check_asterisk_registry(item: str, section: List[AsteriskRegistry], expected_check_result: Tuple) -> None:
    assert tuple(check_asterisk_registry(item, section)) == expected_check_result
