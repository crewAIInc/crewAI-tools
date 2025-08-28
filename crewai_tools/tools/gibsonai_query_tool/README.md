# GibsonAIQueryTool

## Description
This tool enables direct SQL query execution against [GibsonAI](https://www.gibsonai.com/) serverless databases (MySQL/PostgreSQL) via the hosted Data API. The GibsonAIQueryTool provides a flexible interface for performing database operations including SELECT queries for data retrieval and INSERT/UPDATE/DELETE operations for data modification. It works with any database schema deployed in your GibsonAI project, making it a versatile tool for database interactions.

## Installation
To install the `crewai_tools` package and utilize the GibsonAIQueryTool, execute the following command in your terminal:

```shell
pip install 'crewai[tools]'
```

## Setup

### 1. Set up your GibsonAI Project
In [GibsonAI](https://app.gibsonai.com), create a new project with your desired database schema. For example:

```txt
I want to create a customer management system with the following tables:
- "customers" table with fields (name, email, phone, created_at)
- "orders" table with fields (customer_id, product_name, quantity, price, order_date)
- "products" table with fields (name, description, price, stock_quantity)
```

Once generated, click `Deploy` to Production and copy the API key from the `Data API` tab.

### 2. Set up Environment Variables
Create a `.env` file in your project root and add your GibsonAI API key:

```env
GIBSONAI_API_KEY=your_project_api_key_here
```

## Example Usage

```python
from crewai_tools import GibsonAIQueryTool

# Initialize the tool
tool = GibsonAIQueryTool()

# Or initialize with explicit API key
tool = GibsonAIQueryTool(api_key="your_api_key_here")

# Example queries
# 1. Select data
result = tool.run(query="SELECT * FROM customers WHERE email LIKE '%@gmail.com'")

# 2. Insert new data
result = tool.run(query="INSERT INTO customers (name, email, phone) VALUES ('John Doe', 'john@example.com', '555-0123')")

# 3. Update existing data
result = tool.run(query="UPDATE products SET price = 29.99 WHERE name = 'Widget'")

# 4. Delete data
result = tool.run(query="DELETE FROM orders WHERE order_date < '2023-01-01'")

# 5. Parameterized query (recommended for security)
result = tool.run(
    query="SELECT * FROM customers WHERE name = ? AND email = ?",
    parameters={"name": "John Doe", "email": "john@example.com"}
)
```

## Arguments
The GibsonAIQueryTool accepts the following arguments:

- `query` (required): A string containing the SQL query to execute. This can be any valid SQL statement (SELECT, INSERT, UPDATE, DELETE)
- `parameters` (optional): A dictionary containing parameters for parameterized queries. Use this for safer query execution to prevent SQL injection attacks.

## Supported Operations

### Data Retrieval (SELECT)
```python
# Simple select
tool.run(query="SELECT * FROM customers")

# Complex select with joins
tool.run(query="""
    SELECT c.name, c.email, COUNT(o.id) as order_count 
    FROM customers c 
    LEFT JOIN orders o ON c.id = o.customer_id 
    GROUP BY c.id, c.name, c.email
""")
```

### Data Modification (INSERT, UPDATE, DELETE)
```python
# Insert single record
tool.run(query="INSERT INTO products (name, description, price) VALUES ('New Product', 'Description', 19.99)")

# Update records
tool.run(query="UPDATE customers SET phone = '555-9999' WHERE email = 'john@example.com'")

# Delete records
tool.run(query="DELETE FROM orders WHERE quantity = 0")
```

### Parameterized Queries (Recommended)
```python
# Safe parameter substitution
tool.run(
    query="SELECT * FROM customers WHERE created_at BETWEEN ? AND ?",
    parameters={"start_date": "2023-01-01", "end_date": "2023-12-31"}
)

tool.run(
    query="INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
    parameters={"name": "Jane Smith", "email": "jane@example.com", "phone": "555-0456"}
)
```

## Response Format
The tool returns formatted responses based on the query type:

- **SELECT queries**: Returns row count and formatted data
- **INSERT/UPDATE/DELETE**: Returns success message with affected row count
- **Errors**: Returns detailed error messages for troubleshooting

## Security Best Practices

1. **Use parameterized queries** when dealing with user input to prevent SQL injection
2. **Store your API key securely** in environment variables, not in code
3. **Limit database permissions** in your GibsonAI project to only what's needed
4. **Validate input data** before constructing queries
5. **Use transactions** for multi-step operations when supported

## Error Handling
The tool provides comprehensive error handling for:
- Invalid SQL syntax
- Authentication failures
- Network connectivity issues
- Database constraint violations
- Timeout errors

## Integration with CrewAI Agents
This tool is designed to work seamlessly with CrewAI agents for database-driven workflows:

```python
from crewai import Agent, Task, Crew
from crewai_tools import GibsonAIQueryTool

# Create database agent
db_agent = Agent(
    role='Database Analyst',
    goal='Query and analyze customer data',
    backstory='Expert in SQL and data analysis',
    tools=[GibsonAIQueryTool()],
    verbose=True
)

# Create analysis task
analysis_task = Task(
    description='Find the top 10 customers by order value',
    agent=db_agent,
    expected_output='List of top customers with their total order values'
)

# Execute the crew
crew = Crew(agents=[db_agent], tasks=[analysis_task])
result = crew.kickoff()
```

## Troubleshooting

### Common Issues
1. **"Missing GIBSONAI_API_KEY"**: Ensure your API key is set in the environment or passed to the constructor
2. **"Unauthorized"**: Verify your API key is correct and has the necessary permissions
3. **"Invalid query"**: Check your SQL syntax and ensure it matches your schema
4. **"Connection failed"**: Check your internet connection and GibsonAI service status

### Getting Help
- Check your GibsonAI project's Data API documentation
- Verify your database schema in the GibsonAI console
- Test simple queries first before complex operations
- Use parameterized queries for dynamic content
