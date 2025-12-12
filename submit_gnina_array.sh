#!/bin/bash --login
#SBATCH --job-name=gnina_array
#SBATCH --time=6:00:00
#SBATCH --cpus-per-task=1
#SBATCH --gpus=1
#SBATCH --mem=2G
#SBATCH --array=0-46 # Adjust to match number of rows in docking_index.csv
#SBATCH --output=/mnt/scratch/jeaves/docking/gnina/logs/%x_%A_%a.out # Adjust path!
#SBATCH --error=/mnt/scratch/jeaves/docking/gnina/logs/%x_%A_%a.err # Adjust path!

set -euo pipefail

module load Miniforge3
conda activate gnina_docking

CSV_PATH="/mnt/research/woldring_lab/Members/Eaves/plip-plop/inputs/docking_index.csv" # Adjust path!
SIF_PATH="/mnt/research/woldring_lab/gnina_env/apps/gnina_1.3.1.sif" # Adjust path!

IFS=',' read -r pdb_id lig_id prot_path lig_path pocket_path output_dir < <(sed -n "$((SLURM_ARRAY_TASK_ID + 2))p" $CSV_PATH)

python3 run_gnina_docking.py \
    --gnina_sif_path "$SIF_PATH" \
    --pdb_id "$pdb_id" \
    --lig_id "$lig_id" \
    --prot_path "$prot_path" \
    --lig_path "$lig_path" \
    --pocket_path "$pocket_path" \
    --output_dir "$output_dir" \
    -v
