# COMPOSITE

This is a computational tool for multiplet detection in both single-omics and multiomics single-cell setting


## Data preparation
To prepare the data from a Seurat object: [tutorial](https://htmlpreview.github.io/?https://github.com/HAH112/COMPOSITE/composite_data_preparation.html)

## Running COMPOSITE

### Option 1: Install the Python package 

Installation:
```
pip install sccomposite
```
Running COMPOSITE analysis. Store the RNA data, ADT data, and ATAC data respectively as "RNA.mtx", "ADT.mtx", and "ATAC.mtx" in the working directory.
```
import sccomposite
from sccomposite import RNA_modality
from sccomposite import ADT_modality
from sccomposite import ATAC_modality
from sccomposite import Multiomics

# RNA modality only
rna_classification, rna_consistency = RNA_modality.composite_rna("./RNA.mtx")

# ADT modality only
adt_classification, adt_consistency = ADT_modality.composite_adt("./RNA.mtx")

# ATAC modality only
atac_classification, atac_consistency = ATAC_modality.composite_atac("./RNA.mtx")

# RNA+ADT
comined_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ADT =  "ADT.mtx")

# RNA+ATAC
comined_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ATAC =  "ATAC.mtx")

# RNA+ADT+ATAC
comined_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ADT =  "ADT.mtx", ATAC =  "ATAC.mtx")
```

### Option 2: Cloud-based web app

[COMPOSITE cloud-based app](https://ondemand.htc.crc.pitt.edu/rnode/htc-n42.crc.pitt.edu/63206/?#)

Note that in order to leverage GPU for acceleration, please use the Python package.

