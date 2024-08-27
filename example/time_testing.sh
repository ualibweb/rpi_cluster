#!/bin/bash

# Script to submit jobs for all combinations of nodes (1-3) and CPUs per node (1-4)
# Modify the script name and parameters as needed

# Loop over number of nodes (1 to 3)
for nodes in {1..3}; do
  # Loop over number of CPUs per node (1 to 4)
  for cpus in {1..4}; do
    # Submit the job with the specified number of nodes and CPUs per node
    sbatch --nodes=$nodes --ntasks-per-node=$cpus <<-EOF
#!/bin/bash
#SBATCH -J mpi_test_${nodes}nodes_${cpus}cpus
#SBATCH -e errors/errors_mpi_${nodes}nodes_${cpus}cpus.%A
#SBATCH -o outputs/output_mpi_${nodes}nodes_${cpus}cpus.%A

# Activate the conda environment
source /cluster/miniconda/etc/profile.d/conda.sh
conda activate rdkit_w_mpi
sleep 25

# Change to the directory where the job was submitted
cd \$SLURM_SUBMIT_DIR

# Calculate the total number of tasks
TOTAL_TASKS=\$((SLURM_NNODES * SLURM_NTASKS_PER_NODE))

# Run the MPI program with the calculated number of tasks
mpiexec -n \$TOTAL_TASKS python3 ./TAN_MPI.py

EOF
  done
done
