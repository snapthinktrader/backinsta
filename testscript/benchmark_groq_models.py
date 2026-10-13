#!/usr/bin/env python3
"""
Benchmark text generation models on Groq for BackInsta:
- Latency (time to complete)
- Tokens per second
- Analysis quality
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"

MODELS = [
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "openai/gpt-oss-120b"
]

TEST_TITLE = "Global Oil Prices Surge as Middle East Tensions Escalate"
TEST_CONTENT = (
    "Brent crude surged past $85 a barrel on Tuesday amid heightened geopolitical "
    "concerns and shipping disruptions in key supply corridors. Energy analysts warn "
    "that continued volatility could push inflation higher and delay interest rate cuts "
    "by major central banks. Meanwhile, airlines and logistics firms are scrambling to hedge fuel costs."
)

PROMPT = f"""You are a senior financial analyst.
Analyze this news article for an Instagram Reel caption.
Provide a 2-3 sentence punchy insight highlighting what investors and traders need to know.

Title: {TEST_TITLE}
Content: {TEST_CONTENT}
"""

def benchmark():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("=" * 70)
    print("GROQ MODEL LATENCY & TOKEN SPEED BENCHMARK")
    print("=" * 70)

    results = []

    for model in MODELS:
        print(f"\n▶ Testing Model: {model} ...")
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a concise financial analyst."},
                {"role": "user", "content": PROMPT}
            ],
            "max_tokens": 150,
            "temperature": 0.6
        }

        # Run 2 iterations to account for cold start
        times = []
        tokens_list = []
        sample_output = ""

        for iteration in range(2):
            start = time.perf_counter()
            try:
                resp = requests.post(URL, headers=headers, json=payload, timeout=20)
                elapsed = time.perf_counter() - start
                
                if resp.status_code == 200:
                    data = resp.json()
                    usage = data.get("usage", {})
                    completion_tokens = usage.get("completion_tokens", 0)
                    times.append(elapsed)
                    tokens_list.append(completion_tokens)
                    if iteration == 1 or not sample_output:
                        sample_output = data["choices"][0]["message"]["content"].strip()
                else:
                    print(f"   Iteration {iteration+1} failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"   Iteration {iteration+1} error: {e}")

        if times:
            avg_time = sum(times) / len(times)
            avg_tokens = sum(tokens_list) / len(tokens_list)
            speed_tps = avg_tokens / avg_time if avg_time > 0 else 0
            results.append({
                "model": model,
                "avg_time": avg_time,
                "avg_tokens": avg_tokens,
                "tps": speed_tps,
                "sample": sample_output
            })
            print(f"   Avg Time: {avg_time:.3f}s | Avg Output: {avg_tokens:.0f} tokens | Speed: {speed_tps:.1f} tokens/s")
            print(f"   Sample Output:\n   \"{sample_output[:120]}...\"")

    print("\n" + "=" * 70)
    print(f"{'Model':26} | {'Latency':10} | {'Speed (tok/s)':14} | Recommendation")
    print("-" * 70)
    # Sort by speed descending
    results.sort(key=lambda x: x["tps"], reverse=True)
    for r in results:
        rec = "⚡ Best Speed & Latency" if r == results[0] else ("🧠 Deep Reasoning" if "120b" in r["model"] else "Multimodal / High Quality")
        print(f"{r['model']:26} | {r['avg_time']:.3f}s    | {r['tps']:.1f} tok/s     | {rec}")
    print("=" * 70)

if __name__ == "__main__":
    benchmark()
