# -*- coding:utf-8 -*-
import numpy as np

# PCA的训练函数
def pca(data,nRedDim=0,normalise=0):
    # 数据标准化
    m = np.mean(data,axis=0)
    data -= m
    # 协方差矩阵
    C = np.cov(np.transpose(data))
    # 计算特征值evals,特征向量evecs，按降序排序
    evals,evecs = np.linalg.eig(C)
    indices = np.argsort(evals)
    indices = indices[::-1]
    evecs = evecs[:,indices]
    evals = evals[indices]
    if nRedDim>0:
        evecs = evecs[:,:nRedDim]

    if normalise:
        for i in range(np.shape(evecs)[1]):
            evecs[:,i] / np.linalg.norm(evecs[:,i]) * np.sqrt(evals[i])
    # 产生新的数据矩阵
    x = np.dot(np.transpose(evecs),np.transpose(data))
    # 重新计算原数据
    y=np.transpose(np.dot(evecs,x))+m
    return x,y,evals,evecs