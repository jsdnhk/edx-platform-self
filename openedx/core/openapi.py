"""
Open API support.
"""

import textwrap

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema as drf_swagger_auto_schema

openapi_info = openapi.Info(
    title="Open edX API",
    default_version="v1",
    description="APIs for access to Open edX information",
    #terms_of_service="https://www.google.com/policies/terms/",         # TODO: Do we have these?
    contact=openapi.Contact(email="oscm@edx.org"),
    #license=openapi.License(name="BSD License"),                       # TODO: What does this mean?
)

schema_view = get_schema_view(
    openapi_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def swagger_auto_schema(**kwargs):
    if 'operation_description' in kwargs:
        kwargs['operation_description'] = textwrap.dedent(kwargs['operation_description'])
    for param in kwargs.get('manual_parameters', ()):
        param.description = textwrap.dedent(param.description)
    return drf_swagger_auto_schema(**kwargs)
