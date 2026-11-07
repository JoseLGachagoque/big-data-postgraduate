#!/usr/bin/env bash
# Ejecuta el pipeline completo en orden: bronze -> silver -> gold -> análisis -> mapas -> pruebas.
# Se detiene en el primer notebook que falle (set -e). Uso:  ./run_pipeline.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p outputs/logs
for nb in notebooks/0*.ipynb; do
  echo ">> $(date +%H:%M:%S) $nb"
  jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=1200 "$nb" 2>&1 | tee -a outputs/logs/pipeline.log
done
echo ">> pruebas"
python -m pytest -q tests | tee -a outputs/logs/pipeline.log
echo ">> listo: revise outputs/quality, outputs/stats, outputs/figures y outputs/maps"
