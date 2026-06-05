"""
Divide el dataset organizado por clase en train / val / test.

Uso:
    python split_dataset.py [--raw raw] [--out processed] [--train 0.7] [--val 0.15]

Salida:
    dataset/processed/
        train/unripe/  train/breaking/  ...
        val/unripe/    val/breaking/    ...
        test/unripe/   test/breaking/   ...
"""

import argparse
import random
import shutil
from pathlib import Path


CLASSES = ["unripe", "breaking", "ripe_first", "ripe_second", "overripe"]


def split_class(class_dir: Path, out_dir: Path, train_r: float, val_r: float, seed: int):
    images = sorted(class_dir.glob("*.jpg"))
    random.seed(seed)
    random.shuffle(images)

    n = len(images)
    n_train = int(n * train_r)
    n_val = int(n * val_r)

    splits = {
        "train": images[:n_train],
        "val":   images[n_train:n_train + n_val],
        "test":  images[n_train + n_val:],
    }

    counts = {}
    for split_name, split_images in splits.items():
        dest = out_dir / split_name / class_dir.name
        dest.mkdir(parents=True, exist_ok=True)
        for img in split_images:
            shutil.copy2(img, dest / img.name)
        counts[split_name] = len(split_images)

    return counts


def main():
    parser = argparse.ArgumentParser(description="Split dataset en train/val/test estratificado")
    parser.add_argument("--raw",   default="raw",       help="Carpeta con imágenes organizadas por clase")
    parser.add_argument("--out",   default="processed", help="Carpeta de salida")
    parser.add_argument("--train", type=float, default=0.70, help="Fracción train (default: 0.70)")
    parser.add_argument("--val",   type=float, default=0.15, help="Fracción val (default: 0.15)")
    parser.add_argument("--seed",  type=int,   default=42,   help="Semilla aleatoria (default: 42)")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    raw_dir = script_dir / args.raw
    out_dir = script_dir / args.out

    if not raw_dir.exists():
        raise FileNotFoundError(f"Carpeta raw no encontrada: {raw_dir}\nEjecuta primero: python prepare_dataset.py")

    test_r = 1.0 - args.train - args.val
    print(f"=== Split dataset ===")
    print(f"Train: {args.train*100:.0f}%  Val: {args.val*100:.0f}%  Test: {test_r*100:.0f}%\n")

    total = {"train": 0, "val": 0, "test": 0}

    print(f"{'Clase':15s} {'Train':>7} {'Val':>7} {'Test':>7} {'Total':>7}")
    print("-" * 45)

    for cls in CLASSES:
        class_dir = raw_dir / cls
        if not class_dir.exists():
            print(f"  {cls}: carpeta no encontrada, saltando")
            continue

        counts = split_class(class_dir, out_dir, args.train, args.val, args.seed)
        row_total = sum(counts.values())
        print(f"{cls:15s} {counts['train']:>7} {counts['val']:>7} {counts['test']:>7} {row_total:>7}")

        for k in total:
            total[k] += counts[k]

    print("-" * 45)
    grand = sum(total.values())
    print(f"{'TOTAL':15s} {total['train']:>7} {total['val']:>7} {total['test']:>7} {grand:>7}")

    print(f"\nDataset procesado en: {out_dir}")
    print("Siguiente paso: subir a Google Colab y ejecutar el notebook de entrenamiento")


if __name__ == "__main__":
    main()
