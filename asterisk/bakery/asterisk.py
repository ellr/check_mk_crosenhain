#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-


from pathlib import Path
from .bakery_api.v1 import OS, Plugin, register


PLUGIN_NAME: str = 'asterisk'


def bake_asterisk(conf):
    yield Plugin(
        base_os=OS.LINUX,
        source=Path(PLUGIN_NAME),
        interval=conf.get("interval"),
    )


register.bakery_plugin(
    name=PLUGIN_NAME,
    files_function=bake_asterisk,
)
