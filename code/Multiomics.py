from stable_feature_selection import select_stable
from RNA_modality import *
from ADT_modality import *
from ATAC_modality import *
import numpy as np
import pandas as pd
import scipy
from scipy.io import mmread
import random
import math
#import scanpy as sc
import torch
import torch.nn as nn
import torch.optim as optim
import torch.utils.data
import torch.nn.functional as F
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.stats import gamma
from scipy.stats import poisson
from scipy.stats import multivariate_normal
from sklearn.metrics import roc_auc_score
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc
from scipy import special
import operator
from numpy import genfromtxt

def composite_multiomics(RNA = None, ADT = None, ATAC = None, N=3, lr1=0.001, lr2=0.02, p=0.7, stable_criterion = "signal", stable_number_RNA = None, stable_number_ADT = None, stable_number_ATAC = None, tolerance=10, corr=False, lbda=0.5):
    if RNA is not None and ADT is not None and ATAC is not None:
        rna_prob_doublet, rna_final_weight = composite_rna(RNA, multiomics = True, N=N, lr=lr1, p=p, stable_criterion=stable_criterion, stable_number=stable_number_RNA, tolerance=tolerance)
        adt_prob_doublet, adt_final_weight = composite_adt(ADT, multiomics = True, N=N, lr=lr2, p=p, stable_criterion=stable_criterion, stable_number=stable_number_ADT, tolerance=tolerance, corr=corr)
        atac_prob_doublet, atac_final_weight = composite_atac(ATAC, multiomics = True, N=N, lr=lr1, p=p, stable_criterion=stable_criterion, stable_number=stable_number_ATAC, tolerance=tolerance, lbda=lbda)

        weight_joint = np.stack((rna_final_weight, adt_final_weight, atac_final_weight))
        weight_joint = special.softmax(weight_joint, axis = 0)
        combined_prediction = weight_joint[0,:]*rna_prob_doublet + weight_joint[1,:]*adt_prob_doublet + weight_joint[2,:]*atac_prob_doublet

        combined_classification = np.where(combined_prediction > 0.5, 1, 0)
        return combined_classification, combined_prediction
        
    elif RNA is not None and ADT is not None:
        rna_prob_doublet, rna_final_weight = composite_rna(RNA, multiomics = True, N=N, lr=lr1, p=p, stable_criterion=stable_criterion, stable_number=stable_number_RNA, tolerance=tolerance)
        adt_prob_doublet, adt_final_weight = composite_adt(ADT, multiomics = True, N=N, lr=lr2, p=p, stable_criterion=stable_criterion, stable_number=stable_number_ADT, tolerance=tolerance, corr=corr)

        weight_joint = np.stack((rna_final_weight, adt_final_weight))
        weight_joint = special.softmax(weight_joint, axis = 0)
        combined_prediction = weight_joint[0,:]*rna_prob_doublet + weight_joint[1,:]*adt_prob_doublet

        combined_classification = np.where(combined_prediction > 0.5, 1, 0)
        return combined_classification, combined_prediction

    elif RNA is not None and ATAC is not None:
        rna_prob_doublet, rna_final_weight = composite_rna(RNA, multiomics = True, N=N, lr=lr1, p=p, stable_criterion=stable_criterion, stable_number=stable_number_RNA, tolerance=tolerance)
        atac_prob_doublet, atac_final_weight = composite_atac(ATAC, multiomics = True, N=N, lr=lr1, p=p, stable_criterion=stable_criterion, stable_number=stable_number_ATAC, tolerance=tolerance, lbda=lbda)

        weight_joint = np.stack((rna_final_weight, atac_final_weight))
        weight_joint = special.softmax(weight_joint, axis = 0)
        combined_prediction = weight_joint[0,:]*rna_prob_doublet + weight_joint[1,:]*atac_prob_doublet

        combined_classification = np.where(combined_prediction > 0.5, 1, 0)
        return combined_classification, combined_prediction



    else:
        print("No eligible multiomics data was provided.")
