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

from typing import List

import pytest

from cmk.base.plugins.agent_based.asterisk_iax2_peer import (
    parse_asterisk_iax2_peers,
    IAX2Peer,
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
                ['voxlink/pbx27', '195.211.101.70', '(S)', '4569', 'OK', '6'],
            ],
            [
                IAX2Peer('voxlink/pbx27', '195.211.101.70', 4569, 'OK', 6),
            ],
        ),
        (
            [
                ['voxlink/pbx27', '195.211.101.70', '(S)', '4569', 'OK', '6'],
                ['voxlink/pbx47', '195.211.201.70', '(S)', '4569', 'UNKNOWN', '65'],
            ],
            [
                IAX2Peer('voxlink/pbx27', '195.211.101.70', 4569, 'OK', 6),
                IAX2Peer('voxlink/pbx47', '195.211.201.70', 4569, 'UNKNOWN', 65),
            ],
        ),
    ],
)
def test_parse_asterisk_iax2_peers(string_table: List[List[str]], expected_section: List[IAX2Peer]) -> None:
    assert parse_asterisk_iax2_peers(string_table) == expected_section
