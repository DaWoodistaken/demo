import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table

# Configuration
MCP_SERVER_SCRIPT = "my_demo_server.py"  
MODEL_NAME = "llama3.2"                

console = Console()

def display_header():
    console.print(Panel.fit(
        "[bold cyan]MCP ENTERPRISE CLIENT v2.0[/bold cyan]\n"
        "[dim]Powered by Llama 3.2 & Model Context Protocol[/dim]",
        border_style="blue"
    ))

async def run_chat_loop():
    display_header()
    
    # We use "-u" for unbuffered output to prevent hanging
    server_params = StdioServerParameters(
        command="python", 
        args=["-u", MCP_SERVER_SCRIPT], 
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # --- CONNECTION & INITIALIZATION ---
            with console.status("[bold green]Connecting to MCP Server...", spinner="dots"):
                await session.initialize()
                mcp_tools = await session.list_tools()
                
                # Convert MCP tools to Ollama format
                ollama_tools = []
                for tool in mcp_tools.tools:
                    ollama_tools.append({
                        'type': 'function',
                        'function': {
                            'name': tool.name,
                            'description': tool.description,
                            'parameters': tool.inputSchema
                        }
                    })
                
                resources = await session.list_resources()

            # --- DISPLAY RESOURCES ---
            console.print(f"[bold green]✓ Connected successfully![/bold green] {len(ollama_tools)} tools loaded.")
            
            r_table = Table(title="Available Resources")
            r_table.add_column("URI", style="cyan")
            r_table.add_column("Description", style="magenta")
            
            for res in resources.resources:
                r_table.add_row(str(res.uri), res.name or "No description")
            
            console.print(r_table)
            
            # --- CHAT LOOP ---
            # System prompt to prevent over-triggering tools during small talk
            history = [{
                'role': 'system', 
                'content': (
                    "You are a helpful corporate assistant. "
                    "If the user greets you (e.g., 'Hi', 'Hello'), reply naturally WITHOUT calling any tools. "
                    "ONLY use tools when the user specifically asks for data about employees, salary, or system health. "
                    "When writing SQL, ensure it is complete and valid."
                )
            }]
            
            while True:
                user_input = console.input("\n[bold yellow]You > [/bold yellow]")
                if user_input.lower() in ['q', 'exit']:
                    break
                
                history.append({'role': 'user', 'content': user_input})

                # Spinner for AI processing
                with console.status("[bold white]AI is thinking...", spinner="aesthetic") as status:
                    
                    response = ollama.chat(
                        model=MODEL_NAME,
                        messages=history,
                        tools=ollama_tools,
                    )

                    # Check if model wants to use a tool
                    if response['message'].get('tool_calls'):
                        status.update("[bold orange3]Executing Tool...", spinner="material")
                        
                        history.append(response['message'])

                        for tool_call in response['message']['tool_calls']:
                            t_name = tool_call['function']['name']
                            t_args = tool_call['function']['arguments']
                            
                            console.print(f"[dim]➔ Calling: {t_name}({t_args})[/dim]", style="italic")
                            
                            # Execute Tool via MCP
                            result = await session.call_tool(t_name, t_args)
                            tool_result_text = result.content[0].text
                            
                            console.print(Panel(tool_result_text, title=f"Output: {t_name}", border_style="green"))

                            history.append({
                                'role': 'tool',
                                'content': tool_result_text,
                            })

                        # Get final response with tool data
                        final_response = ollama.chat(model=MODEL_NAME, messages=history)
                        ai_content = final_response['message']['content']
                        history.append(final_response['message'])
                        
                    else:
                        ai_content = response['message']['content']
                        history.append(response['message'])
                
                console.print(Panel(Markdown(ai_content), title="Assistant", border_style="blue"))

if __name__ == "__main__":
    try:
        asyncio.run(run_chat_loop())
    except KeyboardInterrupt:
        console.print("\n[bold red]System shutting down...[/bold red]")