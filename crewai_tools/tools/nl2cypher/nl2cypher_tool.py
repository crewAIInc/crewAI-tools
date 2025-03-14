from typing import Any, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from neo4j import GraphDatabase, Query
from neo4j.exceptions import (
    Neo4jError,
    ConfigurationError,
    ServiceUnavailable,
    AuthError,
)

from neo4j_graphrag.schema import (
    _value_sanitize,
    format_schema,
    get_structured_schema,
)


class NL2CypherToolInput(BaseModel):
    query: str = Field(
        title="Cypher Query",
        description="The Cypher query to execute.",
    )


class NL2CypherTool(BaseTool):
    name: str = "NL2CypherTool"
    description: str = "Converts natural language to Cypher queries and executes them."
    uri: str
    username: str
    password: str
    database: str = "neo4j"
    schema: str = ""
    structured_schema: dict = {}
    timeout: float = 10
    sanitize: bool = True
    args_schema: Type[BaseModel] = NL2CypherToolInput

    def model_post_init(self, __context: Any) -> None:
        self._driver = GraphDatabase.driver(
            self.uri, auth=(self.username, self.password)
        )
        # Verify connection
        try:
            self._driver.verify_connectivity()
        except ConfigurationError:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the driver config is correct"
            )
        except ServiceUnavailable:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the url is correct"
            )
        except AuthError:
            raise ValueError(
                "Could not connect to Neo4j database. "
                "Please ensure that the username and password are correct"
            )
        # Get schema
        self._get_schema()

    def _get_schema(self) -> None:
        self.structured_schema = get_structured_schema(
            driver=self._driver,
            is_enhanced=True,
            database=self.database,
            timeout=self.timeout,
            sanitize=self.sanitize,
        )
        self.schema = format_schema(schema=self.structured_schema, is_enhanced=True)

    def _run(self, query: str) -> list:
        try:
            data = self.execute_cypher(query)
        except Exception as exc:
            data = (
                f"Based on the provided schema {self.schema}, "
                "you can construct a valid Cypher query to retrieve the desired data. "
                f"The original query was: {query}. "
                f"The encountered error was: {exc}. "
                "Use this information to generate a corrected Cypher query."
            )
        return data

    def execute_cypher(
        self, cypher_query: str, params: dict = None
    ) -> Union[list, str]:
        try:
            data, _, _ = self._driver.execute_query(
                Query(text=cypher_query, timeout=self.timeout),
                database_=self.database,
                parameters_=params,
            )
            json_data = [r.data() for r in data]
            if self.sanitize:
                json_data = [_value_sanitize(el) for el in json_data]
            return json_data
        except Neo4jError as e:
            if not (
                (
                    (  # isCallInTransactionError
                        e.code == "Neo.DatabaseError.Statement.ExecutionFailed"
                        or e.code
                        == "Neo.DatabaseError.Transaction.TransactionStartFailed"
                    )
                    and e.message is not None
                    and "in an implicit transaction" in e.message
                )
                or (  # isPeriodicCommitError
                    e.code == "Neo.ClientError.Statement.SemanticError"
                    and e.message is not None
                    and (
                        "in an open transaction is not possible" in e.message
                        or "tried to execute in an explicit transaction" in e.message
                    )
                )
            ):
                raise
        # fallback to allow implicit transactions
        with self._driver.session(database=self.database) as session:
            result = session.run(Query(text=cypher_query, timeout=self.timeout), params)
            json_data = [r.data() for r in result]
            if self.sanitize:
                json_data = [_value_sanitize(el) for el in json_data]
            return json_data
