# flasql

Basic flask views to provide endpoints for graphql queries, and an interactive graphql interface.


### GraphQLView

Keyword Arguments

- `schema` a graphene schema to handle the GraphQL queries
- `error_handler` (optional, default: no-op) a function that takes two kwargs, `error` which is the specific error, and `params` which are the parameters that came into the request.
- `result_class` (optional, default:`GraphQLResult`) a class that conforms to the same interface of `GraphQLResult`
- `enable_graphiql` (default: True) determines whether or not the GraphiQL GUI will be available.
- `context_factory` (optional, default: no-op) a factory which will return a dictionary of additional context to pass into the query being executed, ie the current user. The result of this fn [must be iterable](https://docs.python.org/2/glossary.html#term-iterable) because `dict()` is called on the result that is passed to Graphene.

### Example Sentry Error Handler

```python
def sentry_error_handler(error, params):
    sentry.captureMessage(error, extra={
        'params': params
    })
```


### Example Context Handler

This will pass `auth` through to the Graphene resolvers:

```python
def context_factory():
    """
    Called just prior to executing a query against the schema.
    The result of this (dict) is sent along with the query as the `context`.

    Useful for attaching high-level things like the current user, etc...

    """
    auth = flask.g.get('auth')

    return {
        'auth': auth,
    }
```
