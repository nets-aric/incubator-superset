# -*- coding: utf-8 -*-
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
import json
import logging
from dataclasses import dataclass
from email.utils import make_msgid, parseaddr
from typing import Any, Dict, Optional

from flask_babel import gettext as __

from superset import app
from superset.models.reports import ReportRecipientType
from superset.reports.notifications.base import BaseNotification
from superset.reports.notifications.exceptions import NotificationError
from superset.utils.core import send_email_smtp
from datetime import datetime
import boto3

s3_client = boto3.client('s3')
logger = logging.getLogger(__name__)


@dataclass
class S3Content:
    filename: str
    data: bytes


class S3Notification(BaseNotification):  # pylint: disable=too-few-public-methods
    """
    Sends an email notification for a report recipient
    """

    type = ReportRecipientType.S3

    @staticmethod
    def _error_template(text: str) -> str:
        return __(
            """
            Error: %(text)s
            """,
            text=text,
        )

    def _get_content(self) -> S3Content:
        # Get the domain from the 'From' address ..
        # and make a message id without the < > in the end
        if self._content.screenshot:
            img_data = self._content.screenshot
            name = str(datetime.now()) + self._content.name + ".png"
            name.replace(" ", "-")
            return S3Content(filename=name, data=img_data)
        if self._content.csv:
            csv_data = self._content.csv
            name = str(datetime.now()) + "-" + self._content.name + ".csv"
            name.replace(" ", "-")
            return S3Content(filename=name, data=csv_data)

    def _get_bucket(self) -> str:
        return json.loads(self._recipient.recipient_config_json)["target"]

    def send(self) -> None:
        content = self._get_content()
        bucket = self._get_bucket()
        try:
            s3_client.put_object(Body=content.data, Bucket=bucket, Key=content.filename)
            logger.info("Report sent to s3")
        except Exception as ex:
            raise NotificationError(ex)
