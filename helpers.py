# This python notebooks contains some helpers to the analysis and all the visualisation function.
#librairies
from shapely.geometry import Polygon,Point
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd 

# helper

def create_poly(df):
    '''
    INPUT: dataset with the location of the low left point (ll_x,ll_y) and the high right point (ur_x,ur_y) for each tiles
    OUTPUT: polygons for plots of all tiles
    '''
    
    p1 = Point(df.ll_x,df.ll_y)
    p2 = Point(df.ll_x,df.ur_y)
    p3 = Point(df.ur_x,df.ur_y)
    p4 = Point(df.ur_x,df.ll_y)
    pointList = [p1, p2, p3, p4, p1]
    return Polygon(pointList)
                    
def plot_time_series_cluster(df,title,xticks_lab):
    plt.figure(figsize=(14,6))
    plt.plot(df)
    plt.title(title,fontweight="bold")
    plt.legend(range(0,df.shape[0]))
    plt.xticks(range(0,24),labels=xticks_lab,rotation=90,fontweight="bold")
    plt.yticks(fontweight="bold")
    plt.show()
    
def plot_sse(data, start=2, end=11):
    sse = []
    for k in range(start, end):
        # Assign the labels to the clusters
        kmeans = KMeans(n_clusters=k, random_state=10).fit(data)
        sse.append({"k": k, "sse": kmeans.inertia_}) # SSE = .inertia 

    sse = pd.DataFrame(sse)
    # Plot the data
    plt.figure(figsize=(14,6))
    plt.plot(sse.k, sse.sse)
    plt.xlabel("K",fontweight="bold")
    plt.ylabel("Sum of Squared Errors",fontweight="bold")
    plt.xticks(fontweight="bold")
    plt.yticks(fontweight="bold")

def plot_tsne_pca(X_reduced_tsne,X_reduced_pca,labels):
    fig, axs = plt.subplots(1, 2, figsize=(14,6), sharey=False)

    # Plot the data reduced in 2d space with t-SNE
    axs[0].scatter(X_reduced_tsne[:,0], X_reduced_tsne[:,1], c=labels, alpha=0.6)
    axs[0].set_title("t-SNE",fontweight="bold")

    # Plot the data reduced in 2d space with PCA
    axs[1].scatter(X_reduced_pca[:,0], X_reduced_pca[:,1], c=labels, alpha=0.6)
    axs[1].set_title("PCA",fontweight="bold")

    plt.xticks(fontweight="bold")
    plt.yticks(fontweight="bold")
    plt.show()