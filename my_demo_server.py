from mcp.server.fastmcp import FastMCP
import sqlite3
import psutil
import json

# Initialize Database (Mock Enterprise DB)
def initialize_database():
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employees 
                 (id TEXT PRIMARY KEY, name TEXT, role TEXT, salary REAL, performance INTEGER)''')
    
    # Seed data
    c.execute("INSERT OR IGNORE INTO employees VALUES ('emp_101', 'Alice Johnson', 'Senior Dev', 90000, 5)")
    c.execute("INSERT OR IGNORE INTO employees VALUES ('emp_102', 'Bob Smith', 'Marketing Lead', 65000, 3)")
    c.execute("INSERT OR IGNORE INTO employees VALUES ('emp_103', 'Charlie Davis', 'Intern', 30000, 4)")
    
    conn.commit()
    conn.close()

initialize_database()

mcp = FastMCP("Enterprise Omni-System")

# --- RESOURCES ---

@mcp.resource("system://logs/latest")
def get_system_logs() -> str:
    """Returns the latest system health metrics (CPU, RAM)."""
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    return f"""
    --- SYSTEM HEALTH REPORT ---
    CPU Usage: {cpu_usage}%
    RAM Usage: {memory.percent}%
    Available RAM: {memory.available / (1024**3):.2f} GB
    Status: {'CRITICAL' if cpu_usage > 80 else 'NOMINAL'}
    """

@mcp.resource("biz://policy/bonus")
def get_bonus_policy() -> str:
    """Returns the official company bonus policy text."""
    return """
    COMPANY BONUS POLICY (2025):
    1. Performance Score 5: 20% of annual salary.
    2. Performance Score 3-4: 10% of annual salary.
    3. Performance Score < 3: No bonus.
    4. Engineering roles receive an additional 5% tech allowance.
    """

# --- TOOLS ---

@mcp.tool()
def query_employee(query_sql: str) -> str:
    """
    Executes a SQL query on the 'employees' table. 
    Columns: id, name, role, salary, performance.
    """
    try:
        conn = sqlite3.connect('company.db')
        c = conn.cursor()
        c.execute(query_sql)
        results = c.fetchall()
        conn.close()
        return json.dumps(results)
    except Exception as e:
        return f"SQL Error: {str(e)}"

@mcp.tool()
def calculate_bonus(salary: float, performance_score: int) -> str:
    """Calculates the exact bonus amount based on salary and performance score (1-5)."""
    if performance_score >= 5:
        bonus = salary * 0.20
    elif performance_score >= 3:
        bonus = salary * 0.10
    else:
        bonus = 0.0
    return f"Calculated Bonus: ${bonus}"
# ---------------------------------------

@mcp.tool()
def analyze_server_health() -> str:
    """Analyzes current server telemetry and returns a summary report."""
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    analysis = "ANALYSIS RESULT:\n"
    if cpu > 50:
        analysis += "⚠️ WARNING: High CPU load detected! Optimization recommended.\n"
    else:
        analysis += "✅ CPU status is stable.\n"
        
    analysis += f"📊 Current Load -> CPU: {cpu}%, RAM: {ram}%"
    return analysis

if __name__ == "__main__":
    mcp.run()