import os
import subprocess
from openbabel import pybel
from rdkit import Chem
import pandas as pd

def prepare_receptor(protein_path, pdb_id):
    receptor_pdbqt = f"/tmp/{pdb_id}_receptor.pdbqt"
    subprocess.run([
        "obabel", protein_path, "-O", receptor_pdbqt,
        "--partialcharge", "gasteiger",
        "--gen3d", "-xh"
    ], check=True)
    return receptor_pdbqt

def prepare_ligand(ligand_path, lig_id):
    ligand_pdbqt = f"/tmp/{lig_id}_ligand.pdbqt"
    subprocess.run([
        "obabel", ligand_path, "-O", ligand_pdbqt,
        "--partialcharge", "gasteiger",
        "--gen3d", "-xh"
    ], check=True)
    return ligand_pdbqt

def get_structure_center(pocket_pdb):
    coords = []
    mol = next(pybel.readfile("pdb", pocket_pdb))
    for atom in mol:
        coords.append(atom.coords)
    center = tuple(sum(x)/len(coords) for x in zip(*coords))
    return center

def get_box_size(ligand_path, buffer=5.0):
    mol = Chem.SDMolSupplier(ligand_path, removeHs=False)[0]
    conformer = mol.GetConformer()
    coords = conformer.GetPositions()
    min_coords = coords.min(axis=0)
    max_coords = coords.max(axis=0)
    size = tuple(float((max_coords - min_coords)[i] + 2 * buffer) for i in range(3))
    return size

def run_gnina(sif_path, receptor_pdbqt, ligand_pdbqt, center, box_size, out_pdbqt, log_file):
    x, y, z = center
    sx, sy, sz = box_size

    subprocess.run([
        "singularity", "exec", sif_path, "gnina",
        "--receptor", receptor_pdbqt,
        "--ligand", ligand_pdbqt,
        "--center_x", str(x), "--center_y", str(y), "--center_z", str(z),
        "--size_x", str(sx), "--size_y", str(sy), "--size_z", str(sz),
        "--out", out_pdbqt,
        "--log", log_file,
        "--cpu", "1", "--num_modes", "100"
    ], check=True)

def parse_gnina_log(log_path, csv_out):
    with open(log_path) as f:
        lines = f.readlines()

    rows = []
    for line in lines:
        if line.startswith("mode"):
            continue
        if line.strip().startswith("1"):
            break

    for line in lines:
        if line.strip().startswith(""""""1"""):
            while line.strip():
                parts = line.split()
                rows.append({
                    'mode': int(parts[0]),
                    'score': float(parts[1]),
                    'cnn_score': float(parts[2]),
                    'cnn_affinity': float(parts[3])
                })
                line = next(f, '').strip()

    df = pd.DataFrame(rows)
    df.to_csv(csv_out, index=False)

def split_gnina_poses_manual(pdbqt_file, out_dir, verbose=False):
    with open(pdbqt_file, 'r') as f:
        contents = f.read()

    poses = contents.split("MODEL")
    for i, pose in enumerate(poses[1:], 1):
        pose_block = "MODEL" + pose.split("ENDMDL")[0] + "ENDMDL\n"
        sdf_path = os.path.join(out_dir, f"pose_{i:04d}.sdf")
        with open("/tmp/tmp_pose.pdbqt", "w") as tmp:
            tmp.write(pose_block)
        subprocess.run(["obabel", "/tmp/tmp_pose.pdbqt", "-O", sdf_path], check=True)
        if verbose:
            print(f"[INFO] Saved: {sdf_path}")
