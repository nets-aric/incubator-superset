from flask import flash, g
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access
from .base import DeleteMixin, SupersetModelView
from flask import abort, flash, g, Markup, redirect, render_template, request, Response
from flask_appbuilder import BaseView, Model, ModelView
from superset.views.base import (
    api,
    BaseSupersetView,
    check_ownership,
    common_bootstrap_payload,
    create_table_permissions,
    CsvResponse,
    data_payload_response,
    generate_download_headers,
    get_error_msg,
    get_user_roles,
    handle_api_exception,
    json_error_response,
    json_errors_response,
    json_success,
    validate_sqlatable,
)
class DataTableView(BaseView):

    @expose('/dtable/<int:slice_id>/', methods=["GET", "POST"])
    def dt(self,slice_id):
        return self.render_template("superset/add_dtable.html", slice_id=slice_id)
