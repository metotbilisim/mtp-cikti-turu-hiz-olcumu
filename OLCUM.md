# MTP (taslak model) ölçümü: gemma4:26b, açık ve kapalı (2026-10-24)

## Düzenek
- RTX 3090 24 GB, Ollama 0.40.6, bağlam 65.536, temperature 0.3, top_p 0.95, top_k 50.
- `gemma4:26b`: Ollama paketi. Ana model (17,07 GB, Q4_K_M) + `image.draft` katmanı (0,46 GB, MTP taslak modeli) + görsel modülü (1,19 GB). Ollama bunu `--spec-type draft-mtp --spec-draft-n-max 3` ile yükler: taslak model her adımda en çok 3 token önerir, ana model bunları tek adımda doğrular.
- `gemma4-nomtp`: aynı ana model ve görsel modülü, `DRAFT` satırı çıkarılmış (`Modelfile.nomtp`). Ağırlıklar birebir aynı; tek fark taslak model. Günlükte yükleme komutunda `--spec-type` yok (doğrulandı).
- Kabul oranı ve ortalama adım uzunluğu Ollama `server.log` satırlarından: `draft acceptance = … (kabul / üretilen), mean len = …`. "mean len": ana modelin bir adımda ürettiği ortalama token (en çok 4).
- Her çıktı türü 2 deneme. Betik: `mtp_olcum.py`, ham sonuç: `mtp_olcum.json`.

## Sonuç: yazma hızı (token/sn)

| Çıktı türü | MTP açık (1 / 2) | Ort. | MTP kapalı (1 / 2) | Ort. | Kat |
|---|---|---|---|---|---|
| Türkçe düz metin | 140,7 / 134,2 | 137,5 | 108,3 / 108,7 | 108,5 | 1,27 |
| İngilizce düz metin | 147,1 / 145,9 | 146,5 | 108,9 / 108,6 | 108,8 | 1,35 |
| Düşünme metni (iç ses) | 166,2 / 162,2 | 164,2 | 106,1 / 107,3 | 106,7 | 1,54 |
| Kod (Python) | 206,9 / 215,6 | 211,3 | 107,1 / 107,6 | 107,4 | 1,97 |
| JSON (40 mesaj sınıflandırma, sağlık testi saglik-3 istemi) | 226,7 / 213,4 | 220,1 | 104,0 / 104,3 | 104,2 | 2,11 |

## Taslak kabul oranı (MTP açık)

| Çıktı türü | Kabul oranı (1 / 2) | Ortalama adım uzunluğu (1 / 2) |
|---|---|---|
| Türkçe düz metin | %41,7 / %37,7 | 2,25 / 2,13 |
| İngilizce düz metin | %46,3 / %45,4 | 2,39 / 2,36 |
| Düşünme metni | %57,7 / %55,9 | 2,73 / 2,67 |
| Kod (Python) | %84,0 / %86,5 | 3,52 / 3,59 |
| JSON | %99,7 (1.029 / 1.032) | 3,99 |

JSON 2. denemede çıktı 1. denemeyle birebir aynıydı (1.374 token); günlük satırı ayrıca okunamadı, oran 1. denemeninkidir.

## Kontrol: taslak modeli olmayan modeller (aynı gün, aynı ayar)
- Qwen3.6-35B-A3B (UD-IQ4_XS, 256 uzmandan 8'i, taslak model yok): düz metin 131,3 / 131,2; JSON 129,3 / 128,9 token/sn. Çıktı türü hızı değiştirmedi.
- qwen3.5:9b (taslak model yok; günlükte `--spec-type` yok): sağlık testinde JSON görevlerinde ort. 100,7 token/sn.

## Önceki testlerle ilişki (günlükle doğrulandı)
- Hukuk (23 Ekim), sağlık (23–24 Ekim) ve Gemma–LFM (19 Ekim) testlerinin hepsinde gemma4:26b MTP açık yüklendi (`server-1.log`, `server-2.log`: `--spec-type draft-mtp`).
- Bu testlerdeki ~216–220 token/sn MTP açıkken ölçüldü (sağlık: JSON; Gemma–LFM: kod ve uzun düşünme metni). Çıktı türüne göre kazanç değişir. MTP kapalıyken aynı model bu kartta ~104–109 token/sn yazar.
- lfm2.5-24b-a2b paketinde taslak model yok (manifest: model, params). Gemma–LFM yazısındaki 222'ye karşı 216: LFM ham hız, Gemma MTP'li hız.
- 24 Ekim sağlık testinde qwen3.5:9b (100,7) ile gemma4:26b (219,4) arasındaki yazma hızı farkının çoğu MTP'den gelir: MTP kapalı Gemma JSON'da 104,2.
