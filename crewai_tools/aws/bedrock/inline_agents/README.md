# BedrockInlineAgentTool

The `BedrockInlineAgentTool` enables CrewAI agents to leverage Amazon Bedrock Inline Agents within your workflows. Inline agents run directly within your CrewAI process, providing powerful capabilities like code interpretation and knowledge base access for AWS service analysis, security assessment, and infrastructure optimization.

## Installation

```bash
pip install 'crewai[tools]'
```

## Requirements

- AWS credentials configured (either through environment variables or AWS CLI)
- `boto3` and `python-dotenv` packages
- Access to Amazon Bedrock models

## Usage

Here are two distinct ways to initialize and use the `BedrockInlineAgentTool`:

### Method 1: Direct Parameter Initialization

```python
from crewai import Agent, Task, Crew
from crewai_tools.aws.bedrock import BedrockInlineAgentTool

# Initialize the tool with direct parameters
aws_security_analyzer = BedrockInlineAgentTool(
    model_id="bedrock/us.amazon.nova-pro-v1:0",
    region_name="us-east-1",
    instruction="""You are an AWS security analysis expert specializing in identifying security vulnerabilities and compliance issues.
    
    For each security analysis request:
    1. Analyze the AWS resource configuration provided
    2. Identify potential security vulnerabilities and compliance issues
    3. Generate Python code to analyze security groups, IAM policies, and network configurations
    4. Provide detailed security recommendations with specific AWS best practices
    5. Create visualizations of security findings when appropriate
    6. Prioritize findings based on severity and potential impact
    7. Reference relevant AWS security standards (e.g., AWS Well-Architected Framework, CIS Benchmarks)
    
    IMPORTANT: You MUST save any generated reports as both HTML and PDF files with clear, descriptive filenames.
    """,
    enable_trace=True,
    enable_code_interpreter=True,
    knowledge_base_id="your-security-kb-id",
    kb_description="AWS security best practices and compliance requirements knowledge base",
    output_folder="security_reports",
    name="AWS_Security_Analyzer",
    description="Analyze AWS resources for security vulnerabilities and compliance issues."
)
```

### Method 2: Configuration-Based Initialization

You can store your Bedrock agent configurations in a YAML file. This file can be placed in the same folder as your CrewAI `agents.yaml` and `tasks.yaml` configuration files for a unified configuration approach.

Example `bedrock_agents.yaml` file:

```yaml
service_limits_analyzer:
  model_id: "bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0"
  instruction: |
    You are an AWS service limits and quotas expert.
    Your task is to analyze AWS service usage, identify potential quota issues, and recommend solutions.
    
    For each analysis request:
    1. Identify current service usage and applicable quotas
    2. Analyze usage patterns and growth trends
    3. Flag services approaching their limits
    4. Generate Python code to visualize usage vs. quotas
    5. Recommend quota increase requests with justifications
    6. Suggest architectural changes to work within existing quotas
    7. Provide best practices for quota management
  enable_code_interpreter: true
  knowledge_base_id: "your-aws-quotas-kb-id"
  kb_description: "AWS service quotas and limits knowledge base"
  name: "AWS_Service_Limits_Analyzer"
  description: "Analyze AWS service usage against quotas and recommend solutions."
```

Using the configuration file:

```python
from crewai import Agent, Task, Crew
from crewai_tools.aws.bedrock import BedrockInlineAgentTool, ConfigLoader

# Create a ConfigLoader instance
config_loader = ConfigLoader(verbose=True)

# Load the Bedrock agent config
bedrock_agent_config = config_loader.load_config("config/bedrock_agents.yaml")

# Initialize the tool using config
service_limits_analyzer = BedrockInlineAgentTool(
    config=bedrock_agent_config["service_limits_analyzer"],
    region_name="us-east-1",
    output_folder="service_reports"
)
```

### Using the Tool with CrewAI

```python
# Create a CrewAI agent that uses the tool
aws_architect = Agent(
    role='AWS Solutions Architect',
    goal='Analyze AWS infrastructure for security, cost, and performance optimization',
    backstory='I am an experienced AWS Solutions Architect with expertise in security, compliance, and infrastructure optimization.',
    tools=[aws_security_analyzer, service_limits_analyzer],
    verbose=True
)

# Create a task for the agent
security_task = Task(
    description="Analyze our AWS environment for security vulnerabilities, focusing on EC2 security groups, IAM policies, and S3 bucket configurations.",
    agent=aws_architect
)

# Create a crew with the agent
crew = Crew(
    agents=[aws_architect],
    tasks=[security_task],
    verbose=2
)

# Run the crew
result = crew.kickoff()
print(result)
```

