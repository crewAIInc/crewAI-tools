# ApiRequestTool

## Description
The `ApiRequestTool` is a component of the `crewai_tools` package, designed to make simple API calls to specified URLs and return the response code and response body wrapped in JSON. It is initially designed and used for leveraging the CrewAI framework in API testing purposes but may be used in any situation where you need to get a response from an endpoint.

## Installation
Install the `crewai_tools` package to use the `ApiRequestTool` in your projects:

```shell
pip install 'crewai[tools]'


from crewai_tools import ApiRequestTool
# Initialize the tool to make API calls to URLs the agent will get to know
api_request_tool = ApiRequestTool()

# OR

# Initialize the tool with a specific URL, so the agent can only trigger the API call and get the result
api_request_tool = ApiRequestTool(endpoint_url='https://api.example.com', http_verb='POST')

```

## Arguments
`endpoint_url`: The URL to be called. Please pay attention that there is no `params` dictionary 'cause LLM Agents usually struggles more the more tool has parameters. So all the URL-encoding must be wrapped in the endpoint_url
`http_verb`: The HTTP verb of the API call to be done (e.g., 'GET', 'POST').
`data`: The request data as a dictionary. {'key': 'value'}, which is converted to a JSON-formatted string.