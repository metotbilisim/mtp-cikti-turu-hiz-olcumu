import json, sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hiz
LOG = os.path.expandvars(r"%LOCALAPPDATA%\Ollama\server.log")
JSONP = open(r"C:\Users\<kullanici>\Documents\Localaitest\sektor-test\sektorler\saglik\data\saglik-3\prompt.md", encoding="utf-8").read()
DUZ = "Yerel yapay zekâ modellerinin bir sağlık kuruluşunda hangi işlerde kullanılabileceğini maddeler hâlinde, ayrıntılı anlat."
def last_accept():
    t = open(LOG, encoding="utf-8", errors="ignore").read()
    m = re.findall(r"draft acceptance = ([0-9.]+) \(\s*(\d+) accepted /\s*(\d+) generated\), mean len =\s*([0-9.]+)", t)
    return m[-1] if m else None
out = []
for model in sys.argv[1:]:
    hiz.unload_all(); hiz.chat(model, "Merhaba, tek kelimeyle cevap ver.", 8)
    for ad, p, n in [("duz-1", DUZ + " (a)", 800), ("json-1", JSONP, 1500), ("duz-2", DUZ + " (b)", 800), ("json-2", "[2]\n" + JSONP, 1500)]:
        r = hiz.chat(model, p, n); r["test"] = ad; r["kabul"] = last_accept() if "gemma" in model else None; r["model"] = model; out.append(r)
    hiz.unload_all()
print(json.dumps(out, ensure_ascii=False, indent=0))
