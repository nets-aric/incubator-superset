import requests
import sqlparse
import copy
import dataclasses
import inspect
import logging
import math
import re
from collections import defaultdict, OrderedDict
from datetime import date, datetime, timedelta
from itertools import product
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    TYPE_CHECKING,
    Union,
)
import geohash
import numpy as np
import pandas as pd
import polyline
import simplejson as json
from dateutil import relativedelta as rdelta
from flask import request
from flask_babel import lazy_gettext as _
from geopy.point import Point
from pandas.tseries.frequencies import to_offset
from superset import app, cache, db, security_manager
from superset.constants import NULL_STRING
from superset.errors import ErrorLevel, SupersetError, SupersetErrorType
from superset.exceptions import (
    NullValueException,
    QueryObjectValidationError,
    SpatialException,
)
from superset.models.cache import CacheKey
from superset.models.helpers import QueryResult
from superset.typing import QueryObjectDict, VizData, VizPayload
from superset.utils import core as utils
from superset.utils.core import (
    DTTM_ALIAS,
    JS_MAX_INTEGER,
    merge_extra_filters,
    QueryMode,
    to_adhoc,
)
from superset.utils.dates import datetime_to_epoch
from superset.utils.hashing import md5_sha_from_str
if TYPE_CHECKING:
    from superset.connectors.base.models import BaseDatasource
config = app.config

logger = logging.getLogger(__name__)

tokenise_query = config["TOKENISE_QUERY"]
tokenise_post_url = config["TOKENISE_POST_URL"]
tokenise_access_token = config["TOKENISE_ACCESS_TOKEN"]
tokenise_lookup_name = config["TOKENISE_LOOKUP_NAME"]
tokenise_timeout_value = config["TOKENISE_TIMEOUT_VALUE"]

def tokenise_fixed_string(self, fixed_string: str) -> str:
        response = requests.post(tokenise_post_url,
            timeout=tokenise_timeout_value,
            data="\"" + fixed_string + "\"",
            headers={"content-type":"text/plain", "Access-Token": tokenise_access_token},
            )
        return response.text.strip()


def extract_lookup_info(self, sql_string: str, regex: str) -> Tuple[str, str]:
        rawLookups = re.findall(regex, sql_string)
        if rawLookups:
            lookup = [lookup.strip() for lookup in rawLookups][0]
            lookupFunction = re.match("^\s*(\w+)\s*\((.*)\)", lookup)
            lookupFunctionSplit = lookupFunction.group(2).split(',')
            lookupColumn = eval(lookupFunctionSplit[0])
            lookupName = eval(lookupFunctionSplit[1])
            return lookupColumn, lookupName
        else:
            return None


def tokenise_query_obj_sql(self, query_obj: QueryObjectDict) -> QueryObjectDict:
        rawSql = self.datasource.sql
        if type(query_obj) != dict:
            query_obj = query_obj.to_dict()
        formattedSql = sqlparse.format(rawSql, reindent=True, keyword_case="upper", identifier_case="upper", strip_comments=True)
        filters = query_obj.get("filter")
        if filters:
            modified_query_obj = copy.copy(query_obj)
            modified_query_obj["filter"] = []
            for filter in filters:
                new_filter = copy.copy(filter)
                column = filter.get("col")
                value = filter.get("val")
                regex = f".*LOOKUP.*AS.*.*{column}.*"
                result = extract_lookup_info(self, formattedSql, regex)
                if result:
                    lookupColumn, lookupName = result
                    if lookupName == tokenise_lookup_name:


                        if isinstance(value, list):
                            token = []
                            for i in value:
                                temp = tokenise_fixed_string(self, i)
                                token.append(temp)
                            new_filter["col"] = lookupColumn
                            new_filter["val"] = token
                            modified_query_obj["filter"].append(new_filter)
                        else:
                            token = tokenise_fixed_string(self, value)
                            new_filter["col"] = lookupColumn
                            new_filter["val"] = token
                            modified_query_obj["filter"].append(new_filter)
                    else:
                        modified_query_obj["filter"].append(filter)
                else:
                    modified_query_obj["filter"].append(filter)
            return modified_query_obj
        else:
            return query_obj

def tokenise_query_obj_table(self, query_obj: QueryObjectDict) -> QueryObjectDict:
        filters = query_obj.get("filter")
        if filters:
            modified_query_obj = query_obj
            modified_query_obj["filter"] = []
            for filter in filters:
                new_filter = copy.copy(filter)
                column = filter.get("col")
                value = filter.get("val")
                filter_col = datasource.get_column(column)
                if filter_col.expression:
                    rawSql = filter_col.expression
                    formattedSql = sqlparse.format(rawSql, reindent=True, keyword_case="upper", identifier_case="upper", strip_comments=True)
                    regex = ".*LOOKUP.*"
                    result = extract_lookup_info(formattedSql, regex)
                    if result:
                        lookupColumn, lookupName = result
                        if lookupName == tokenise_lookup_name:
                            token = tokenise_fixed_string(value)
                            new_filter["col"] = lookupColumn
                            new_filter["val"] = token
                            modified_query_obj["filter"].append(new_filter)
                        else:
                            modified_query_obj["filter"].append(filter)
                    else:
                        modified_query_obj["filter"].append(filter)
                else:
                    modified_query_obj["filter"].append(filter)
            return modified_query_obj
        else:
            return query_obj


def tokenise_query_obj(self, query_obj: QueryObjectDict) -> QueryObjectDict:
        if self.datasource.sql:
            processed_query_obj = tokenise_query_obj_sql(self, copy.copy(query_obj))
        else:
            return query_obj.to_dict()

        if processed_query_obj:
            return processed_query_obj
        else:
            return query_obj.to_dict()
