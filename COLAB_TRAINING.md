# AgriMind — Colab disease-model training

This is the only runtime artifact that must be created by an actual GPU training run: the MobileNetV3-Large disease checkpoint.

## 1. Clone
```bash
!git clone https://github.com/Lokilogesh001/agri.git
%cd agri
```

## 2. Install
```bash
!pip install -q -r requirements.txt
```

## 3. Download the exact PlantVillage assets
```bash
!python scripts/setup_runtime.py
```

This downloads the official PlantVillage archive plus the official color train/test manifests. The raw image archive is intentionally not committed to GitHub.

## 4. Verify GPU
```python
import torch
print('CUDA:', torch.cuda.is_available())
print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')
```

## 5. Train MobileNetV3-Large
```bash
!python -m ml.train_disease \
  --root data/raw/color \
  --train-manifest data/download/color_train.txt \
  --test-manifest data/download/color_test.txt \
  --epochs 15 \
  --batch-size 64 \
  --lr 3e-4 \
  --patience 4 \
  --output ml/artifacts/best.pt
```

Outputs:
- `ml/artifacts/best.pt`
- `ml/artifacts/best.metrics.json`
- `ml/artifacts/best.classes.json`

The validation split is leaf-grouped and comes only from the training manifest. The official test manifest is held out for the final evaluation.

## 6. Verify
```bash
!python scripts/verify_product.py
```

Do not commit PlantVillage images or API keys. Store a large trained checkpoint with Git LFS or external model storage if required.
