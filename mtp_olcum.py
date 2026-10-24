import json, sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hiz
LOG = os.path.expandvars(r"%LOCALAPPDATA%\Ollama\server.log")
JSONP = open(r"C:\Users\<kullanici>\Documents\Localaitest\sektor-test\sektorler\saglik\data\saglik-3\prompt.md", encoding="utf-8").read()
TESTS = [
 ("Türkçe düz metin", "Yerel yapay zekâ modellerinin bir sağlık kuruluşunda hangi işlerde kullanılabileceğini ayrıntılı, akıcı paragraflarla anlat.", 800, False),
 ("İngilizce düz metin", "Explain in detailed flowing paragraphs how a small clinic could use a local AI model for administrative work.", 800, False),
 ("JSON (mesaj sınıflandırma)", JSONP, 1500, False),
 ("Kod (Python)", "Write a complete Python module that parses a CSV file of patient appointments, validates dates and phone numbers, and writes a summary report. Include docstrings and unit tests. Output only code.", 1200, False),
 ("Düşünme metni", "Bir hastanın ilaç listesinde 3 ilaç var: Ramipril 5 mg, Furosemid 40 mg, Pantoprazol 40 mg. Olası etkileşimleri adım adım düşün ve kısa bir özet ver.", 1500, True),
]
def last_accept():
    t = open(LOG, encoding="utf-8", errors="ignore").read()
    m = re.findall(r"draft acceptance = ([0-9.]+) \(\s*(\d+) accepted /\s*(\d+) generated\), mean len =\s*([0-9.]+)", t)
    return [float(m[-1][0]), int(m[-1][1]), int(m[-1][2]), float(m[-1][3])] if m else None
def chat(model, prompt, n, think):
    r = hiz.post("/api/chat", {"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False, "think": think,
        "options": {"num_ctx": 65536, "num_predict": n, "temperature": 0.3, "top_p": 0.95, "top_k": 50}})
    return r["eval_count"], round(r["eval_count"] / (r["eval_duration"] / 1e9), 1)
out = []
for model in sys.argv[1:]:
    hiz.unload_all(); chat(model, "Merhaba, tek kelimeyle cevap ver.", 8, False)
    for ad, p, n, think in TESTS:
        for i in (1, 2):
            before = last_accept()
            ev, tps = chat(model, f"[{i}] " + p, n, think)
            acc = last_accept()
            out.append({"model": model, "test": ad, "deneme": i, "eval_tok": ev, "tok_s": tps, "kabul": acc if acc != before else None})
            print(json.dumps(out[-1], ensure_ascii=False), flush=True)
    hiz.unload_all()
json.dump(out, open("mtp_olcum.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
