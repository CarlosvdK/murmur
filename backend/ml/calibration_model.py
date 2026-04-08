"""
Multi-Model Calibration System

Compares multiple ML models to find which best predicts simulation
accuracy from survey features. The winning model tells us which
survey questions matter most (feature importance) so we can adjust
accuracy weights in survey_schema.yaml.

Models tested:
- Random Forest
- XGBoost
- CatBoost
- LightGBM
- Logistic Regression
- Gradient Boosting (sklearn)

All models use the same features from FeatureExtractor
(which reads survey_schema.yaml). Adding a field with
ml.include=true automatically adds it to all models.

Usage:
    from backend.ml.calibration_model import ModelArena
    arena = ModelArena()
    arena.train(training_data)
    results = arena.compare()  # returns ranked model performance
    best = arena.best_model()
    importance = arena.feature_importance()
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

MODEL_DIR = Path(__file__).parent / "saved_models"
MODEL_DIR.mkdir(exist_ok=True)


@dataclass
class ModelResult:
    name: str
    accuracy: float
    f1: float
    auc: Optional[float]
    cv_mean: float
    cv_std: float
    feature_importances: Optional[dict]


class ModelArena:
    """Trains and compares multiple ML models on the same data."""

    def __init__(self):
        self._models = {}
        self._results: list[ModelResult] = []
        self._best_name: Optional[str] = None
        self._feature_names: list[str] = []
        self._scaler = StandardScaler()
        self._trained = False

    def _build_models(self) -> dict:
        """Creates all candidate models."""
        models = {
            "random_forest": RandomForestClassifier(
                n_estimators=100, max_depth=8, min_samples_leaf=3,
                random_state=42, n_jobs=-1,
            ),
            "gradient_boosting": GradientBoostingClassifier(
                n_estimators=100, max_depth=5, learning_rate=0.1,
                min_samples_leaf=3, random_state=42,
            ),
            "logistic_regression": LogisticRegression(
                max_iter=1000, random_state=42, C=1.0,
            ),
        }

        # Optional: XGBoost
        try:
            from xgboost import XGBClassifier
            models["xgboost"] = XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                min_child_weight=3, random_state=42,
                use_label_encoder=False, eval_metric="logloss",
                verbosity=0,
            )
        except ImportError:
            logger.info("XGBoost not available, skipping")

        # Optional: LightGBM
        try:
            from lightgbm import LGBMClassifier
            models["lightgbm"] = LGBMClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                min_child_samples=3, random_state=42,
                verbose=-1,
            )
        except ImportError:
            logger.info("LightGBM not available, skipping")

        # Optional: CatBoost
        try:
            from catboost import CatBoostClassifier
            models["catboost"] = CatBoostClassifier(
                iterations=100, depth=6, learning_rate=0.1,
                random_state=42, verbose=0,
            )
        except ImportError:
            logger.info("CatBoost not available, skipping")

        return models

    def train(self, X: np.ndarray, y: np.ndarray, feature_names: list[str]):
        """Train all models and compare.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Binary target (1 = prediction was correct, 0 = incorrect)
            feature_names: List of feature names matching X columns
        """
        self._feature_names = feature_names
        self._models = self._build_models()
        self._results = []

        # Scale features for logistic regression
        X_scaled = self._scaler.fit_transform(X)

        n_splits = min(5, max(2, len(y) // 5))
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

        for name, model in self._models.items():
            try:
                # Use scaled data for logistic regression, raw for tree models
                X_use = X_scaled if name == "logistic_regression" else X

                # Cross-validation
                cv_scores = cross_val_score(model, X_use, y, cv=cv, scoring="accuracy")

                # Full fit for feature importance
                model.fit(X_use, y)
                y_pred = model.predict(X_use)

                # Metrics
                acc = accuracy_score(y, y_pred)
                f1 = f1_score(y, y_pred, zero_division=0)

                auc = None
                if hasattr(model, "predict_proba"):
                    try:
                        y_proba = model.predict_proba(X_use)[:, 1]
                        auc = roc_auc_score(y, y_proba)
                    except Exception:
                        pass

                # Feature importances
                importances = None
                if hasattr(model, "feature_importances_"):
                    importances = dict(zip(feature_names, model.feature_importances_.tolist()))
                elif hasattr(model, "coef_"):
                    importances = dict(zip(feature_names, np.abs(model.coef_[0]).tolist()))

                result = ModelResult(
                    name=name, accuracy=acc, f1=f1, auc=auc,
                    cv_mean=float(cv_scores.mean()),
                    cv_std=float(cv_scores.std()),
                    feature_importances=importances,
                )
                self._results.append(result)
                logger.info(
                    "%s: accuracy=%.3f, f1=%.3f, cv=%.3f+/-%.3f",
                    name, acc, f1, cv_scores.mean(), cv_scores.std(),
                )

            except Exception as e:
                logger.error("Model %s failed: %s", name, e)

        # Sort by CV score
        self._results.sort(key=lambda r: r.cv_mean, reverse=True)
        if self._results:
            self._best_name = self._results[0].name

        self._trained = True

    def compare(self) -> list[dict]:
        """Returns ranked comparison of all models."""
        return [
            {
                "rank": i + 1,
                "model": r.name,
                "cv_accuracy": round(r.cv_mean, 4),
                "cv_std": round(r.cv_std, 4),
                "train_accuracy": round(r.accuracy, 4),
                "f1_score": round(r.f1, 4),
                "auc": round(r.auc, 4) if r.auc else None,
            }
            for i, r in enumerate(self._results)
        ]

    def best_model(self) -> Optional[str]:
        """Returns name of the best-performing model."""
        return self._best_name

    def feature_importance(self, model_name: str = None) -> dict:
        """Returns feature importances from the specified model (or best).

        This is what tells us which survey questions matter most.
        Higher importance = more weight in survey_schema.yaml accuracy scores.
        """
        name = model_name or self._best_name
        if not name:
            return {}

        for r in self._results:
            if r.name == name and r.feature_importances:
                # Sort by importance descending
                sorted_imp = dict(
                    sorted(r.feature_importances.items(),
                           key=lambda x: x[1], reverse=True)
                )
                return sorted_imp
        return {}

    def predict(self, X: np.ndarray, model_name: str = None) -> np.ndarray:
        """Predict using the specified model (or best)."""
        name = model_name or self._best_name
        if not name or name not in self._models:
            raise ValueError(f"Model {name} not found")
        model = self._models[name]
        X_use = self._scaler.transform(X) if name == "logistic_regression" else X
        return model.predict(X_use)

    def predict_proba(self, X: np.ndarray, model_name: str = None) -> np.ndarray:
        """Predict probabilities using the specified model (or best)."""
        name = model_name or self._best_name
        if not name or name not in self._models:
            raise ValueError(f"Model {name} not found")
        model = self._models[name]
        X_use = self._scaler.transform(X) if name == "logistic_regression" else X
        return model.predict_proba(X_use)

    def save(self, path: str = None):
        """Save all trained models and results."""
        save_path = Path(path) if path else MODEL_DIR / "arena.pkl"
        data = {
            "models": self._models,
            "results": self._results,
            "best_name": self._best_name,
            "feature_names": self._feature_names,
            "scaler": self._scaler,
        }
        with open(save_path, "wb") as f:
            pickle.dump(data, f)
        logger.info("Saved model arena to %s", save_path)

    def load(self, path: str = None):
        """Load previously trained models."""
        load_path = Path(path) if path else MODEL_DIR / "arena.pkl"
        if not load_path.exists():
            raise FileNotFoundError(f"No saved model at {load_path}")
        with open(load_path, "rb") as f:
            data = pickle.load(f)
        self._models = data["models"]
        self._results = data["results"]
        self._best_name = data["best_name"]
        self._feature_names = data["feature_names"]
        self._scaler = data["scaler"]
        self._trained = True
        logger.info("Loaded model arena from %s", load_path)

    def report(self) -> str:
        """Human-readable report of model comparison."""
        lines = [
            "=" * 60,
            "MODEL COMPARISON REPORT",
            "=" * 60,
            "",
            f"{'Rank':<5} {'Model':<22} {'CV Acc':<10} {'F1':<8} {'AUC':<8}",
            "-" * 60,
        ]
        for i, r in enumerate(self._results):
            auc_str = f"{r.auc:.3f}" if r.auc else "N/A"
            lines.append(
                f"{i+1:<5} {r.name:<22} {r.cv_mean:.3f}+/-{r.cv_std:.3f}  "
                f"{r.f1:.3f}   {auc_str}"
            )

        lines.extend(["", f"Best model: {self._best_name}", ""])

        if self._best_name:
            imp = self.feature_importance()
            if imp:
                lines.append("TOP 10 FEATURE IMPORTANCES (best model):")
                lines.append("-" * 40)
                for i, (feat, score) in enumerate(list(imp.items())[:10]):
                    bar = "#" * int(score * 50)
                    lines.append(f"  {feat:<30} {score:.4f} {bar}")

        lines.append("=" * 60)
        return "\n".join(lines)
