#!/usr/bin/env python
# coding: utf-8

from mpi4py import MPI
from time import time
from pprint import pprint
from rdkit import rdBase
from rdkit.Chem import rdFMCS
import pickle
from rdkit import Chem
from rdkit.Chem import rdMolDescriptors
from rdkit import DataStructs

def t_sim(mol1, mol2, key):
    fp1 = Chem.RDKFingerprint(mol1)
    fp2 = Chem.RDKFingerprint(mol2)
    tan_sim = round(DataStructs.TanimotoSimilarity(fp1,fp2), 3)
    return key, tan_sim

def main():
    total_start_time = time()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    if rank == 0:
        with open('mol_objects.pickle', 'rb') as infile:
            mol_objects = pickle.load(infile)

        with open('subsets.pickle', 'rb') as infile:
            subsets = pickle.load(infile)

        mol_tuples = [(mol_objects[value["smi1"]], mol_objects[value["smi2"]], key) for key, value in subsets.items()]

        chunk_size = len(mol_tuples) // size
        chunks = [mol_tuples[i*chunk_size : (i+1)*chunk_size] for i in range(size)]
        if len(mol_tuples) % size != 0:
            chunks[-1].extend(mol_tuples[size*chunk_size:])

    else:
        chunks = None
    
    # Time to scatter the data
    scatter_start_time = time()
    local_chunk = comm.scatter(chunks, root=0)
    scatter_end_time = time()
    
    if rank == 0:
        print(f"Time to scatter data: {scatter_end_time - scatter_start_time:.4f} seconds")

    # Time for local calculations
    calc_start_time = time()
    local_results = [t_sim(mol1, mol2, key) for mol1, mol2, key in local_chunk]
    calc_end_time = time()
    
    # Calculate and print average time per calculation
    avg_calc_time = (calc_end_time - calc_start_time) / len(local_chunk)
    print(f"Rank {rank}: Average time per calculation: {avg_calc_time:.4f} seconds")

    # Time to gather the results
    gather_start_time = time()
    gathered_results = comm.gather(local_results, root=0)
    gather_end_time = time()
    
    if rank == 0:
        print(f"Time to gather results: {gather_end_time - gather_start_time:.4f} seconds")

        # Combine and save results
        results = [item for sublist in gathered_results for item in sublist]
        for key, tan_mcs in results:
            subsets[key].update({"tan_mcs": round(tan_mcs, 3)})

        with open('subsets_mcs_multi.pickle', 'wb') as outfile:
            pickle.dump(subsets, outfile, pickle.HIGHEST_PROTOCOL)

        print("File saved as: subsets_mcs_multi.pickle")

    # Total execution time
    if rank == 0:
        total_end_time = time()
        print(f"Total Time: {total_end_time - total_start_time:.4f} seconds")

if __name__ == '__main__':
    main()
