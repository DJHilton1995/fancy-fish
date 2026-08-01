#!/usr/bin/env python3
"""
CLI chat companion with OpenAI chat + image generation and optional Groq support.

Commands:
  /image <prompt>   -> Generate an image with OpenAI and save it to ai_data/images/
  /groq <prompt>    -> (Optional) Send a prompt to Groq if GROQ_API_KEY and library are available
  memories          -> show saved memories
  help              -> show this help
  exit              -> quit

Run: python chat_cli.py
"""
import base64
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Optional

from fancy_fish import config

try:
    import openai
except Exception as e:
    raise RuntimeError("Install the openai package (pip install openai)") from e

# Configure model via env var OPENAI_MODEL, default to gpt-3.5-turbo
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
openai.api_key = config.OPENAI_API_KEY

DATA_DIR = Path("ai_data")
IMAGES_DIR = DATA_DIR / "images"
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CONVERSATION_FILE = DATA_DIR / "conversation.json"
MEMORIES_FILE = DATA_DIR / "memories.json"

SYSTEM_PROMPT = (
    "You are a warm, empathetic friend named 'Companion'. "
    "Be supportive, curious, and helpful. Keep responses concise but kind. "
    "When helpful, ask follow-up questions to encourage conversation."
)

# Attempt to wire Groq if available and configured
GROQ_AVAILABLE = False
GROQ_CLIENT = None
try:
    if getattr(config, "GROQ_API_KEY", None):
        try:
            # Try to import a groq client library if the user has one installed.
            # This is intentionally permissive because Groq client libraries vary.
            import groq  # type: ignore

            # Example: groq.Client(api_key=...)
            GROQ_CLIENT = getattr(groq, "Client", None)
            if callable(GROQ_CLIENT):
                GROQ_CLIENT = GROQ_CLIENT(api_key=config.GROQ_API_KEY)  # type: ignore
                GROQ_AVAILABLE = True
            else:
                GROQ_AVAILABLE = False
        except Exception:
            # groq package not installed or client init failed — leave GROQ_AVAILABLE False
            GROQ_AVAILABLE = False
    else:
        GROQ_AVAILABLE = False
except Exception:
    GROQ_AVAILABLE = False


# Load or initialize storage
def load_json(path: Path, default):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default


def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


conversation = load_json(CONVERSATION_FILE, {"messages": [{"role": "system", "content": SYSTEM_PROMPT}]})
memories = load_json(MEMORIES_FILE, [])


def chat_turn(user_text: str) -> str:
    conversation["messages"].append({"role": "user", "content": user_text})
    # Call ChatCompletion
    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=conversation["messages"],
        temperature=0.8,
        max_tokens=800,
    )
    assistant_text = resp["choices"][0]["message"]["content"].strip()
    conversation["messages"].append({"role": "assistant", "content": assistant_text})
    save_json(CONVERSATION_FILE, conversation)
    return assistant_text


def generate_image(prompt: str, size: str = "1024x1024") -> Optional[Path]:
    """Generate an image using OpenAI Images API and save it to ai_data/images."""
    try:
        resp = openai.Image.create(
            prompt=prompt,
            n=1,
            size=size,
            response_format="b64_json",
        )
        b64 = resp["data"][0]["b64_json"]
        img_bytes = base64.b64decode(b64)
        filename = f"img_{int(time.time())}.png"
        out = IMAGES_DIR / filename
        with open(out, "wb") as f:
            f.write(img_bytes)
        return out
    except Exception as e:
        print("Image generation failed:", e)
        return None


def groq_query(prompt: str) -> str:
    """Send a prompt to Groq if available. Returns a string response or raises RuntimeError."""
    if not GROQ_AVAILABLE or GROQ_CLIENT is None:
        raise RuntimeError("Groq is not available. Make sure GROQ_API_KEY is set and a groq client library is installed.")
    # The exact API depends on the groq client library. Attempt a common call shape, but don't guarantee it.
    try:
        if hasattr(GROQ_CLIENT, "generate"):
            # hypothetical: groq.Client.generate(prompt=...)
            resp = GROQ_CLIENT.generate(prompt=prompt)
            # Try to extract text
            if isinstance(resp, dict):
                return resp.get("text", str(resp))
            return str(resp)
        else:
            # Fallback: try calling client as a function or using a 'complete' method
            if callable(GROQ_CLIENT):
                rv = GROQ_CLIENT(prompt)
                return str(rv)
            return "Groq client available but we couldn't determine how to call it."
    except Exception as e:
        return f"Groq call failed: {e}"


def reflect_and_store():
    """Create a short memory summary from recent conversation and save it."""
    recent = "\n".join(f"{m['role']}: {m['content']}" for m in conversation["messages"][-12:])
    prompt = [
        {"role": "system", "content": "You are a helpful summarizer that extracts short personal memories."},
        {
            "role": "user",
            "content": (
                "Read the following recent conversation and produce a one-sentence memory that captures stable facts, "
                "preferences, or important emotional notes. Only output the memory sentence.\n\n"
                + recent
            ),
        },
    ]
    try:
        resp = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=prompt, temperature=0.3, max_tokens=100)
        memory_text = resp["choices"][0]["message"]["content"].strip()
        if memory_text:
            entry = {"timestamp": int(time.time()), "memory": memory_text}
            memories.append(entry)
            save_json(MEMORIES_FILE, memories)
            print(f"[memory saved] {memory_text}")
    except Exception as e:
        print("[reflect failed]", e)


def show_memories():
    if not memories:
        print("No memories yet.")
        return
    print("Memories:")
    for m in memories[-20:]:
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(m["timestamp"]))
        print(f"- {ts}: {m['memory']}")


def print_help():
    print("Commands:")
    print("  /image <prompt>   -> Generate an image with OpenAI and save it to ai_data/images/")
    print("  /groq <prompt>    -> (Optional) Send a prompt to Groq if GROQ_API_KEY and library are available")
    print("  memories          -> show saved memories")
    print("  help              -> show this help")
    print("  exit              -> quit")


def main():
    print("Companion: hello — I'm here to talk. Type 'help' for commands. Type 'exit' to quit.")
    if GROQ_AVAILABLE:
        print("Groq support: ENABLED")
    else:
        print("Groq support: disabled or not installed. Set GROQ_API_KEY and install a groq client to enable.")

    turn_count = 0
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit"):
            print("Bye for now. I'll be here when you return.")
            break
        if user.lower() == "memories":
            show_memories()
            continue
        if user.lower() == "help":
            print_help()
            continue
        # Image generation command
        if user.startswith("/image ") or user.startswith("image:"):
            # Extract prompt
            prompt = user.split(" ", 1)[1] if user.startswith("/image ") else user.split(":", 1)[1].strip()
            print("Generating image... this may take a moment.")
            out = generate_image(prompt)
            if out:
                print(f"Image saved to: {out}")
            else:
                print("Image generation failed.")
            continue
        # Groq command
        if user.startswith("/groq ") or user.startswith("groq:"):
            prompt = user.split(" ", 1)[1] if user.startswith("/groq ") else user.split(":", 1)[1].strip()
            try:
                resp = groq_query(prompt)
                print("Groq:\n", resp)
            except Exception as e:
                print("Groq is not available or call failed:", e)
            continue

        # Normal chat
        reply = chat_turn(user)
        print(f"\nCompanion: {reply}")
        turn_count += 1

        # After every N turns, reflect and store a short memory
        if turn_count % 8 == 0:
            try:
                reflect_and_store()
            except Exception as e:
                print("[reflect failed]", e)


if __name__ == "__main__":
    main()
