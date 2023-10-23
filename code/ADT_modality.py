from stable_feature_selection import select_stable
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


#Initialization for multivariate gaussian parameters
#parameter alpha is the location parameter, and beta is the covariance matrix/std parameter
#the covariance parameter is estimated by the unbiased estimator

def initialization_adt(theta, data, corr):

  if corr == True:
      #theta is a numerical value
      #data should be the count matrix in tensor form
      theta = torch.tensor(theta, device = dev)
      alpha = torch.mean(data, dim=0)
      beta = torch.cov(torch.transpose(data,0,1))


      theta = theta.requires_grad_()
      alpha = alpha.requires_grad_()
      beta = beta.requires_grad_()

  else:
      #theta is a numerical value
      #data should be the count matrix in tensor form
      theta = torch.tensor(theta, device = dev)
      alpha = torch.mean(data, dim=0)
      var = torch.var(data, dim=0)
      beta = torch.sqrt(var)


      theta = theta.requires_grad_()
      alpha = alpha.requires_grad_()
      beta = beta.requires_grad_()


  return theta, alpha, beta



#log likelihood with logsumexp
def loglik_adt(N, theta, alpha, beta, decay, data, corr):

  if corr == True:

      #N is the user estimated maximum number of cells in a droplet
      #theta, alpha, and beta are outputs from initialization function
      #data should be the count matrix in tensor form
      poisson = torch.distributions.Poisson(theta)
      list_k = torch.zeros(N,data.shape[0])
      for k in range(N):
        gaussian = torch.distributions.MultivariateNormal(alpha*(1+torch.tensor(k, device = dev)/(1+torch.exp(-decay))), torch.tensor(k+1, device = dev)*beta)
        list_k[k] = gaussian.log_prob(data)+poisson.log_prob(torch.tensor([k], device = dev))

      sum_k = torch.logsumexp(list_k,0)
      l = torch.sum(sum_k, dtype = torch.float64)


  else:
      #N is the user estimated maximum number of cells in a droplet
      #theta, alpha, and beta are outputs from initialization function
      #data should be the count matrix in tensor form
      poisson = torch.distributions.Poisson(theta)
      list_k = torch.zeros(N, data.shape[0], data.shape[1])
      for k in range(N):
        gaussian = torch.distributions.Normal(alpha*(1+torch.tensor(k, device = dev)/(1+torch.exp(-decay))), torch.tensor(k+1, device = dev)*beta)
        list_k[k] = gaussian.log_prob(data)+poisson.log_prob(torch.tensor([k], device = dev))

      sum_k = torch.logsumexp(list_k, 0)
      l = torch.sum(sum_k, dtype = torch.float64)


  return l

def MLE_adt(data, N=3, p=0.7, lr=0.02, tolerance = 15, corr = False):
   #p is a numerical value, initial guess of singlet rate; this value doesn't have a big impact on parameter estimation
   #data should be the count matrix in tensor form
   #N is the user estimated maximum number of cells in a droplet
   #tolerance controls how many steps we allow the loss not to improve

    x = data
    x.requires_grad_(False)  ## data

    decay = torch.tensor(0.0, device = dev)
    decay = decay.requires_grad_()

    theta = -math.log(p)
    theta, alpha, beta = initialization_adt(theta, data, corr)
    alpha0 = 0.5*torch.mean(alpha).to('cpu').detach().item()

    parameters = [theta, alpha, beta, decay]


    optimizer = optim.Adam(parameters, lr=lr, eps = 1e-6, weight_decay=0.1)

    l = []
    singlet_rate = []


    for i in range(10000):
        NLL = -loglik_adt(N, theta, alpha, beta, decay, x, corr)
        if i % 200 == 0:
            l.append(NLL.to('cpu').detach())
            singlet_rate.append(torch.tensor([-theta]).exp())
            if len(l) > 2:
              if (l[-2] - l[-1]) < 0.01*(l[0] - l[1]):
                tolerance = tolerance - 1
        if tolerance == 0:
          break

        NLL.backward()
        optimizer.step()
        optimizer.zero_grad()
        theta.data.clamp_(0.01, 1.0)
        decay.data.clamp_(-10, 10)
        alpha.data.clamp_(min = 0)
        beta.data.clamp_(min = 0)



    return theta, alpha, beta, decay, l, singlet_rate



