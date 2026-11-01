"""
backend/app/optimizers/clustering.py
Geographic and demand-weighted spatial clustering for retail stores and logistics assets.
Implements K-Means++ with demand weighting to partition stores into optimal delivery zones.
"""

from typing import Dict, List, Tuple
import numpy as np
from pydantic import BaseModel, Field


class ClusterSummary(BaseModel):
    cluster_id: int
    center_lat: float
    center_lon: float
    store_ids: List[str]
    total_demand_weight: float
    bounding_box: Tuple[float, float, float, float]  # min_lat, min_lon, max_lat, max_lon


class DemandWeightedKMeans:
    """Partitions stores into K geographic clusters weighted by demand density."""

    def __init__(self, n_clusters: int = 3, max_iter: int = 100, tol: float = 1e-4, seed: int = 42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.seed = seed
        self.centroids: np.ndarray = np.empty((0, 2))
        self.rng = np.random.default_rng(seed)

    def fit_predict(
        self,
        store_ids: List[str],
        coordinates: np.ndarray,      # Shape (N, 2) [lat, lon]
        demand_weights: np.ndarray,    # Shape (N,)
    ) -> Dict[int, List[str]]:
        """
        Executes K-Means++ initialization and demand-weighted centroid updates.
        Returns mapping: cluster_id -> list of store_ids.
        """
        n_points = len(coordinates)
        if n_points == 0:
            return {}

        k = min(self.n_clusters, n_points)
        weights = np.maximum(demand_weights, 1.0)
        norm_weights = weights / np.sum(weights)

        # 1. K-Means++ Initialization
        centroids = [coordinates[self.rng.choice(n_points, p=norm_weights)]]
        for _ in range(1, k):
            # Compute squared distances to nearest existing centroid
            dists = np.min(
                np.linalg.norm(coordinates[:, np.newaxis] - np.array(centroids), axis=2) ** 2,
                axis=1,
            )
            prob = dists * norm_weights
            prob_sum = np.sum(prob)
            if prob_sum > 0:
                prob /= prob_sum
                next_centroid = coordinates[self.rng.choice(n_points, p=prob)]
            else:
                next_centroid = coordinates[self.rng.integers(0, n_points)]
            centroids.append(next_centroid)

        self.centroids = np.array(centroids)

        # 2. Lloyd's Algorithm with Demand-Weighted Means
        assignments = np.zeros(n_points, dtype=int)
        for _ in range(self.max_iter):
            # Distance from each store to all centroids: shape (N, K)
            diffs = coordinates[:, np.newaxis, :] - self.centroids[np.newaxis, :, :]
            dists = np.sum(diffs ** 2, axis=2)
            new_assignments = np.argmin(dists, axis=1)

            # Check convergence
            if np.array_equal(new_assignments, assignments):
                break
            assignments = new_assignments

            # Update centroids with demand weighting
            new_centroids = np.copy(self.centroids)
            for c_idx in range(k):
                mask = assignments == c_idx
                if np.any(mask):
                    cluster_weights = weights[mask]
                    w_sum = np.sum(cluster_weights)
                    new_centroids[c_idx] = np.sum(
                        coordinates[mask] * cluster_weights[:, np.newaxis], axis=0
                    ) / w_sum

            shift = np.max(np.linalg.norm(new_centroids - self.centroids, axis=1))
            self.centroids = new_centroids
            if shift < self.tol:
                break

        # Group store_ids by cluster
        result: Dict[int, List[str]] = {i: [] for i in range(k)}
        for store_id, cluster_idx in zip(store_ids, assignments):
            result[cluster_idx].append(store_id)

        return result

    def get_cluster_summaries(
        self,
        clusters: Dict[int, List[str]],
        store_coord_map: Dict[str, Tuple[float, float]],
        store_demand_map: Dict[str, float],
    ) -> List[ClusterSummary]:
        """Calculates geographic centroids, bounding boxes, and aggregate cluster demand."""
        summaries = []
        for c_id, stores in clusters.items():
            if not stores:
                continue
            coords = np.array([store_coord_map[s] for s in stores])
            demands = [store_demand_map.get(s, 10.0) for s in stores]
            min_lat, min_lon = np.min(coords, axis=0)
            max_lat, max_lon = np.max(coords, axis=0)
            center_lat, center_lon = self.centroids[c_id] if c_id < len(self.centroids) else np.mean(coords, axis=0)

            summaries.append(
                ClusterSummary(
                    cluster_id=c_id,
                    center_lat=round(float(center_lat), 4),
                    center_lon=round(float(center_lon), 4),
                    store_ids=stores,
                    total_demand_weight=round(float(sum(demands)), 1),
                    bounding_box=(
                        round(float(min_lat), 4),
                        round(float(min_lon), 4),
                        round(float(max_lat), 4),
                        round(float(max_lon), 4),
                    ),
                )
            )
        return summaries
