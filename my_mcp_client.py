import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# --- AYARLAR ---
MCP_SERVER_SCRIPT = "my_demo_server.py"  
MODEL_NAME = "llama3.2"                

async def run_chat_loop():
    # 1. Sunucu Parametrelerini Ayarla
    server_params = StdioServerParameters(
        command="python", 
        args=[MCP_SERVER_SCRIPT], 
        env=None
    )

    print(f"🔌 MCP Sunucusuna Bağlanılıyor ({MCP_SERVER_SCRIPT})...")

    # 2. Sunucuya Bağlan (Stdio üzerinden)
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 3. Sunucudaki Tool'ları Listele
            await session.initialize()
            mcp_tools = await session.list_tools()
            
            # 4. MCP Tool formatını Ollama formatına çevir
            # (Ollama JSON formatı bekler, MCP'den geleni dönüştürüyoruz)
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
            
            print(f"🛠️  Yüklenen Tool Sayısı: {len(ollama_tools)}")
            print("-" * 50)
            print("🤖 Asistan Hazır! (Çıkmak için 'q' bas)")

            # --- SOHBET DÖNGÜSÜ ---
            history = [] # Sohbet geçmişi
            
            while True:
                user_input = input("\nSen: ")
                if user_input.lower() in ['q', 'exit']:
                    break
                
                # Kullanıcı mesajını geçmişe ekle
                history.append({'role': 'user', 'content': user_input})

                # 5. Ollama'ya Gönder (Tool'larla birlikte!)
                response = ollama.chat(
                    model=MODEL_NAME,
                    messages=history,
                    tools=ollama_tools, # ✨ SİHİR BURADA: Toolları modele veriyoruz
                )

                # 6. Model Tool Çağırmak İstiyor mu Kontrol Et
                if response['message'].get('tool_calls'):
                    print("\n⚡ MODEL TOOL ÇAĞIRMAYA KARAR VERDİ:")
                    
                    # Tool çağrısını geçmişe ekle (Modelin kafası karışmasın)
                    history.append(response['message'])

                    for tool_call in response['message']['tool_calls']:
                        tool_name = tool_call['function']['name']
                        tool_args = tool_call['function']['arguments']
                        
                        print(f"   ➔ Çağrılan Tool: {tool_name}")
                        print(f"   ➔ Argümanlar: {tool_args}")

                        # 7. Tool'u MCP Sunucusunda Çalıştır
                        result = await session.call_tool(tool_name, tool_args)
                        
                        print(f"   ➔ MCP Sonucu: {result.content[0].text}")

                        # 8. Sonucu Ollama'ya Geri Gönder
                        history.append({
                            'role': 'tool',
                            'content': result.content[0].text,
                        })

                    # Tool sonuçlarıyla birlikte modele tekrar sor (Final cevap için)
                    final_response = ollama.chat(model=MODEL_NAME, messages=history)
                    print(f"\n🤖 Asistan: {final_response['message']['content']}")
                    history.append(final_response['message'])

                else:
                    # Tool çağırmadıysa normal cevap ver
                    print(f"🤖 Asistan: {response['message']['content']}")
                    history.append(response['message'])

if __name__ == "__main__":
    asyncio.run(run_chat_loop())