def log_joint_one_k_adt(data, theta, alpha, beta, decay, k0, corr):

  if corr == True:
      #k0 starts from 0, same interpretation as the k0 in the derivation
      alpha = alpha.to('cpu').detach().numpy()
      beta = beta.to('cpu').detach().numpy()
      data = data.to('cpu').numpy()
      theta = theta.to('cpu').detach().numpy()
      decay = decay.to('cpu').detach().numpy()

      alpha = alpha*(1+k0/(1+np.exp(-decay)))

      log_conditional = np.log(multivariate_normal.pdf(data, mean=alpha, cov=beta)+1e-320)
      log_joint = log_conditional + np.log(poisson.pmf(k0, theta))


  else:
      #k0 starts from 0, same interpretation as the k0 in the derivation
      alpha = alpha.to('cpu').detach().numpy()
      beta = beta.to('cpu').detach().numpy()
      data = data.to('cpu').numpy()
      theta = theta.to('cpu').detach().numpy()
      decay = decay.to('cpu').detach().numpy()

      alpha = alpha*(1+k0/(1+np.exp(-decay)))

      log_conditional = np.log(norm.pdf(data, loc=alpha, scale=beta)+1e-320) #add a small value to avoid log(0)
      sum_gene = np.sum(log_conditional, axis = 1)
      log_joint = sum_gene + np.log(poisson.pmf(k0, theta))
      var_by_cell = np.var(np.exp(log_conditional), axis = 1)

  return log_joint

def prob_k0_adt(data, theta, alpha, beta, decay, k0, k=3, corr = False):
  log_joint_k0 = log_joint_one_k_adt(data, theta, alpha, beta, decay, k0, corr)

  one_ks = np.ones((data.shape[0],k))
  for i in np.arange(k):
    one_ks[:,i] = log_joint_one_k_adt(data, theta, alpha, beta, decay, i, corr)

  logsumexp_ks = special.logsumexp(one_ks, axis = 1)
  log_prob = log_joint_k0 - logsumexp_ks
  log_prob = log_prob.astype('float128')
  prob = np.exp(log_prob, dtype=np.float128)



  return prob

def reliability_adt(data, theta, alpha, beta, decay, k=3,corr = False):

    if corr == True:
        beta = torch.diagonal(beta, 0)
        beta = torch.sqrt(beta)

        prob_singlet = prob_k0_adt(data, theta, alpha, beta, decay, 0, k, corr = True)
        prob_doublet = 1-prob_singlet
        pred = np.where(prob_doublet > 0.5, True, False)

    else:
        prob_singlet = prob_k0_adt(data, theta, alpha, beta, decay, 0, k)
        prob_doublet = 1-prob_singlet
        pred = np.where(prob_doublet > 0.5, True, False)

    alpha = alpha.to('cpu').detach().numpy()
    beta = beta.to('cpu').detach().numpy()
    data = data.to('cpu').numpy()
    theta = theta.to('cpu').detach().numpy()
    decay = decay.to('cpu').detach().numpy()

    one_ks = np.ones((data.shape[0], data.shape[1], k))
    for i in np.arange(k):
        alpha_k = alpha*(1+i/(1+np.exp(-decay)))
        one_ks[:,:,i] = np.log(norm.pdf(data, loc=alpha_k, scale=beta)+1e-320)

    reliability = 1 - (np.exp(one_ks[:,:,0]-special.logsumexp(one_ks, axis = 2))) #probability of doublets predicted by individual feature

    #if individual feature prediction result is the same as result by all features, then record as 1. otherwise record as 0
    #then, calculate proportion of features that can individually provide correct prediction
    reliability[pred,:]=np.where(reliability[pred,:] > 0.5, 1, 0) #predicted doublets
    reliability[list(map(operator.not_, pred)),:]=np.where(reliability[list(map(operator.not_, pred)),:] < 0.5, 1, 0)

    reliability = np.sum(reliability, axis = 1)/data.shape[1]

    result = np.zeros((2, data.shape[0]))
    result[0,:] = reliability
    result[1,:] = np.where(reliability <= 0.5, 1, 0) #flags the cells whose prediction is subject to outliers


    return result

