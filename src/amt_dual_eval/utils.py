"""Shared utilities: config loading and small helpers.

Configuration files are packaged under ``amt_dual_eval/configs`` and loaded with
``importlib.resources`` so they resolve correctly for normal installs (not only
when running from a source checkout).
"""
from __future__ import annotations

import functools
from importlib import resources
from typing import Any, Dict

import yaml

_CONFIG_PACKAGE = "amt_dual_eval.configs"


@functools.lru_cache(maxsize=None)
def load_config(name: str) -> Dict[str, Any]:
    """Load and cache a packaged YAML configuration file.

    Args:
        name: File name within the packaged config directory
            (e.g. ``"twed_default.yaml"``).

    Returns:
        Parsed YAML as a dict.
    """
    resource = resources.files(_CONFIG_PACKAGE).joinpath(name)
    if not resource.is_file():
        raise FileNotFoundError(f"Packaged config not found: {name}")
    with resource.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_text_config(name: str) -> str:
    """Load a packaged plain-text configuration file (e.g. a prompt template)."""
    resource = resources.files(_CONFIG_PACKAGE).joinpath(name)
    if not resource.is_file():
        raise FileNotFoundError(f"Packaged config not found: {name}")
    return resource.read_text(encoding="utf-8")


def feature_registry() -> Dict[str, Any]:
    """Return the parsed feature registry."""
    return load_config("feature_registry.yaml")


def top3(metric: str) -> list[str]:
    """Return the verified top-3 feature names for ``metric`` ('dtw' or 'twed')."""
    metric = metric.lower()
    reg = feature_registry()
    sets = reg.get("top3", {})
    if metric not in sets:
        raise ValueError(f"No top3 set defined for metric={metric!r}; have {list(sets)}")
    return list(sets[metric])


def supported_features() -> list[str]:
    """Return all feature names defined in the registry."""
    return list(feature_registry().get("features", {}).keys())
