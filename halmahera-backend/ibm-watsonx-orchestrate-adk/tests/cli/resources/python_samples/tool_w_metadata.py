from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission


@tool(name="myName", description="the description", permission=ToolPermission.ADMIN)
def my_tool(input: str) -> str:
    pass