def adt_fit_goodness(data, alpha, beta, theta, decay, k=3, corr=False):

    if corr == True:
        beta = torch.diagonal(beta, 0)
        beta = torch.sqrt(beta)

    data = torch.round(data)
    data = data.int()
    data = data.to('cpu').numpy()
    alpha = alpha.to('cpu').detach().numpy()
    beta = beta.to('cpu').detach().numpy()
    theta = theta.to('cpu').detach().numpy()
    decay = decay.to('cpu').detach().numpy()

    empirical = np.apply_along_axis(lambda x: np.bincount(x, minlength=np.max(data)+1), axis=0, arr=data)
    empirical_dist = empirical/data.shape[0] #+ 1e-100 #adjust 1e-100 as needed
    empirical_dist #each column is the empirical distribution of a gene

    for i in range(empirical_dist.shape[0]-1):
        empirical_dist[i+1,] += empirical_dist[i,] #empirical cdf

    #calculate theoretical cdf below
    grid = np.expand_dims(np.arange(0, empirical_dist.shape[0], 1, dtype=int)+0.0001,axis=1)
    grid=np.repeat(grid, empirical_dist.shape[1], axis = 1)
    one_ks = np.ones((grid.shape[0], grid.shape[1], k))

    for i in np.arange(k):
        alpha_k = alpha*(1+i/(1+np.exp(-decay)))
        one_ks[:,:,i] = np.log(norm.cdf(grid, loc=alpha_k, scale=beta))+np.log(poisson.pmf(i, theta))

    logsumexp_ks = special.logsumexp(one_ks, axis = 2)
    theoretical_dist = np.exp(logsumexp_ks)

    diff = np.abs(theoretical_dist-empirical_dist)
    mean_ks = np.mean(np.amax(diff, axis = 0))

    if mean_ks > 0.33:
        print("The ADT modality goodness-of-fit score is less than 3; The model may not fit the data well")

    return mean_ks

def composite_adt(input_path, multiomics=False, N=3, lr=0.02, p=0.7, stable_criterion = "signal", stable_number = None, tolerance = 15, corr = False):

    #N: the maximum number of cells in a droplet that will be modeled
    #lr: learning rate in the maximum likelihood estimation step; Note that the recommanded learning rates for different modalities are different
    #p: user estimated singlet proportion
    #stable_criterion: By default, stable features are selected to have high signal-to-noise ratio.
    #                  User may set it to "mean" so that stable features are selected to have high mean expression level
    #stable_number: number of stable features to be selected for modeling
    #tolerance: Controls early stopping. Increasing this number may slightly improve model performance but will significantly increase computing time
    #corr: whether or not we consider the correlation between stable ADT features. Setting it to True is not recommanded
    global dev
    if torch.cuda.is_available():
      dev = "cuda:0"
    else:
      dev = "cpu"
    device = torch.device(dev)

    if torch.cuda.is_available():
       print ("Cuda is available; Fitting the COMPOSITE model on the ADT modality")
       device_id = torch.cuda.current_device()
       gpu_properties = torch.cuda.get_device_properties(device_id)
       print("Found %d GPUs available. Using GPU %d (%s) of compute capability %d.%d with "
              "%.1fGb total memory.\n" %
              (torch.cuda.device_count(),
              device_id,
              gpu_properties.name,
              gpu_properties.major,
              gpu_properties.minor,
              gpu_properties.total_memory / 1e9))
    else:
       print ("Cuda is not available; Fitting the COMPOSITE model on ADT modality")

    adt_input = mmread(input_path)
    stable = select_stable(adt_input, modality = "ADT", criterion = stable_criterion, stable_number = stable_number)
    stable = torch.tensor(stable, device = dev)
    stable = stable.double()
    stable = stable + torch.tensor([0.0001], device = dev)
    theta,alpha,beta,decay, loss,p = MLE_adt(stable, N=N, p=p,lr=lr, tolerance=tolerance, corr=corr)
    adt_fit = adt_fit_goodness(stable, alpha, beta, theta, decay,k=N, corr=corr)

    prob_singlet = prob_k0_adt(stable, theta, alpha, beta, decay, 0, k=N, corr=corr)
    prob_doublet = 1-prob_singlet
    doublet_classification = np.where(prob_doublet > 0.5, 1, 0)
    reliability_table = reliability_adt(stable, theta, alpha, beta, decay, k=N, corr=corr)
    adt_overall_weight = reliability_table[0,]/adt_fit
    data = {#'prob_doublet': prob_doublet,
            'doublet_classification': doublet_classification,
            'consistency':reliability_table[0,]}
    # Create DataFrame
    reliability_file = pd.DataFrame(data)
    reliability_file.index.name = 'index'
    reliability_file.reset_index(inplace=True)
    #reliability_file.to_csv(output_path, index=False)

    print("The ADT modality goodness-of-fit score is:", 1/adt_fit, "\n<3: poor fit \n3~5: moderate fit \n>5: good fit")

    if multiomics == False:
        return doublet_classification, reliability_table[0,]
    else:
        return prob_doublet, adt_overall_weight
