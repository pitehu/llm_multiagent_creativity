#!/usr/bin/env python3
"""Compute semantic trajectory metrics from turn-level embedding parquet files.

The paper-facing notebooks consume pre-computed CSVs in ``data/``.
Use this script only when regenerating those CSVs from turn-level embeddings.
The expected parquet input contains one row per conversation turn with:
``file_id``, ``question_id``, and ``embedding`` columns.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.spatial.distance import cosine, pdist
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from tqdm import tqdm


class TrajectoryAnalyzer:
    """Compute trajectory metrics for one ordered sequence of embeddings."""

    def __init__(self, embeddings: np.ndarray):
        self.embeddings = np.asarray(embeddings)
        self.n = len(embeddings)

    def mean_pairwise_distance(self) -> float:
        if self.n < 2:
            return np.nan
        return float(np.mean(pdist(self.embeddings, metric="cosine")))

    def local_coherence(self) -> float:
        if self.n < 2:
            return np.nan
        values = [
            1 - cosine(self.embeddings[i], self.embeddings[i + 1])
            for i in range(self.n - 1)
        ]
        return float(np.mean(values))

    def convergence_ratio(self) -> float:
        if self.n < 4:
            return np.nan
        mid = self.n // 2
        early_div = np.mean(pdist(self.embeddings[:mid], metric="cosine"))
        late_div = np.mean(pdist(self.embeddings[mid:], metric="cosine"))
        return float((early_div - late_div) / early_div) if early_div > 0 else 0.0

    def path_length(self) -> float:
        if self.n < 2:
            return 0.0
        return float(
            sum(
                cosine(self.embeddings[i], self.embeddings[i + 1])
                for i in range(self.n - 1)
            )
        )

    def effective_dimensions(self, variance_threshold: float = 0.90) -> int:
        if self.n < 2:
            return 0
        try:
            pca = PCA()
            pca.fit(self.embeddings)
            return int(
                np.argmax(np.cumsum(pca.explained_variance_ratio_) >= variance_threshold)
                + 1
            )
        except Exception:
            return 0

    def cluster_dispersion(self, n_clusters: int = 3) -> float:
        if self.n < n_clusters * 2:
            return np.nan
        try:
            labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(
                self.embeddings
            )
            intra: list[float] = []
            inter: list[float] = []
            for cluster_id in range(n_clusters):
                points = self.embeddings[labels == cluster_id]
                if len(points) > 1:
                    intra.extend(pdist(points, metric="cosine"))
            for left in range(n_clusters):
                for right in range(left + 1, n_clusters):
                    for p1 in self.embeddings[labels == left]:
                        for p2 in self.embeddings[labels == right]:
                            inter.append(cosine(p1, p2))
            return float(np.mean(inter) / np.mean(intra)) if intra and inter else np.nan
        except Exception:
            return np.nan

    def max_pairwise_distance(self) -> float:
        if self.n < 2:
            return np.nan
        return float(np.max(pdist(self.embeddings, metric="cosine")))

    def semantic_velocity(self) -> float:
        if self.n < 2:
            return 0.0
        return self.path_length() / (self.n - 1)

    def trajectory_curvature(self) -> float:
        if self.n < 3:
            return np.nan
        curvatures = []
        for i in range(self.n - 2):
            d1 = self.embeddings[i + 1] - self.embeddings[i]
            d2 = self.embeddings[i + 2] - self.embeddings[i + 1]
            n1 = np.linalg.norm(d1)
            n2 = np.linalg.norm(d2)
            if n1 > 1e-10 and n2 > 1e-10:
                curvatures.append(np.arccos(np.clip(np.dot(d1 / n1, d2 / n2), -1, 1)))
        return float(np.mean(curvatures)) if curvatures else np.nan

    def topic_switching_rate(self, n_clusters: int = 3) -> float:
        if self.n < n_clusters + 1:
            return np.nan
        try:
            labels = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit_predict(
                self.embeddings
            )
            switches = sum(labels[i] != labels[i + 1] for i in range(len(labels) - 1))
            return float(switches / (len(labels) - 1))
        except Exception:
            return np.nan

    def global_coherence(self) -> float:
        if self.n < 2:
            return np.nan
        centroid = np.mean(self.embeddings, axis=0)
        return float(np.mean([1 - cosine(embedding, centroid) for embedding in self.embeddings]))

    def revisit_score(self, early_frac: float = 0.3, late_frac: float = 0.3) -> float:
        if self.n < 6:
            return np.nan
        early_n = int(self.n * early_frac)
        late_n = int(self.n * late_frac)
        return float(
            max(
                1 - cosine(late, early)
                for late in self.embeddings[-late_n:]
                for early in self.embeddings[:early_n]
            )
        )

    def semantic_spread(self) -> float:
        if self.n < 2:
            return np.nan
        centroid = np.mean(self.embeddings, axis=0)
        return float(np.std([np.linalg.norm(embedding - centroid) for embedding in self.embeddings]))

    def compute_all_metrics(self) -> dict[str, float]:
        return {
            "mean_distance": self.mean_pairwise_distance(),
            "local_coherence": self.local_coherence(),
            "convergence_ratio": self.convergence_ratio(),
            "path_length": self.path_length(),
            "effective_dims": self.effective_dimensions(),
            "cluster_dispersion": self.cluster_dispersion(),
            "max_distance": self.max_pairwise_distance(),
            "semantic_velocity": self.semantic_velocity(),
            "trajectory_curvature": self.trajectory_curvature(),
            "topic_switching_rate": self.topic_switching_rate(),
            "global_coherence": self.global_coherence(),
            "revisit_score": self.revisit_score(),
            "semantic_spread": self.semantic_spread(),
        }


def process_one(file_id: str, question_id: str, embeddings: np.ndarray) -> dict[str, object]:
    metrics = TrajectoryAnalyzer(embeddings).compute_all_metrics()
    metrics["file_id"] = file_id
    metrics["question_id"] = question_id
    metrics["n_turns"] = len(embeddings)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--turn-embeddings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--jobs", type=int, default=max(1, min(14, (os.cpu_count() or 2) - 2)))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    turns = pd.read_parquet(args.turn_embeddings)
    required = {"file_id", "question_id", "embedding"}
    missing = required.difference(turns.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    turns["question_id"] = turns["question_id"].astype(str)
    turns["embedding"] = turns["embedding"].apply(lambda value: np.asarray(value))

    conversations = [
        (file_id, question_id, np.stack(group["embedding"].values))
        for (file_id, question_id), group in turns.groupby(["file_id", "question_id"], sort=False)
    ]

    results = Parallel(n_jobs=args.jobs)(
        delayed(process_one)(file_id, question_id, embeddings)
        for file_id, question_id, embeddings in tqdm(conversations, desc="Conversations")
    )

    output = pd.DataFrame(results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(f"Wrote {len(output):,} rows to {args.output}")


if __name__ == "__main__":
    main()
