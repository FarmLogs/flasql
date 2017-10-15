"""
Intends to provide conveniences around mounting a Graphene schema

"""
from flask import request, json, jsonify
from flask.views import MethodView

from flasql import graphiql


def format_error(error):
    """
    Taken from graphql-python/graphql-core, modified to be a little more robust.
    https://github.com/graphql-python/graphql-core/blob/master/graphql/error/format_error.py

    """
    formatted_error = {
        'message': error.message if hasattr(error, 'message') else str(error)
    }

    if hasattr(error, 'locations') and error.locations is not None:
        formatted_error['locations'] = [
            {'line': loc.line, 'column': loc.column}
            for loc in error.locations
        ]

    return formatted_error


class GraphQLResult(object):
    def __init__(self, result):
        self.result = result

    def to_response(self):
        return jsonify(self.result)


class GraphQLView(MethodView):
    def __init__(self,
                 schema=None,
                 error_handler=None,
                 result_class=None,
                 enable_graphiql=True,
                 graphiql_version=graphiql.GRAPHIQL_VERSION,
                 context_factory=None):

        super(GraphQLView, self).__init__()

        if not schema:
            raise Exception("A graphene schema must be specified.")

        self.schema = schema
        self.error_handler = error_handler or False
        self.result_class = result_class or GraphQLResult
        self.enable_graphiql = enable_graphiql
        self.context_factory = context_factory or False
        self.graphiql_version = graphiql_version
        self._params = None

    @property
    def can_display_graphiql(self):
        """Determines if we are *allowed* to display the UI"""
        return self.enable_graphiql or 'raw' not in request.args

    @property
    def request_wants_html(self):
        """
        Determines if the inbound request desires an HTTP response.
        Taken from flask_graphql, refactor.

        """
        best = request.accept_mimetypes.best_match(
            ['application/json', 'text/html'])

        return (best == 'text/html' and
                request.accept_mimetypes[best] >
                request.accept_mimetypes['application/json'])

    @property
    def should_display_graphiql(self):
        """Determines if we *should* show the graphiql UI."""
        return self.can_display_graphiql and self.request_wants_html

    @property
    def params(self):
        if self._params:
            return self._params

        request_keys = {'query', 'operationName', 'variables'}

        if request.method == 'GET':
            # we will collect the data from the query parameters,
            # such as ?query={}
            self._params = {k: request.args.get(k) for k in request_keys}
            return self._params
        if request.method == 'POST':
            if request.mimetype == 'application/graphql':
                return {'query': request.data.decode('utf8')}

            elif request.mimetype == 'application/json':
                payload = request.json
                if "variables" in payload and isinstance(payload["variables"], str):
                    payload["variables"] = json.loads(payload["variables"])
                self._params = payload
                return self._params

            elif request.mimetype in ('application/x-www-form-urlencoded',
                                      'multipart/form-data'):
                self._params = request.form
                return self._params

        # Else, return an empty map
        self._params = {k: None for k in request_keys}
        return self._params

    def format_execution_result(self, result):
        """
        Transforms the graphql.execution.base.ExecutionResult into a JSON
        encodable entity.

        """
        if not result:
            return None

        resp = {}

        if result.data:
            resp['data'] = result.data

        if result.errors:
            resp['errors'] = [format_error(e) for e in result.errors]

        return resp

    def track_errors(self, errors):
        if not self.error_handler:
            return

        for error in errors:
            self.error_handler(error=error, params=self.params)

    @property
    def context(self):
        """
        Handles calling the context_factory, if it is defined.

        Duck typing: we call dict on the result from our factory so that
        we ensure consistency, yet allow for more flexibility in implementation.

        """
        if not self.context_factory:
            return None

        try:
            return dict(self.context_factory())

        except TypeError:
            raise Exception(('The result of `context_factory` must be an iterable '
                             'that allows dict() to be called on it.'))

    @property
    def variables(self):
        variables = self.params.get('variables', None)

        if not variables:
            return None

        if isinstance(variables, str):
            return json.loads(variables)

        return variables

    def handle_request(self):
        params = self.params
        result = None

        # This is where we actually submit our query to the graphql schema
        if params.get('query'):
            kwargs = {
                'variable_values': self.variables,
                'context_value': self.context
            }

            result = self.schema.execute(params.get('query'), **kwargs)

        # this is where we would capture graphql errors
        if result and result.errors:
            self.track_errors(result.errors)

        return self.format_execution_result(result)

    def get(self):
        """
        For displaying the graphiql client, and for query requests

        """
        result = self.handle_request()

        if self.should_display_graphiql:
            return graphiql.render(params=self.params, result=result, graphiql_version=self.graphiql_version)

        return self.result_class(result)

    def post(self):
        """For mutations"""
        result = self.handle_request()

        return self.result_class(result)
