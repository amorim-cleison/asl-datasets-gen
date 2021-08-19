# **ASL-Skeleton3D** and **ASL-Phono** Datasets Generator

![Build](https://github.com/amorim-cleison/asllvd-skeleton-creator/workflows/Build/badge.svg)
![Code Quality](https://github.com/amorim-cleison/asllvd-skeleton-creator/workflows/Code%20Quality/badge.svg)


This is the source code used to generate the **ASL-Skeleton3D** and **ASL-Phono** datasets, which are based on the [American Sign Language Lexicon Video Dataset (ASLLVD)](http://www.bu.edu/asllrp/av/dai-asllvd.html).

The **ASL-Skeleton3D** contains a representation based on mapping  into  the  three-dimensional  space  the  coordinates  ofthe  signers  in  the  ASLLVD  dataset. The **ASL-Phono**, in turn, introduces a novel linguistics-based representation,  which  describes  the  signs  in  the  ASLLVD  dataset in terms of a set of attributes of the American Sign Language phonology.

Learn more about the datasets:

- Paper: "ASL-Skeleton3D and ASL-Phono: Two NovelDatasets for the American Sign Language" -->
[Pre-print (arXiv)](http://www.cin.ufpe.br/~cca5/asl-3d-phono-datasets)


### Previous works
In the past, we worked on previous versions of the datasets presented here. Although those versions are now deprecated, you can find more about them in the links:

- Paper: "Spatial-Temporal Graph Convolutional Networks for Sign Language Recognition" --> 
[ICANN 2019](https://doi.org/10.1007/978-3-030-30493-5_59) |
[Pre-print (arXiv)](https://arxiv.org/pdf/1901.11164)


## Requirements
Your system is required to have the following software configured:
- [Python 3.7 (or later)](https://www.python.org/downloads/)
- [Poetry (latest)](https://python-poetry.org/)
- [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose)
  - [OpenPose: additional requirements and dependencies](https://github.com/CMU-Perceptual-Computing-Lab/openpose/blob/master/doc/installation/0_index.md#operating-systems-requirements-and-dependencies)
- asllvd-vid-reader (available embedded to this project in `./3rd_party/` folder or at [source-code repository](https://github.com/amorim-cleison/asllvd-vid-reader))

OpenPose will require your machine to have additional hardware and software configured which might include (but not limited to) the following. Check the link
- NVIDIA GPU (graphic card with at least 1.6 GB available)
- [CUDA 10.0 (or later)](https://developer.nvidia.com/cuda-downloads)
- [cuDNN 7 (or later)](https://developer.nvidia.com/cudnn)


> Alternatively, you can use the following Docker container, which contains most of the software requirements above (make sure to observe the hardware requirements):
> - [Docker / OpenPose](https://hub.docker.com/r/amorimcleison/openpose)


## Installation
Once observed the requirements above, checkout the source code and execute the following command. This will configure a virtual environment and install the dependencies required:

```
poetry install
```

## Configuration
The generation of datasets is performed through several phases, ranging from downloading the ASLLVD samples to generating skeletons and processing additional attributes, as follows:

- **download**: videos are obtained from the ASLLVD.
- **segment**: signs are segmented from original videos.
- **skeleton**: skeletons are estimated.
- **normalize**: coordinates of the skeletons are normalized.
- **phonology**: phonological attributes are extracted.

Thus, in order to configure the parameters of the phases above, you can use the files under the folder `./config`. 


There are also predefined configuration that will allow you easily proceed with the generation of the ASL datasets:
- `./config/asl-skeleton3d.yaml`
- `./config/asl-phono.yaml`



## Execution

To execute this code, run
```
python main.py preprocessing -c config/config.yaml [--work_dir <work folder>]
```
The training results, configurations and logging files, will be saved under the ```./work_dir``` by default or ```<work folder>``` if you appoint it.

You can modify the preprocessing parameters in the command line or configuration files. The order of priority is:  command line > config file > default parameter. For more information, use ```main.py -h```.


## Configuration

Details on how to configure preprocessing can be obtained below

[config/](config/)


## Citation
Please cite the following paper if you use this repository in your reseach.
```
@article{stgcnsl2019,
  title     = {Spatial-Temporal Graph Convolutional Networks for Sign Language Recognition},
  author    = {Cleison Correia de Amorim and David Macêdo and Cleber Zanchettin},
  year      = {2019},
}
```

## Contact
For any question, feel free to contact me at
```
Cleison Amorim  : cca5@cin.ufpe.br
```
