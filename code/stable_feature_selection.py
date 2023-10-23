import scipy 
from scipy import sparse
import numpy as np

def select_stable(full, modality = "RNA", stable_number = None, criterion = "signal"):

    #full is the data in np array format, either dense or sparse
    
    if sparse.issparse(full)==True:
        full = full.todense()

    if stable_number == None:
        if modality == "RNA":
            stable_number = 300
        elif modality == "ATAC":
            stable_number = 300
        elif modality == "ADT":
            stable_number = 15

    nonzero_proportion = np.array((full>0).sum(axis = 1))/full.shape[1]
    full = np.array(full)
    subset = full[np.squeeze(nonzero_proportion>0.5),]
    high_nonzero = full[np.squeeze(nonzero_proportion>0.5),]
    high_nonzero = np.log1p(high_nonzero)

    if high_nonzero.shape[0]<stable_number:
        print("Warning: too few stable features to provide reliable inference.")
        result = subset


    elif criterion == "signal":
        mean = np.mean(high_nonzero, axis = 1)
        std = np.std(high_nonzero, axis = 1)
        signal = mean/std

        #calculate the rank of the magnitude of signal for each cell
        order = (-signal).argsort()
        ranks = order.argsort()
        result = subset[ranks<stable_number]

    else:
        mean = np.mean(high_nonzero, axis = 1)
        #calculate the rank of the magnitude of mean for each cell
        order = (-mean).argsort()
        ranks = order.argsort()
        result = subset[ranks<stable_number]

    result = np.transpose(result)

    return result
