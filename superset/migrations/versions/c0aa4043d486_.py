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
"""empty message

Revision ID: c0aa4043d486
Revises: f1410ed7ec95
Create Date: 2021-06-16 15:46:54.230435

"""

# revision identifiers, used by Alembic.
revision = 'c0aa4043d486'
down_revision = 'f1410ed7ec95'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.add_column('report_recipient', sa.Column('body', sa.String(length=500), nullable=True))
    op.add_column('report_recipient', sa.Column('subject', sa.String(length=50), nullable=False))

def downgrade():
    op.drop_column('report_recipient', 'subject')
    op.drop_column('report_recipient', 'body')
