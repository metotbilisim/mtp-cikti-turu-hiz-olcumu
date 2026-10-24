"""Kısa hız testi: model başına 1 ısınma + 2 üretim + 2 okuma çağrısı. Sektör testi değil."""
import json, subprocess, sys, urllib.request

API = "http://127.0.0.1:11434"
CTX = 65536
METIN = open(r"C:\Users\<kullanici>\Documents\Localaitest\sektor-test\sektorler\saglik\data\saglik-4\prompt.md", encoding="utf-8").read()


def post(path, body):
    req = urllib.request.Request(API + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def chat(model, prompt, num_predict):
    r = post("/api/chat", {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False, "think": False,
                           "options": {"num_ctx": CTX, "num_predict": num_predict, "temperature": 0.3, "top_p": 0.95, "top_k": 50}})
    return {"load_s": round(r.get("load_duration", 0) / 1e9, 2),
            "prompt_tok": r.get("prompt_eval_count", 0),
            "prompt_tok_s": round(r["prompt_eval_count"] / (r["prompt_eval_duration"] / 1e9), 1) if r.get("prompt_eval_duration") else None,
            "eval_tok": r.get("eval_count", 0),
            "gen_tok_s": round(r["eval_count"] / (r["eval_duration"] / 1e9), 1) if r.get("eval_duration") else None}


def vram():
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout
    return int(out.strip())


def ps():
    return [{"name": m["name"], "size_gb": round(m["size"] / 1e9, 2), "vram_gb": round(m["size_vram"] / 1e9, 2)} for m in post_get("/api/ps")["models"]]


def post_get(path):
    with urllib.request.urlopen(API + path, timeout=30) as r:
        return json.loads(r.read())


def unload_all():
    for m in post_get("/api/ps")["models"]:
        post("/api/generate", {"model": m["name"], "keep_alive": 0})


def moe_info(model):
    info = post("/api/show", {"model": model}).get("model_info", {})
    keys = ("architecture", "block_count", "expert_count", "expert_used_count", "expert_shared_count", "parameter_count", "context_length")
    return {k: v for k, v in info.items() if any(k.endswith(x) for x in keys)}


def run(model):
    unload_all()
    res = {"model": model, "moe": moe_info(model)}
    res["isinma"] = chat(model, "Merhaba, tek kelimeyle cevap ver.", 8)
    res["ps"] = ps()
    gen = "Yerel yapay zekâ modellerinin bir sağlık kuruluşunda hangi işlerde kullanılabileceğini maddeler hâlinde, ayrıntılı anlat."
    res["uretim"] = [chat(model, gen + f" (deneme {i})", 600) for i in (1, 2)]
    # Okuma: her denemede metnin başına farklı bir satır eklenir ki önbellek devreye girmesin.
    res["okuma"] = [chat(model, f"[okuma denemesi {i}]\n" + METIN + "\n\nBu metin kaç belge içeriyor? Yalnızca sayıyı yaz.", 4) for i in (1, 2)]
    res["vram_mb"] = vram()
    unload_all()
    return res


if __name__ == "__main__":
    print(json.dumps([run(m) for m in sys.argv[1:]], ensure_ascii=False, indent=1))
