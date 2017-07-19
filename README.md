# flasql

Basic flask views to provide endpoints for graphql queries, and an
interactive graphql interface.


### GraphQLView

Keyword Arguments

- `schema` a graphene schema to handle the GraphQL queries
- `error_handler` a function that takes two kwargs, `error` which is the specific error, and `params` which are the parameters that came into the request.
- `result_class` (optional, default:`GraphQLResult`) a class that conforms to the same interface of `GraphQLResult`
- `enable_graphiql` (default: True) determines whether or not the GraphiQL GUI will be available.


### Example Sentry Error Handler

```python
def sentry_error_handler(error, params):
    sentry.captureMessage(error, extra={
        'params': params
    })
```


