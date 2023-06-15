# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# pylint: disable=invalid-name
from __future__ import annotations

import asyncio
import contextvars
import functools
from asyncio import events

from requests_futures.sessions import FuturesSession
import json
import logging
from pandas import DataFrame

from superset import app

config = app.config
logger = logging.getLogger(__name__)

session = FuturesSession()
session.headers.update({
    'Access-Token': config['DETOKENISE_ACCESS_TOKEN'],
    'Content-Type': 'text/plain; charset=utf-8'
})


def detokenise_json(df: DataFrame) -> DataFrame:
    if df.dtype == 'object' and any(val.startswith('t:') if val is not None else False for val in df):
        data = json.dumps({"id": df.to_list()})
        req = session.post(config['DETOKENISE_POST_URL'],
                           data=data)
        return req.result().json()
    return df


async def to_thread(func, /, *args, **kwargs):
    """Asynchronously run function *func* in a separate thread.
    Any *args and **kwargs supplied for this function are directly passed
    to *func*. Also, the current :class:`contextvars.Context` is propogated,
    allowing context variables from the main thread to be accessed in the
    separate thread.
    Return a coroutine that can be awaited to get the eventual result of *func*.
    """
    loop = events.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)


async def detokenise_post_process(df: DataFrame) -> DataFrame:
    data = await asyncio.gather(
        *[to_thread(detokenise_json, df[col]) for col in df])
    for count, col in enumerate(df):
        df[col] = data[count]
    return df
