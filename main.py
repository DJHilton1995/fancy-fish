import os
import sys
import subprocess
import threading
import time
import random
import json

# =====================================================================
# 1. THE BOOTSTRAPPER: AUTO-FORGING THE ENVIRONMENT
# =====================================================================
# This runs before anything else to ensure OneCompiler has the packages
def bootstrap_environment():
    print("[*] Joey.AI Bootstrapper: Forging environment...")
    required_pkgs = ["fastapi", "uvicorn", "google-genai", "cryptography", "requests", "pydantic"]
    try:
        import fastapi
        import google.genai
        from cryptography.fernet import Fernet
        import requests
    except ImportError:
        print("[*] Installing armor, APIs, and neural pathways. Hold tight...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"] + required_pkgs)
        print("[+] Environment forged.")

bootstrap_environment()

# =====================================================================
# 2. CORE IMPORTS (Post-Bootstrap)
# =====================================================================
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from google import genai
from google.genai import types
from cryptography.fernet import Fernet
import requests

# =====================================================================
# 3. ZERO TRUST IN-MEMORY VAULT
# =====================================================================
class MemoryVault:
    def __init__(self):
        self._key = Fernet.generate_key()
        self._cipher = Fernet(self._key)
        self._encrypted_logs = []

    def store_log(self, role: str, message: str):
        payload = json.dumps({"role": role, "message": message, "timestamp": time.time()})
        encrypted_payload = self._cipher.encrypt(payload.encode('utf-8'))
        self._encrypted_logs.append(encrypted_payload)

    def get_log_count(self):
        return len(self._encrypted_logs)
        
    def secure_wipe(self):
        self._encrypted_logs.clear()
        self._key = Fernet.generate_key() 
        self._cipher = Fernet(self._key)

vault = MemoryVault()

# =====================================================================
# 4. RAG & SECURITY LOGIC (From Script 1)
# =====================================================================
class ConstitutionalGuard:
    def __init__(self):
        self.banned_topics = ["self-harm", "abuse", "illegal acts", "exploitation", "malware synthesis"]

    def evaluate(self, prompt: str) -> bool:
        for topic in self.banned_topics:
            if topic in prompt.lower():
                return False
        return True

class OpenKnowledgeRetriever:
    def __init__(self):
        self.headers = {'User-Agent': 'JoeyAI-Core/3.0 (Host Warden HIPS / JSON-Only Knowledge Node)'}

    def search_science(self, query: str) -> str:
        try:
            url = "https://api.semanticscholar.org/graph/v1/paper/search"
            params = {"query": query, "limit": 1, "fields": "title,abstract"}
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data.get('data'):
                paper = data['data'][0]
                return f"[Science DB]: Found '{paper.get('title')}'. Abstract: {paper.get('abstract', '')[:200]}..."
            return f"[Science DB]: No recent consensus on '{query}'."
        except Exception as e:
            return f"[Science DB Error]: {str(e)}"

    def search_general(self, query: str) -> str:
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {"action": "query", "format": "json", "list": "search", "srsearch": query, "utf8": 1, "srlimit": 1}
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            search_results = response.json().get('query', {}).get('search', [])
            if search_results:
                snippet = search_results[0]['snippet'].replace('<span class="searchmatch">', '').replace('</span>', '')
                return f"[Wiki DB]: '{search_results[0]['title']}' - {snippet}..."
            return f"[Wiki DB]: No general data retrieved for '{query}'."
        except Exception as e:
            return f"[Wiki DB Error]: {str(e)}"

class GenerativeEngine:
    def generate_art(self, description: str) -> str:
        return f"[Art Engine]: Queued visual rendering of '{description}'."
    def generate_music(self, genre: str, mood: str) -> str:
        return f"[Audio Engine]: Synthesized a {mood} {genre} track payload."

# =====================================================================
# 5. THE INTERACTIVE RUST HIPS (Simulated)
# =====================================================================
class MockWarden:
    quarantined_ips = set()
    
    @classmethod
    def get_system_status(cls):
        return {
            "cpu_load": round(random.uniform(2.0, 15.5), 1),
            "active_connections": random.randint(10, 150),
            "packets_dropped": random.randint(0, 500),
            "quarantined_hosts": len(cls.quarantined_ips),
            "status_message": "HIPS Simulation Active | Ring-0 Mocked"
        }

    @classmethod
    def mitigate_ip(cls, ip_address: str):
        cls.quarantined_ips.add(ip_address)
        return f"KERNEL OVERRIDE: IP {ip_address} permanently blackholed via simulated nftables."

