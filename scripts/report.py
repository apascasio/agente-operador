"""Reporte de llamadas al LLM a partir de logs/llm_calls.jsonl.

Uso:
    uv run scripts/report.py [ruta/al/archivo.jsonl]
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

DEFAULT_PATH = Path("logs/llm_calls.jsonl")


def print_report(reporte: dict) -> None:
    """Imprime el reporte ya calculado."""
    ancho = 44
    print("=" * ancho)
    print("REPORTE DE LLAMADAS AL LLM".center(ancho))
    print("=" * ancho)
    print(f"Llamadas registradas:  {reporte['total']}")
    print(f"Costo total:           ${reporte['cost_usd']:.6f} USD")
    print(f"Latencia p50:          {reporte['p50']}")
    print(f"Latencia p95:          {reporte['p95']}")
    print(f"Fallback:              {reporte['fallback_pct']:.1f} %")
    print("-" * ancho)
    print("Llamadas por proveedor:")
    for provider, count in reporte["providers"].items():
        print(f"  {provider:<12} {count}")
    print("=" * ancho)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    path = Path(argv[0]) if argv else DEFAULT_PATH

    if not path.exists():
        print(f"No existe el archivo: {path}")
        return 0

    lines = path.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines if line.strip()]

    if not events:
        print(f"El archivo esta vacio: {path}")
        return 0

    # 1. Costo total en USD (los intentos fallidos registran 0.0)
    total_cost = sum(event["cost_usd"] for event in events)

    # 2. Latencia p50 y p95 (solo llamadas exitosas)
    successful = [event for event in events if event["success"]]
    latencies = sorted(event["latency_ms"] for event in successful)

    if len(latencies) >= 2:
        cuantiles = statistics.quantiles(latencies, n=100)
        p50 = f"{cuantiles[49]:.1f} ms"  # percentil 50
        p95 = f"{cuantiles[94]:.1f} ms"  # percentil 95
    else:
        p50 = p95 = "n/d"

    # 3. Porcentaje de llamadas con fallback
    fallback_count = sum(event["fallback"] for event in events)
    fallback_percentage = fallback_count / len(events) * 100

    # 4. Numero de llamadas por proveedor
    providers = Counter(event["provider"] for event in events)

    print_report(
        {
            "total": len(events),
            "cost_usd": total_cost,
            "p50": p50,
            "p95": p95,
            "fallback_pct": fallback_percentage,
            "providers": providers,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
