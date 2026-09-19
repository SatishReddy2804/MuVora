import os
import sys
import json
import time
import argparse
import numpy as np

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.ml.preprocessing import TextPreprocessor
from backend.ml.metrics import compute_classification_metrics


def train_model(
    vocab_size: int = 10000,
    maxlen: int = 200,
    embedding_dim: int = 128,
    lstm_units: int = 64,
    batch_size: int = 64,
    epochs: int = 5,
    output_dir: str = "models",
    val_split: float = 0.2
):
    print("=" * 60)
    print("MuVora: Training Production Bidirectional LSTM Sentiment Model")
    print("=" * 60)

    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Embedding, Bidirectional, LSTM, Dense, Dropout
        from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
        from tensorflow.keras.datasets import imdb
    except ImportError as e:
        print(f"Error importing TensorFlow: {e}", file=sys.stderr)
        print("Please ensure tensorflow is installed in the current environment.", file=sys.stderr)
        sys.exit(1)

    # Set seeds for reproducibility
    tf.random.set_seed(42)
    np.random.seed(42)

    os.makedirs(output_dir, exist_ok=True)
    model_save_path = os.path.join(output_dir, "sentiment_bilstm.keras")
    vocab_save_path = os.path.join(output_dir, "vocab.json")
    metadata_save_path = os.path.join(output_dir, "metadata.json")
    history_save_path = os.path.join(output_dir, "history.json")

    print(f"1. Loading IMDB dataset (vocab_size={vocab_size}, maxlen={maxlen})...")
    # index_from=3 accounts for <PAD>: 0, <START>: 1, <UNK>: 2
    try:
        (x_train_raw, y_train_raw), (x_test_raw, y_test_raw) = imdb.load_data(
            num_words=vocab_size,
            index_from=3
        )
    except Exception as e:
        print(f"Failed to download or load IMDB dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Train samples: {len(x_train_raw)}, Test samples: {len(x_test_raw)}")

    print("2. Preparing vocabulary and preprocessor...")
    word_index = imdb.get_word_index()
    preprocessor = TextPreprocessor(vocab_size=vocab_size, maxlen=maxlen)
    preprocessor.build_vocab_from_imdb(word_index)
    preprocessor.save_vocab(vocab_save_path)
    print(f"Saved vocabulary to {vocab_save_path}")

    print("3. Preprocessing sequences (padding/truncating)...")
    # Pad sequences
    def pad_dataset(raw_sequences):
        padded = []
        for seq in raw_sequences:
            if len(seq) > maxlen:
                p = seq[-maxlen:]
            else:
                p = [0] * (maxlen - len(seq)) + seq
            padded.append(p)
        return np.array(padded, dtype=np.int32)

    x_train_full = pad_dataset(x_train_raw)
    y_train_full = np.array(y_train_raw, dtype=np.float32)
    x_test = pad_dataset(x_test_raw)
    y_test = np.array(y_test_raw, dtype=np.float32)

    # Split train into train and validation (keep test set completely separate)
    val_size = int(len(x_train_full) * val_split)
    indices = np.random.permutation(len(x_train_full))
    train_idx, val_idx = indices[val_size:], indices[:val_size]

    x_train, y_train = x_train_full[train_idx], y_train_full[train_idx]
    x_val, y_val = x_train_full[val_idx], y_train_full[val_idx]

    print(f"Final training set: {len(x_train)}, Validation set: {len(x_val)}, Test set: {len(x_test)}")

    print("4. Building corrected neural network architecture...")
    model = Sequential([
        Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            input_length=maxlen,
            mask_zero=True
        ),
        Bidirectional(LSTM(lstm_units)),
        Dropout(0.4),
        Dense(64, activation="relu"),
        Dropout(0.3),
        Dense(1, activation="sigmoid")
    ])

    model.compile(
        loss="binary_crossentropy",
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        metrics=["accuracy"]
    )
    model.summary()

    callbacks = [
        EarlyStopping(
            monitor="val_loss",
            patience=2,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=1,
            verbose=1,
            min_lr=1e-5
        ),
        ModelCheckpoint(
            filepath=model_save_path,
            monitor="val_accuracy",
            save_best_only=True,
            verbose=1
        )
    ]

    print("5. Training model...")
    start_train_time = time.time()
    history = model.fit(
        x_train, y_train,
        validation_data=(x_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks
    )
    train_duration = time.time() - start_train_time
    print(f"Training completed in {train_duration:.1f} seconds.")

    print("6. Evaluating on independent test set...")
    y_test_pred_prob = model.predict(x_test, batch_size=batch_size, verbose=0).ravel()
    metrics = compute_classification_metrics(y_test, y_test_pred_prob)

    print("\n--- Test Set Evaluation Metrics ---")
    print(f"Accuracy:  {metrics['accuracy'] * 100:.2f}%")
    print(f"Precision: {metrics['precision'] * 100:.2f}%")
    print(f"Recall:    {metrics['recall'] * 100:.2f}%")
    print(f"F1-Score:  {metrics['f1'] * 100:.2f}%")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"Confusion Matrix:\n{metrics['confusion_matrix']['matrix']}")

    print("7. Saving model artifacts and metadata...")
    model.save(model_save_path)
    print(f"Saved model to {model_save_path}")

    # Serialize history
    serializable_history = {}
    for k, v in history.history.items():
        serializable_history[k] = [float(x) for x in v]

    with open(history_save_path, "w", encoding="utf-8") as f:
        json.dump(serializable_history, f, indent=2)

    metadata = {
        "model_name": "IMDB BiLSTM Sentiment Classifier",
        "version": "1.0.0",
        "architecture": "Embedding(10000->128) -> BiLSTM(64) -> Dropout(0.4) -> Dense(64, relu) -> Dropout(0.3) -> Dense(1, sigmoid)",
        "vocab_size": vocab_size,
        "max_sequence_length": maxlen,
        "embedding_dim": embedding_dim,
        "metrics": metrics,
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "training_duration_seconds": round(train_duration, 1)
    }

    with open(metadata_save_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved metadata to {metadata_save_path}")

    print("\nTraining and evaluation pipeline completed successfully!")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train BiLSTM Sentiment Classifier on IMDB")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs (default: 3 for fast convergence)")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size (default: 64)")
    parser.add_argument("--vocab-size", type=int, default=10000, help="Vocabulary size (default: 10000)")
    parser.add_argument("--maxlen", type=int, default=200, help="Max sequence length (default: 200)")
    parser.add_argument("--output-dir", type=str, default="models", help="Artifacts output directory")

    args = parser.parse_args()
    train_model(
        vocab_size=args.vocab_size,
        maxlen=args.maxlen,
        batch_size=args.batch_size,
        epochs=args.epochs,
        output_dir=args.output_dir
    )
