from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix


def compute_classification_metrics(y_true: np.ndarray, y_pred_probs: np.ndarray, threshold: float = 0.5) -> Dict[str, Any]:
    """
    Computes standard binary classification metrics and confusion matrix.
    """
    y_true = np.array(y_true, dtype=int)
    y_pred = (np.array(y_pred_probs) >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    try:
        auc = float(roc_auc_score(y_true, y_pred_probs))
    except Exception:
        auc = 0.0

    cm = confusion_matrix(y_true, y_pred)
    # cm format: [[TN, FP], [FN, TP]]
    tn, fp, fn, tp = map(int, cm.ravel())

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(auc, 4),
        "confusion_matrix": {
            "true_negative": tn,
            "false_positive": fp,
            "false_negative": fn,
            "true_positive": tp,
            "matrix": [[tn, fp], [fn, tp]]
        },
        "threshold": threshold
    }