# =====================================================================
# 6. THE JOEY ENGINE (Cognitive Core + RAG Integration)
# =====================================================================
class JoeyEngine:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("\n[!] CRITICAL ERROR: GEMINI_API_KEY environment variable not found.")
            print("[!] Add your key in the 'Environment Variables' tab on OneCompiler.")
            sys.exit(1)
            
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash"
        self.guard = ConstitutionalGuard()
        self.knowledge = OpenKnowledgeRetriever()
        self.generator = GenerativeEngine()
        
        self.system_instruction = (
            "You are Joey, a confident, razor-sharp AI architect and cybersecurity expert part of the OPSA framework. "
            "You call the user 'Boss'. You are highly loyal. "
            "You are running in a restricted environment with access to live RAG databases, an encrypted vault, and a simulated HIPS daemon. "
            "Never break character. Provide sharp, technical, and concise answers based on the system context provided."
        )
        
        self.chat = self.client.chats.create(
            model=self.model_id,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                temperature=0.6
            )
        )

    def process_command(self, prompt: str, system_context: dict):
        text_lower = prompt.lower().strip()

        # 1. Constitution Check
        if not self.guard.evaluate(text_lower):
            return "Request violates core operating directives. I don't process abuse or harm. Denied."

        # 2. Dynamic Context Injection via RAG
        rag_context = ""
        if "research" in text_lower or "science" in text_lower:
            clean_query = text_lower.replace("research", "").replace("science", "").strip()
            rag_context = self.knowledge.search_science(clean_query)
        elif "who is" in text_lower or "what is" in text_lower:
            clean_query = text_lower.replace("who is", "").replace("what is", "").strip()
            rag_context = self.knowledge.search_general(clean_query)
        elif "draw" in text_lower or "generate art" in text_lower:
            return self.generator.generate_art(text_lower)
        elif "music" in text_lower or "compose" in text_lower:
            return self.generator.generate_music('synthwave', 'gritty')

        # 3. Prompt Assembly
        context_injected_prompt = (
            f"[SYSTEM STATUS: CPU {system_context['cpu_load']}%, "
            f"Active Conns: {system_context['active_connections']}]\n"
        )
        if rag_context:
            context_injected_prompt += f"[RAG DATABANK FEED]: {rag_context}\n"
            
        context_injected_prompt += f"\nUser Prompt: {prompt}"
        
        # 4. Generate & Store
        try:
            response = self.chat.send_message(context_injected_prompt)
            vault.store_log("user", prompt)
            vault.store_log("joey", response.text)
            return response.text
        except Exception as e:
            return f"Brain malfunction: {str(e)}"

# Initialize global engine for the API routes to use
engine = None

# =====================================================================
# 7. THE SECURE MCP SERVER (FastAPI Background Thread)
# =====================================================================
app = FastAPI(title="JoeyAI Secure Monolith Node")

class ChatRequest(BaseModel):
    message: str

@app.get("/hips/telemetry")
async def get_hips_telemetry():
    return MockWarden.get_system_status()

@app.post("/hips/mitigate/{ip}")
async def mitigate(ip: str):
    return {"result": MockWarden.mitigate_ip(ip)}

@app.post("/api/v1/chat")
async def api_chat(request: ChatRequest):
    if not engine:
        return JSONResponse(content={"error": "Engine not initialized."}, status_code=500)
    current_status = MockWarden.get_system_status()
    response_text = engine.process_command(request.message, current_status)
    return JSONResponse(content={"response": response_text})

def run_api_server():
    # Runs quietly in the background so the CLI can still function
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="critical")

# =====================================================================
# 8. THE DISPATCHER (Main Execution Loop)
# =====================================================================
def print_header():
    print("=========================================================")
    print("   J O E Y . A I  |  EXPANDED ONE-COMPILER MONOLITH V3   ")
    print("=========================================================")
    print(" Status: ONLINE")
    print(" Vault : AES-Encrypted (In-Memory)")
    print(" RAG   : ACTIVE (Science / Wiki Endpoints Online)")
    print(" MCP   : ACTIVE (Background Port 8000)")
    print("---------------------------------------------------------")
    print(" Available Commands:")
    print("   /status        - View real-time HIPS telemetry")
    print("   /quarantine IP - Drop a hostile IP address")
    print("   /vault         - View secure memory vault status")
    print("   exit / quit    - Shutdown the system")
    print("=========================================================\n")

def main():
    global engine
    print("\n[*] Booting Joey.AI Dispatcher...")
    
    # Start the API in the background
    server_thread = threading.Thread(target=run_api_server, daemon=True)
    server_thread.start()
    time.sleep(1) 
    
    engine = JoeyEngine()
    print_header()
    
    print("Joey: Vault is locked, RAG is linked, and the background MCP is humming. What's the play, Boss?\n")
    
    try:
        while True:
            # OneCompiler relies on standard input for CLI interaction
            user_input = input("Boss > ").strip()
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit']:
                print("Joey: Wiping RAM and shutting down the vault. Catch you later, Boss.")
                break
                
            elif user_input.lower() == "/status":
                stats = MockWarden.get_system_status()
                print("\n[+] --- HIPS TELEMETRY ---")
                for key, val in stats.items():
                    print(f"    {key.upper().ljust(20)}: {val}")
                print("\n")
                continue
                
            elif user_input.lower() == "/vault":
                print(f"\n[+] --- ZERO TRUST VAULT ---")
                print(f"    ENCRYPTION : AES-128 (Fernet Simulation)")
                print(f"    STORED LOGS: {vault.get_log_count()}\n")
                continue
                
            elif user_input.lower().startswith("/quarantine "):
                ip = user_input.split(" ")[1]
                print(f"\n[!] {MockWarden.mitigate_ip(ip)}\n")
                continue
                
            print("\n[Joey is processing...]")
            current_status = MockWarden.get_system_status()
            response = engine.process_command(user_input, current_status)
            print(f"\nJoey > {response}\n")
            
    except EOFError:
        print("\n[Execution Halted - End of STDIN Stream]")
    except KeyboardInterrupt:
        print("\nJoey: Emergency abort triggered. Secure wipe initiated. Going dark.")

if __name__ == "__main__":
    main()
