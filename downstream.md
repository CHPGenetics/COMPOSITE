Removing multiplets from the Seurat object using COMPOSITE output
================

``` r
library(Seurat)
library(Signac)
library(Matrix)
```

### Loading the demo Seurat object and the COMPOSITE output

``` r
load("demo_data.RData")
multiplet = read.csv("Multiplet_prediction.csv")
```

### Removing the predicted multiplets from the Seurat object

``` r
demo_data$multiplet_label = multiplet$multiplet_classification
demo_data = subset(demo_data, subset = multiplet_label == 0)
```
