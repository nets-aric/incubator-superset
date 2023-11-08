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
import concurrent.futures
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


async def detokenise_post_process(df: DataFrame) -> DataFrame:
    filtered_tokens = {value for col_name in df.columns for value in df[col_name] if
                       isinstance(value, str) and value.startswith('t:')}

    detokenised_values = session.post(config['DETOKENISE_POST_URL'],
                           data=json.dumps({"id": list(filtered_tokens)})).result().json()

    result_dict = dict(zip(filtered_tokens, detokenised_values))

    for col_name in df.columns:
        df[col_name] = df[col_name].map(lambda x: result_dict.get(x, x))

    return df


