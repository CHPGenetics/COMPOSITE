# COMPOSITE

COMPOSITE (COMpound POiSson multIplet deTEction model) is a computational tool for multiplet detection in both single-omics and multiomics single-cell settings.
It has been implemented as an automated pipeline and is available as both a cloud-based application with a user-friendly interface and a Python package.


![Overview of the COMPOSITE model](./pictures/overview.png)


## Data preparation
To prepare the data from a Seurat object: [Preparing data for COMPOSITE.](https://htmlpreview.github.io/?https://github.com/CHPGenetics/COMPOSITE/blob/main/composite_data_preparation.html)

## Running COMPOSITE


### Option 1: Cloud-based web app

[COMPOSITE cloud-based app](https://ondemand.htc.crc.pitt.edu/rnode/htc-1024-n0.crc.pitt.edu/28614/?)

Note that in order to leverage GPU for acceleration, please use the Python package.


### Option 2: Install the Python package <img align="right" style="margin-left: 20px; margin-bottom: 10px;" src="./pictures/sticker3.png">

<img src="./pictures/sticker3.png" width="245" height="245">



Installation:
```
pip install sccomposite==1.0.0
```
Store the RNA data, ADT data, and ATAC data respectively as "RNA.mtx", "ADT.mtx", and "ATAC.mtx" in the working directory. Import the `sccomposite` package.

```
import sccomposite
from sccomposite import RNA_modality
from sccomposite import ADT_modality
from sccomposite import ATAC_modality
from sccomposite import Multiomics
```
We recommend users to use the default parameter settings when running COMPOSITE. COMPOSITE is a robust statistical model and the default parameters are suitable for most of the cases.  All the [results](https://github.com/CHPGenetics/COMPOSITE/tree/main/experiments/description) in our manuscript were generated under the default parameter setting. We recommand the users to use all the available modalities of data as input.

When only one modality of data is available:

```
# RNA modality only
multiplet_classification, consistency = RNA_modality.composite_rna("RNA.mtx")

# ADT modality only
multiplet_classification, consistency = ADT_modality.composite_adt("ADT.mtx")

# ATAC modality only
multiplet_classification, consistency = ATAC_modality.composite_atac("ATAC.mtx")
```
The `multiplet_classification` variable contains the predicted multiplet label for each droplet, with "1" representing multiplet and "0" representing singlet.

The `consistency` variable contains the droplet-specific modality consistency. A higher value of consistency indicates the data in the corresponding modality are less noisy for the given droplet, resulting in a more reliable multiplet prediction result for the droplet.

When multiomics data are available:
```
# RNA+ADT
multiplet_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ADT =  "ADT.mtx")

# RNA+ATAC
multiplet_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ATAC =  "ATAC.mtx")

# RNA+ADT+ATAC
multiplet_classification, multiplet_probability = Multiomics.composite_multiomics(RNA = "RNA.mtx", ADT =  "ADT.mtx", ATAC =  "ATAC.mtx")
```
The `multiplet_classification` variable contains the predicted multiplet label for each droplet, with "1" representing multiplet and "0" representing singlet.

The `multiplet_probability` variable contains the predicted probability for each droplet to be multiplet, leveraging the information across all the provided modalities. It quantifies the uncertainty of multiplet prediction results.

To save the mutiplet classification result: 

```
import pandas as pd
data = {'multiplet_classification': multiplet_classification}

data_file = pd.DataFrame(data)
data_file.index.name = 'index'
data_file.reset_index(inplace=True)
data_file.to_csv("Multiplet_prediction.csv",index=False)
```
## Using COMPOSITE output in R

We demonstrate how to use the COMPOSITE output to remove the predicted multiplets from the Seurat object: [Eliminating multiplets.](https://htmlpreview.github.io/?https://github.com/CHPGenetics/COMPOSITE/blob/main/downstream.html)
