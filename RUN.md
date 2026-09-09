# Running AgriMind

## 1. Install

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Prepare PlantVillage

The full PlantVillage image archive is intentionally **not stored in GitHub**. Run:

```bash
python scripts/setup_runtime.py
```

This downloads the official repository archive and the official color train/test manifests.

## 3. Disease model

Train MobileNetV3-Large on the prepared dataset:

```bash
python -m ml.train_disease
```

The best checkpoint is written locally under `artifacts/` and is intentionally not fabricated or committed unless a real trained checkpoint is available.

## 4. Start the API

```bash
uvicorn api.main:app --reload
```

Health check: `http://127.0.0.1:8000/health`

## 5. Start the web app

```bash
cd web
npm install
npm run dev
```

Open `http://localhost:3000`.

## 6. Optional xAI explanation

Create `.env` from `.env.example` and set `XAI_API_KEY`. Never commit `.env` or API keys.

## 7. Verification

```bash
python -m compileall -q .
pytest -q
python scripts/verify_product.py
```
