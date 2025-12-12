# GNINA-Docking-Pipeline

This repository was originally created to provide a reproducible pipeline for running GNINA v1.3.1 to generate docked protein-ligand poses for the CASF-2016 dataset using Singularity on the MSU High-Performance Computing Cluster (HPCC).  

## Directory Structure
```bash
inputs/  
|--docking_index.csv  #contains one row per docking job: pdb_id, lig_id, prot_path, lig_path, pocket_path, output_dir  
templates/  
|--input_dir_structure.txt #giude for input file locations  
|--output_dir_structure.txt #guide for output file locations  
run_gning_docking.py #CLI-compatible GNINA docking script  
submit_gnina_array.sh #SLURM submission script for GNINA docking via job array  
```

## Environment Setup  
Ensure GNINA 1.3.1 singularity image is installed.
```bash
module purge  
module load Miniforge3
conda create -n gnina_docking python=3.10 -y
conda activate gnina_docking
pip install openbabel==3.1.1 pandas tqdm
```

## Input Requirements
Each complex requires:
- A receptor `.pdb` file
- A ligand `.sdf` file
- A binding pocket `.pdb` file

The `inputs/docking_index.csv` must have columns:
```bash
pdb_id,lig_id,prot_path,lig_path,pocket_path,output_dir
```

## Running the Pipeline
```bash
sbatch submit_gnina_array.sh
```
Each job will 
1. Prepare receptor and ligand PDBQT files
2. Run GNINA docking via Singularity
3. Parse the log and split poses to individual SDFs


