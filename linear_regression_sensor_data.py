"""
Ajusta un modelo de regresión lineal con scikit-learn para predecir si conviene
regar (`regar` / `no regar`) según las lecturas de los sensores.

El modelo utiliza cinco características por defecto:
    - uv_index
    - temperature2
    - humidity2
    - soil_moisture1
    - soil_moisture2

La columna objetivo (`prediccion`) se puede proporcionar en el CSV o generar
automáticamente aplicando la misma regla que en `tagging_watering_prediction.py`.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List, Sequence

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

DEFAULT_FEATURES: Sequence[str] = (
    "uv_index",
    "temperature2",
    "humidity2",
    "soil_moisture1",
    "soil_moisture2",
)
PREDICTION_COLUMN = "prediccion"
LABEL_MAP = {"No regar": 0.0, "Regar": 1.0}
REVERSE_LABEL_MAP = {0.0: "No regar", 1.0: "Regar"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Optimiza una regresión lineal con scikit-learn para predecir "
            "acciones de riego basadas en lecturas de sensores."
        )
    )
    parser.add_argument(
        "--csv-path",
        type=Path,
        default=Path("sensor_data_rows.csv"),
        help="Ruta al archivo CSV con los datos del sensor (default: sensor_data_rows.csv).",
    )
    parser.add_argument(
        "--features",
        nargs="+",
        default=list(DEFAULT_FEATURES),
        help=(
            "Columnas a utilizar como características numéricas. "
            f"Default: {', '.join(DEFAULT_FEATURES)}."
        ),
    )
    parser.add_argument(
        "--prediction-column",
        default=PREDICTION_COLUMN,
        help="Nombre de la columna con etiquetas `Regar`/`No regar` (default: prediccion).",
    )
    parser.add_argument(
        "--generate-labels",
        action="store_true",
        help=(
            "Genera la columna de etiquetas siguiendo la regla: marca `Regar` "
            "en la fila previa a cuando soil_moisture1 o soil_moisture2 valen 100."
        ),
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proporción de datos reservados para prueba (default: 0.2).",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Semilla aleatoria para la partición train/test (default: 42).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Umbral para convertir la predicción continua en `Regar`/`No regar` (default: 0.5).",
    )
    parser.add_argument(
        "--save-predictions",
        type=Path,
        default=None,
        help=(
            "Archivo donde guardar las predicciones del conjunto completo, "
            "incluyendo la etiqueta estimada y la puntuación continua."
        ),
    )
    return parser.parse_args()


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo CSV en {csv_path!s}")

    return pd.read_csv(csv_path)


def ensure_labels(df: pd.DataFrame, label_column: str) -> pd.DataFrame:
    if label_column in df.columns and df[label_column].notna().any():
        # Normalize existing labels to "Regar" or "No regar"
        df_copy = df.copy()
        df_copy[label_column] = df_copy[label_column].str.strip().str.capitalize()
        df_copy[label_column] = df_copy[label_column].replace({
            "Regar": "Regar",
            "No regar": "No regar",
            "regar": "Regar",
            "no regar": "No regar"
        })
        return df_copy

    df_copy = df.copy()
    df_copy[label_column] = "No regar"

    soil_cols = ["soil_moisture1", "soil_moisture2"]
    for idx in range(1, len(df_copy)):
        if any(_is_moisture_hundred(df_copy.iloc[idx].get(col)) for col in soil_cols):
            df_copy.at[idx - 1, label_column] = "Regar"

    return df_copy


def _is_moisture_hundred(value: object) -> bool:
    if pd.isna(value):
        return False
    try:
        return float(value) == 100.0
    except (TypeError, ValueError):
        return False


def validate_features(df: pd.DataFrame, features: Iterable[str]) -> List[str]:
    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(
            "Las siguientes columnas de características no existen en el dataset: "
            + ", ".join(missing)
        )
    return list(features)


def prepare_training_data(
    df: pd.DataFrame, features: List[str], label_column: str
) -> tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    subset = df[features + [label_column]].dropna()
    if subset.empty:
        raise ValueError("No quedan filas después de eliminar NaN en características/etiquetas.")

    # Normalize labels to "Regar" or "No regar"
    subset = subset.copy()
    subset[label_column] = subset[label_column].str.strip().str.capitalize()
    subset[label_column] = subset[label_column].replace({
        "Regar": "Regar",
        "No regar": "No regar",
        "regar": "Regar",
        "no regar": "No regar"
    })
    
    y = subset[label_column].map(LABEL_MAP)
    missing_labels = y.isna()
    if missing_labels.any():
        invalid_values = subset.loc[missing_labels, label_column].unique()
        raise ValueError(
            "Se encontraron etiquetas fuera de `Regar`/`No regar`: "
            + ", ".join(map(str, invalid_values))
        )

    if y.nunique() < 2:
        raise ValueError(
            "Se requiere al menos dos clases (`Regar` y `No regar`) para entrenar el modelo."
        )

    X = subset[features].to_numpy(dtype=float)
    return X, y.to_numpy(dtype=float), subset


def build_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression()),
        ]
    )


def main() -> None:
    args = parse_args()

    try:
        df = load_dataset(args.csv_path)
        if args.generate_labels or args.prediction_column not in df.columns:
            df = ensure_labels(df, args.prediction_column)

        features = validate_features(df, args.features)
        X, y, subset = prepare_training_data(df, features, args.prediction_column)

        stratify = y if len(np.unique(y)) > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=args.test_size,
            random_state=args.random_state,
            stratify=stratify,
        )

        model = build_pipeline()
        model.fit(X_train, y_train)

        y_pred_cont = model.predict(X_test)
        y_pred_label = (y_pred_cont >= args.threshold).astype(float)

        mse = mean_squared_error(y_test, y_pred_cont)
        r2 = r2_score(y_test, y_pred_cont)
        accuracy = accuracy_score(y_test, y_pred_label)

        regressor = model.named_steps["regressor"]
        coefficients = regressor.coef_
        intercept = float(regressor.intercept_)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("=== Modelo de regresión lineal (scikit-learn) ===")
    print(f"Características utilizadas: {', '.join(features)}")
    print(f"Tamaño train/test: {len(X_train)} / {len(X_test)}")
    print(f"Intercepto: {intercept:.4f}")
    for feature, coef in zip(features, coefficients, strict=False):
        print(f"Coeficiente para {feature}: {coef:.4f}")
    print("--- Métricas ---")
    print(f"MSE: {mse:.4f}")
    print(f"R²: {r2:.4f}")
    print(f"Exactitud (umbral {args.threshold}): {accuracy:.4f}")
    print("--- Resultado ---")
    
    # Mostrar predicción para el último dato
    if len(X_test) > 0:
        last_prediction = model.predict(X_test[-1:].reshape(1, -1))[0]
        resultado = REVERSE_LABEL_MAP[1.0] if last_prediction >= args.threshold else REVERSE_LABEL_MAP[0.0]
        print(f"Predicción final: {resultado}")
        print(f"Score continuo: {last_prediction:.4f}")

    if args.save_predictions:
        predictions_df = subset.copy()
        predictions_df["score_continuo"] = model.predict(X)
        predictions_df[PREDICTION_COLUMN + "_estimada"] = np.where(
            predictions_df["score_continuo"] >= args.threshold, "Regar", "No regar"
        )
        predictions_df.to_csv(args.save_predictions, index=False)
        print(f"Predicciones guardadas en: {args.save_predictions}")
        print(f"Resultado: {predictions_df[PREDICTION_COLUMN + '_estimada'].iloc[-1]}")


if __name__ == "__main__":
    main()

