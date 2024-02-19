library(Matrix)
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v75)

args <- commandArgs(trailingOnly = TRUE)
path_target <- args[1]
path_h5 <- args[2]
path_meta <- args[3]
path_frag <- args[4]

counts = Read10X_h5(path_h5)

metadata <- read.csv(
  file = path_meta,
  header = TRUE,
  row.names = 1
)

chrom_assay <- CreateChromatinAssay(
  counts = counts,
  sep = c(":", "-"),
  fragments = path_frag,
  min.cells = 0,
  min.features = 0
)

data <- CreateSeuratObject(
  counts = chrom_assay,
  assay = "peaks",
  meta.data = metadata
)

annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v75)
seqlevels(annotations) <- paste0('chr', seqlevels(annotations))
genome(annotations) <- "hg19"
Annotation(data) <- annotations

DefaultAssay(data) = 'peaks'

inferred_rna = GeneActivity(data)

writeMM(inferred_rna, file = paste0(path_target, '/ATAC.mtx'))
