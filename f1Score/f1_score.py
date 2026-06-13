import argparse
import ast
import re
from typing import List
import pandas as pd


def clean_surrogates(text: str) -> str:
   
    if not isinstance(text, str):
        return ""
    try:
        return text.encode('utf-8', 'surrogatepass').decode('utf-8', 'ignore')
    except Exception:
        return text


def parse_list_like(s: str) -> str:
    if not isinstance(s, str):
        return ""
    
    # Clean the string from rogue surrogates before processing
    s = clean_surrogates(s).strip()
    
    if s == "":
        return ""
    try:
        val = ast.literal_eval(s)
        if isinstance(val, (list, tuple)):
            return " ".join(clean_surrogates(str(x)) for x in val)
        return clean_surrogates(str(val))
    except Exception:
        pass

    s = s.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    items = re.findall(r'(["\'])(.*?)(?<!\\)\1', s)
    if items:
        return " ".join(clean_surrogates(t) for _, t in items)

    parts = [p.strip().strip('"').strip("'") for p in s.split(',') if p.strip()]
    return " ".join(clean_surrogates(p) for p in parts)


def tokenize(text: str) -> List[str]:
    if text is None:
        return []
    
    # Final safety sweep for tokenization strings
    text = clean_surrogates(text).lower()
    tokens = re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)
    return tokens


def compute_f1_from_csv(path: str, gt_col: str = "predicted_sentenceAnswer", pred_col: str = "predicted_sentence", output_excel: str | None = None) -> dict:
    if path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        df = pd.read_csv(path)

    if pred_col not in df.columns:
        raise ValueError(
            f"Prediction column '{pred_col}' not found in CSV. Available columns: {', '.join(df.columns)}"
        )

    if gt_col not in df.columns:
        fallback_candidates = [
            "Processed Comments",
            "predicted_sentenceAnswer",
            "Processed_Comments",
            "predicted_sentence",
            "gold",
            "ground_truth",
            "target",
        ]
        fallback = next((c for c in fallback_candidates if c in df.columns and c != pred_col), None)
        if fallback is not None:
            print(
                f"Warning: ground-truth column '{gt_col}' not found. Using '{fallback}' instead."
            )
            gt_col = fallback
        else:
            raise ValueError(
                f"Ground-truth column '{gt_col}' not found in CSV. Available columns: {', '.join(df.columns)}"
            )

    TP = FP = FN = 0
    per_sample_f1 = []
    details = []

    for idx, row in df.iterrows():
        # Ensure raw inputs are treated as strings and cleaned up front
        gt_raw = clean_surrogates(str(row.get(gt_col, ""))) if pd.notna(row.get(gt_col)) else ""
        pred_raw = clean_surrogates(str(row.get(pred_col, ""))) if pd.notna(row.get(pred_col)) else ""

        gt_text = parse_list_like(gt_raw)
        pred_text = parse_list_like(pred_raw)

        gt_tokens = set(tokenize(gt_text))
        pred_tokens = set(tokenize(pred_text))

        tp = len(pred_tokens & gt_tokens)
        fp = len(pred_tokens - gt_tokens)
        fn = len(gt_tokens - pred_tokens)

        TP += tp
        FP += fp
        FN += fn

        if tp + fp == 0 and tp + fn == 0:
            prec = rec = f1 = 1.0
        else:
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0

        per_sample_f1.append(f1)
        details.append({
            "row_index": idx,
            "gt_text": gt_text,
            "pred_text": pred_text,
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": prec,
            "recall": rec,
            "f1": f1,
        })

    micro_prec = TP / (TP + FP) if (TP + FP) > 0 else 0.0
    micro_rec = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    micro_f1 = 2 * micro_prec * micro_rec / (micro_prec + micro_rec) if (micro_prec + micro_rec) > 0 else 0.0
    macro_f1 = sum(per_sample_f1) / len(per_sample_f1) if per_sample_f1 else 0.0

    metrics = {
        "rows": len(df),
        "TP": TP,
        "FP": FP,
        "FN": FN,
        "micro_precision": micro_prec,
        "micro_recall": micro_rec,
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
    }

    print(f"Rows: {metrics['rows']}")
    print(f"TP: {metrics['TP']}, FP: {metrics['FP']}, FN: {metrics['FN']}")
    print(f"Micro Precision: {metrics['micro_precision']:.4f}")
    print(f"Micro Recall:    {metrics['micro_recall']:.4f}")
    print(f"Micro F1:        {metrics['micro_f1']:.4f}")
    print(f"Macro (avg) F1:  {metrics['macro_f1']:.4f}")

    if output_excel:
        write_scores_to_excel(metrics, details, output_excel)

    return metrics


def write_scores_to_excel(metrics: dict, details: list[dict], output_path: str) -> None:
    metrics_df = pd.DataFrame([
        {"metric": "Rows", "value": metrics["rows"]},
        {"metric": "TP", "value": metrics["TP"]},
        {"metric": "FP", "value": metrics["FP"]},
        {"metric": "FN", "value": metrics["FN"]},
        {"metric": "Micro Precision", "value": metrics["micro_precision"]},
        {"metric": "Micro Recall", "value": metrics["micro_recall"]},
        {"metric": "Micro F1", "value": metrics["micro_f1"]},
        {"metric": "Macro (avg) F1", "value": metrics["macro_f1"]},
    ])
    details_df = pd.DataFrame(details)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        metrics_df.to_excel(writer, sheet_name="summary", index=False)
        details_df.to_excel(writer, sheet_name="details", index=False)

    print(f"Wrote Excel output to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Compute F1 from predictions CSV or Excel file")
    parser.add_argument("csv", nargs="?", default="predictions.csv", help="path to CSV or Excel file")
    parser.add_argument("--gt", default="predicted_sentenceAnswer", help="ground-truth column name")
    parser.add_argument("--pred", default="predicted_sentence", help="prediction column name")
    parser.add_argument("--output", default="f1_scores.xlsx", help="Excel output file path")
    args = parser.parse_args()

    compute_f1_from_csv(args.csv, gt_col=args.gt, pred_col=args.pred, output_excel=args.output)


if __name__ == "__main__":
    main()