from mcp.server.fastmcp import FastMCP
import json

# Initialize Server
mcp = FastMCP("Enterprise Demo System")

# --- MOCK DATABASE (Simulation) ---
# In a real scenario, this would be a SQL Database or an external CRM API.
employee_db = {
    "emp_101": {
        "name": "Alice Johnson",
        "role": "Senior Developer",
        "department": "Engineering",
        "last_login": "2024-12-08 09:15:00",
        "access_level": "Admin"
    },
    "emp_102": {
        "name": "Bob Smith",
        "role": "Marketing Specialist",
        "department": "Marketing",
        "last_login": "2024-12-07 14:30:00",
        "access_level": "User"
    }
}

# --- PART 1: RESOURCES ---

@mcp.resource("memodb://employees/{user_id}")
def get_employee_profile(user_id: str) -> str:
    """
    Retrieves the full profile of an employee by their ID.
    Returns JSON formatted string for the model to parse.
    """
    user_data = employee_db.get(user_id)
    
    if user_data:
        return json.dumps(user_data, indent=2)
    else:
        return "Error: Employee not found in the database."

# --- PART 2: TOOLS ---

@mcp.tool()
def calculate_bonus(salary: float, performance_score: int) -> float:
    """Calculates yearly bonus based on performance (1-5)."""
    if performance_score >= 5:
        return salary * 0.20
    elif performance_score >= 3:
        return salary * 0.10
    return 0.0

@mcp.tool()
def reset_password(user_id: str) -> str:
    """Resets the password for a specific user and generates a temporary one."""
    if user_id in employee_db:
        # Simulation of a password reset logic
        return f"SUCCESS: Password for {employee_db[user_id]['name']} has been reset. Temp pass: Xy9#mP2!"
    return "FAILED: User ID not found."

# --- PART 3: PROMPTS ---

@mcp.prompt()
def create_onboarding_plan(user_id: str) -> str:
    """Generates an onboarding checklist for a new employee based on their ID."""
    return f"""
    Please create an Onboarding Plan for the employee with ID: {user_id}.
    
    First, READ the employee's profile using the 'memodb://employees/{user_id}' resource.
    Then, based on their 'role' and 'department', generate a Day 1 checklist.
    """

if __name__ == "__main__":
    mcp.run()
