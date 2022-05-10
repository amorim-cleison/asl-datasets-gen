#!/bin/bash
#SBATCH --job-name=ASL-DS
#SBATCH --cpus-per-task=4
#SBATCH --gres=gpu:1
#SBATCH --mem=8G

# Aqui o comando de execução de seu programa.
module load cuda-10.2-gcc-8.3.0-nxzzh52
module load singularity-3.6.2-gcc-8.3.0-quskioo

echo "Starting command..."
cd ../../
singularity exec --nv ~/containers/openpose.sif poetry run python main.py --config config/config-cluster-pos.yaml

echo "Command finished."

