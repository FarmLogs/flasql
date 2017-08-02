import pytest

import graphene
import flask

from flasql.views import GraphQLView


class Query(graphene.ObjectType):
    debug = graphene.String()

    def resolve_debug(self, args, context, info):
        return 'Hi from GraphQL'


def create_graphql_view(**kwargs):
    schema = kwargs.pop('schema')

    kwargs.update({
        'schema': schema,
        'enable_graphiql': True,
    })

    return GraphQLView.as_view('graphql', **kwargs)


def create_app(**kwargs):
    app = flask.Flask(__name__)
    app.testing = True

    app.add_url_rule('/graphql', view_func=create_graphql_view(**kwargs))

    return app


def create_schema():
    return graphene.Schema(
        query=Query,
    )


@pytest.fixture()
def app():
    """
    Supplies a basic Flask app with a graphene schema
    mounted inside the flasql view at /graphql.

    """
    app = create_app(schema=create_schema())
    with app.test_request_context():
        yield app
