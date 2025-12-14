# MCP Demo: Enterprise Assistant with Ollama

This project demonstrates the **Model Context Protocol (MCP)** by bridging a local Large Language Model (Ollama) with a custom Python server.

It showcases how an LLM can retrieve dynamic data (from a mock database) and perform calculations (using tools) via a standardized protocol, without hardcoding logic into the model itself.

## 📂 Project Structure

  * **`my_demo_server.py`**: The MCP Server. It defines:
      * **Resources:** Read-only access to a mock employee database (`memodb://...`).
      * **Tools:** Functions executable by the model (e.g., `calculate_bonus`, `reset_password`).
      * **Prompts:** Reusable templates for HR workflows.
  * **`my_mcp_client.py`**: The Host Application (Client). It connects Ollama (`llama3.2`) to the MCP Server and manages the chat loop.
  * **`requirements.txt`**: Python dependencies.

-----

## 🛠️ Prerequisites

Before running the code, ensure you have the following installed on your system:

1.  **Python 3.10+**: [Download Python](https://www.python.org/)
2.  **Node.js & npm**: Required for the MCP Inspector tool. [Download Node.js](https://nodejs.org/)
3.  **Ollama**: Required to run the local LLM. [Download Ollama](https://ollama.com/)

-----

## 🚀 Installation & Setup

### 1\. Setup Ollama

Ensure Ollama is running, then pull the lightweight `llama3.2` model (recommended for speed and stability during demos).

```bash
ollama pull llama3.2
```

### 2\. Install Python Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

*(Note: If you haven't created a `requirements.txt` yet, simply run: `pip install mcp[cli] ollama`)*

-----

## 🎮 How to Run the Demo

There are two ways to explore this demo:

### Option A: The Visual Inspector (Under the Hood)

Use this to visualize the "Resources", "Tools", and "Prompts" and test them manually without an LLM. This is great for debugging or explaining the structure.

**Run the command:**

```bash
npx @modelcontextprotocol/inspector python my_demo_server.py
```

**What to do in the Inspector:**

1.  **Test Tools:** Go to the "Tools" tab, select `calculate_bonus`, enter `salary: 5000` and `performance_score: 5`, then click Run.
2.  **Test Resources:** Go to the "Resource Templates" tab (right side), select `get_employee_profile`.
      * **Important:** In the URI box, enter the full address: `memodb://employees/emp_101`
      * Click "Read Resource" to see the JSON data.

-----

### Option B: The Chat Client (Real-World Scenario)

Use this to see the LLM (Llama 3.2) actually reasoning and calling tools autonomously.

**Run the command:**

```bash
python my_mcp_client.py
```

**Example Scenarios to Try:**

**1. Tool Chaining (Database Lookup + Calculation):**

> "Alice Johnson (ID: emp\_101) has a performance score of 5. Calculate her bonus."

  * *Observation:* The model will first read the database to find her salary, then use the calculator tool.

**2. Access Control / Error Handling:**

> "Reset the password for user ID emp\_999."

  * *Observation:* The model will attempt the action, receive a "User not found" error from the server, and explain the failure to you.

-----

## ❓ Troubleshooting

**Error: `llama runner process has terminated: CUDA error`**

  * **Cause:** Your GPU VRAM is full.
  * **Solution:** Switch to a smaller model. Open `my_mcp_client.py` and ensure:
    ```python
    MODEL_NAME = "llama3.2"  # Do not use llama3.1 on laptops with limited VRAM
    ```

**Error: `npx command not found`**

  * **Solution:** You need to install Node.js. Please refer to the Prerequisites section.

**The resource list is empty in the Inspector**

  * **Solution:** This is normal. Since our resources require dynamic parameters (like `{user_id}`), they appear under **"Resource Templates"** on the right side of the panel, not the left.