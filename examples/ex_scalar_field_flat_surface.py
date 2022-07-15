#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import sys
from GeoDySys import plotting, utils, geometry
from GeoDySys.model import net


def main():
    
    #parameters
    n = 512
    k = 20
    n_clusters = 10
    radius = 1
    
    par = {'batch_size': 256, #batch size, this should be as large as possible
           'epochs': 20, #optimisation epochs
           'order': 1, #order of derivatives
           'n_lin_layers': 2,
           'hidden_channels': 16, #number of internal dimensions in MLP
           'out_channels': 4,
           }
    
    #evaluate functions
    # f1: constant, f2: linear, f3: parabola, f4: saddle
    x0 = geometry.sample_2d(n, [[-1,-1],[1,1]], 'random')
    x1 = geometry.sample_2d(n, [[-1,-1],[1,1]], 'random')
    x2 = geometry.sample_2d(n, [[-1,-1],[1,1]], 'random')
    x3 = geometry.sample_2d(n, [[-1,-1],[1,1]], 'random')
    x = [x0, x1, x2, x3]
    y = [f0(x0), f1(x1), f2(x2), f3(x3)] #evaluated functions
        
    #construct PyG data object
    data = utils.construct_dataset(x, y, graph_type='cknn', k=k)
    
    #train model
    model = net(data, gauge='global', **par)
    model.train_model(data)
    emb = model.evaluate(data)
    emb, clusters = geometry.cluster_and_embed(emb, n_clusters=n_clusters)
    
    #plot
    titles=['Constant','Linear','Parabola','Saddle']
    plot_functions(data, titles=titles) #sampled functions
    plt.savefig('../results/scalar_fields.svg')
    plotting.embedding(emb, clusters, data.y.numpy(), titles=titles) #TSNE embedding 
    plt.savefig('../results/scalar_fields_embedding.svg')
    plotting.histograms(data, clusters, titles=titles) #histograms
    plt.savefig('../results/scalar_fields_histogram.svg')
    plotting.neighbourhoods(data, clusters, n_samples=4, radius=radius, norm=True) #neighbourhoods
    plt.savefig('../results/scalar_fields_nhoods.svg')
    

# def f0(x, alpha=1):
#     return np.cos(alpha)*x[:,[0]] + np.sin(alpha)*x[:,[1]]
  
# def f1(x, alpha=2):
#     return np.cos(alpha)*x[:,[0]] + np.sin(alpha)*x[:,[1]]

# def f2(x, alpha=3):
#     return np.cos(alpha)*x[:,[0]] + np.sin(alpha)*x[:,[1]]

# def f3(x, alpha=4):
#     return np.cos(alpha)*x[:,[0]] + np.sin(alpha)*x[:,[1]]
    
def f0(x):
    return x[:,[0]]*0

def f1(x):
    return x[:,[0]] + x[:,[1]]

def f2(x):
    return x[:,[0]]**2 + x[:,[1]]**2

def f3(x):
    return x[:,[0]]**2 - x[:,[1]]**2


def plot_functions(data, titles=None):
    import matplotlib.gridspec as gridspec
    from torch_geometric.utils.convert import to_networkx

    fig = plt.figure(figsize=(10,10), constrained_layout=True)
    grid = gridspec.GridSpec(2, 2, wspace=0.2, hspace=0.2)
    
    data_list = data.to_data_list()
    
    for i, d in enumerate(data_list):
        
        G = to_networkx(d, node_attrs=['pos'], edge_attrs=None, to_undirected=True,
                remove_self_loops=True)
        
        ax = plt.Subplot(fig, grid[i])
        ax.set_aspect('equal', 'box')
        c=plotting.set_colors(d.x.numpy(), cbar=False)
        plotting.graph(G,node_values=c,show_colorbar=False,ax=ax,node_size=30,edge_width=0.5)
        
        if titles is not None:
            ax.set_title(titles[i])
        fig.add_subplot(ax)  


if __name__ == '__main__':
    sys.exit(main())