## Tool Arguments

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| config | dict | Yes* | None | Configuration dictionary for the tool (alternative to individual parameters) |
| model_id | str | Yes* | None | The Bedrock model ID to use for the inline agent. Follow model |
| region_name | str | Yes* | "us-east-1" | AWS region for Bedrock |
| instruction | str | Yes* | None | Instructions for the inline agent |
| enable_trace | bool | No | False | Whether to enable trace logging |
| enable_code_interpreter | bool | No | True | Whether to enable code interpreter |
| knowledge_base_id | str | No | None | ID of the Bedrock knowledge base to use |
| kb_description | str | No | None | Description of the knowledge base |
| kb_num_results | int | No | 3 | Number of results to return from the knowledge base |
| kb_search_type | str | No | "HYBRID" | Type of search to perform (HYBRID, SEMANTIC) |
| lambda_function_arn | str | No | None | Optional Lambda function ARN for custom actions |
| action_group_name | str | No | None | Name for the custom action group |
| output_folder | str | No | "output" | Folder to save generated files |
| name | str | No | "BedrockInlineAgent" | Custom name for the tool |
| description | str | No | "Use this tool to interact with an Amazon Bedrock Inline Agent." | Custom description for the tool |

*Either provide the `config` parameter OR the required individual parameters (`model_id`, `region_name`, `instruction`)

## Environment Variables

```bash
AWS_REGION=your-aws-region               # Defaults to us-east-1
AWS_ACCESS_KEY_ID=your-access-key        # Required for AWS authentication
AWS_SECRET_ACCESS_KEY=your-secret-key    # Required for AWS authentication
BEDROCK_KB_ID=your-knowledge-base-id     # Optional: Knowledge base ID
```

## Error Handling

The BedrockInlineAgentTool uses custom exceptions to provide more meaningful error messages. Here's how to handle these exceptions in your code:

```python
from crewai_tools.aws.bedrock import BedrockInlineAgentTool
from crewai_tools.aws.bedrock.exceptions import BedrockAgentError, BedrockValidationError

try:
    # Initialize the tool
    bedrock_agent = BedrockInlineAgentTool(
        model_id="bedrock/us.amazon.nova-pro-v1:0",
        region_name="us-east-1",
        instruction="You are an AWS security expert...",
        enable_code_interpreter=True
    )
    
    # Run a query
    result = bedrock_agent.run("Analyze my EC2 security groups")
    print(result)
    
except BedrockValidationError as e:
    # Handle validation errors (missing or invalid parameters)
    print(f"Configuration error: {str(e)}")
    # Example: "Configuration error: model_id must be provided either directly or through config"
    
except BedrockAgentError as e:
    # Handle Bedrock agent execution errors
    print(f"Bedrock Agent error: {str(e)}")
    
    # You can access the original exception if needed
    if e.__cause__:
        print(f"Original error: {e.__cause__}")
        
except Exception as e:
    # Handle any other unexpected errors
    print(f"Unexpected error: {str(e)}")
```

### Common Validation Errors

The tool performs validation on required parameters and will raise `BedrockValidationError` in these cases:

- Missing model ID: `"model_id must be provided either directly or through config"`
- Missing region: `"region_name must be provided either directly or through config"`
- Missing instructions: `"instruction must be provided either directly or through config"`

### Agent Execution Errors

When interacting with the Bedrock service, various errors might occur. The tool wraps these in `BedrockAgentError` exceptions:

- Authentication failures
- Service unavailability
- Rate limiting
- Invalid model ID
- Knowledge base access issues

These errors are captured and wrapped with additional context to help with troubleshooting.

## Use Cases

### Federated Agent Architecture
- **Why it matters**: Different parts of your organization have different AI needs and security requirements
- **How this helps**: Create a federated architecture where some agents run in CrewAI and others in AWS Bedrock
- **Business value**: Build a flexible AI ecosystem that can adapt to different departmental needs while maintaining central orchestration

### Computational Offloading
- **Why it matters**: Some tasks require significant computational resources that may not be available in your CrewAI environment
- **How this helps**: Offload resource-intensive operations like data processing and visualization to AWS Bedrock's infrastructure
- **Business value**: Optimize resource utilization by running intensive tasks in the cloud while keeping orchestration logic in CrewAI

### Security and Compliance Boundary Control
- **Why it matters**: Your organization has strict security policies about where sensitive data can be processed
- **How this helps**: Keep sensitive AWS configuration data and analysis within your AWS security boundary
- **Business value**: Maintain compliance with data sovereignty requirements while still leveraging AI agent capabilities

### Specialized Capability Access
- **Why it matters**: You need specialized capabilities like code interpretation that may not be available in your primary LLM
- **How this helps**: Access Bedrock's code interpreter and other specialized capabilities through the inline agent interface
- **Business value**: Extend your agent capabilities without having to switch your entire workflow to a different platform

### Configuration-Driven Agent Design
- **Why it matters**: You want business users to be able to define agent behaviors without changing code
- **How this helps**: Define agent personalities, instructions, and capabilities in configuration files that can be edited by non-developers
- **Business value**: Accelerate development cycles by separating agent configuration from application code

### AWS Service Integration
- **Why it matters**: Your workflows need to interact with AWS services but you don't want to build custom integrations
- **How this helps**: Leverage Bedrock's native AWS service integrations through the inline agent interface
- **Business value**: Reduce development time by using pre-built integrations rather than creating custom API connections

