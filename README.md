# NASA-NOIS2-192-AI-Services

Full-text extraction, QA/template checks, semantic embeddings and
≤ 250-word summaries for FDA decision-summary PDFs.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10.18 (recommended) |
| pip   | ≥ 22.x  |
| (Optional) Conda | any recent Miniconda/Anaconda |

---

## Quick-start (local dev)

```bash
# 1️⃣  clone this repo
git clone <this-git-url>
cd NASA-NOIS2-192-AI-Services-src-layout

# 2️⃣  create / activate a clean env (optional but recommended)
conda create -n nasa_ai python=3.10.18 -y
conda activate nasa_ai

# 3️⃣  install Python deps
pip install -r requirements.txt

# 4️⃣  one-time NLTK tokenizer download (needed by TextRank fallback)
python -m nltk.downloader punkt

# 5️⃣  install project in *editable* mode
pip install -e .

# 6️⃣ Right now the OpenAI Key is hardcoded in the script  
# (optional) add OpenAI key for GPT-4o summaries to the env variable
# set OPENAI_API_KEY=sk-...

# 7️⃣  smoke-test the full pipeline
python ai_service_test.py
