# Disease model

AgriMind uses a MobileNetV3-Large image classifier for crop-disease inference.

## Training

Use a GPU environment such as Google Colab. The reproducible training command is documented in `COLAB_TRAINING.md`.

```bash
python -m ml.train_disease \
  --root data/raw/color \
  --train-manifest data/download/color_train.txt \
  --test-manifest data/download/color_test.txt \
  --epochs 15 \
  --batch-size 64 \
  --lr 3e-4 \
  --patience 4 \
  --output ml/artifacts/best.pt
```

Outputs include the checkpoint, metrics JSON, and class mapping JSON.

The repository does not contain PlantVillage images or a fabricated checkpoint. After a real training run, store the resulting model with Git LFS or external model storage if it is too large for normal GitHub storage.
