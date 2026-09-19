# Models Directory

This directory stores trained model artifacts:
- `sentiment_bilstm.keras`: Trained Keras Bidirectional LSTM weights.
- `vocab.json`: Preprocessor vocabulary index mapping.
- `metadata.json`: Model version, parameters, architecture, and evaluation metrics.
- `history.json`: Epoch loss, accuracy, val_loss, and val_accuracy history.

## Training Instructions
To train the production model on the IMDB dataset:
```bash
python backend/ml/train.py --epochs 3 --batch-size 64
```
