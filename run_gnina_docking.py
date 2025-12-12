import os
import argparse
import subprocess
from docking_utils import prepare_receptor, prepare_ligand, get_structure_center, get_box_size, run_gnina, parse_gnina_log, split_gnina_poses_manual

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gnina_sif_path', type=str, required=True)
    parser.add_argument('--pdb_id', type=str, required=True)
    parser.add_argument('--lig_id', type=str, required=True)
    parser.add_argument('--prot_path', type=str, required=True)
    parser.add_argument('--lig_path', type=str, required=True)
    parser.add_argument('--pocket_path', type=str, required=True)
    parser.add_argument('--output_dir', type=str, required=True)
    parser.add_argument('-v', '--verbose', action='store_true')
    
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.verbose:
        print(f"[INFO] Starting docking for {args.pdb_id}...")

    receptor_pdbqt = prepare_receptor(args.prot_path, args.pdb_id)
    ligand_pdbqt = prepare_ligand(args.lig_path, args.lig_id)
    center = get_structure_center(args.pocket_path)
    box = get_box_size(args.lig_path)

    output_pdbqt = os.path.join(args.output_dir, f'{args.pdb_id}_{args.lig_id}.pdbqt')
    log_path = os.path.join(args.output_dir, f'{args.pdb_id}_{args.lig_id}.log')
    csv_path = os.path.join(args.output_dir, f'{args.pdb_id}_{args.lig_id}.csv')

    try:
        run_gnina(args.gnina_sif_path, receptor_pdbqt, ligand_pdbqt, center, box, output_pdbqt, log_path)
        parse_gnina_log(log_path, csv_path)
        split_gnina_poses_manual(output_pdbqt, args.output_dir, verbose=args.verbose)
    except subprocess.CalledProcessError as e:
        print(f'[ERROR] Docking failed for {args.pdb_id}: {e}')
