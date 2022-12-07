import operator
import sys, os
from pyspark import SparkConf, SparkContext
import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg
from sklearn.manifold import TSNE


# Macros.
MAX_ITER = 20
DATA_PATH = "gs://6893_course_data/hw1_q1/data.txt"
C1_PATH = "gs://6893_course_data/hw1_q1/c1.txt"
C2_PATH = "gs://6893_course_data/hw1_q1/c2.txt"
NORM = 2


# Helper functions
def closest(p, centroids, norm):
    """
    Compute closest centroid for a given point.
    Args:
        p (numpy.ndarray): input point
        centroids (list): A list of centroids points
        norm (int): 1 or 2
    Returns:
        int: The index of closest centroid.
    """
    closest_c = min([(i, linalg.norm(p - c, norm))
                    for i, c in enumerate(centroids)],
                    key=operator.itemgetter(1))[0]
    return closest_c


def within_cluster_cost(data, norm):
    """
    Compute within-cluster cost.
    Args:
        data (RDD): a RDD of the form (centroid, (point, 1))
        norm (int): 1 or 2
    Returns:
        Float: Within-cluster cost of the current classification.
    """
    cost = sum(data.map(lambda pt: linalg.norm(pt[1][0] - pt[0], norm)).collect())
    return cost


def tSNE_vis(data):
    """
    Produce a 2D dimension of the clustering result.
    Args:
        data (RDD): a RDD of (centroid, (point, 1))
    Returns:
        None
    """
    arr = data.map(lambda pt: [pt[0]] + list(pt[1][0])).collect()
    embedded = TSNE(n_components=2).fit_transform(np.array(arr))
    x, y = embedded[:, 0], embedded[:, 1]
    plt.scatter(x, y)
    plt.show()
    
    print(os.getcwd())
    
    # plt.savefig("gs://6893_course_data/hw1_q1/tsne.png")
    plt.savefig("tsne.png")


# K-means clustering
def kmeans(data, centroids, norm=NORM):
    """
    Conduct k-means clustering given data and centroid.
    Args:
        data (RDD): RDD of points
        centroids (list): A list of centroids points
        norm (int): 1 or 2
    Returns:
        RDD: assignment information of points, a RDD of (centroid, (point, 1))
        list: a list of centroids
    """
    
    cost_list = np.zeros(MAX_ITER)
    
    # iterative k-means
    for i in range(MAX_ITER):
        
        # Points assignment
        points = data.map(lambda p: (closest(p, centroids, norm), (p, 1)))
        
        # Cost Calculation
        cost_list[i] = within_cluster_cost(points, NORM)
        
        # Updata centroids
        reduced_pts = points.reduceByKey(lambda p1, p2: (p1[0] + p2[0], p1[1] + p2[1]))
        centroids = reduced_pts.values().map(lambda c: c[0] / c[1]).collect()
        
    # cost plot
    plt.plot(cost_list)
    plt.xlabel('Iterations')
    plt.ylabel('Cost')
    plt.title('Within-cluster plot under L%d norm'%NORM)
    plt.show()
    # plt.savefig("gs://6893_course_data/hw1_q1/cost_L%d.png"%NORM)
    
    return points, centroids



def main():
    # Spark settings
    conf = SparkConf()
    sc = SparkContext(conf=conf)

    # Load the data, cache this since we're accessing this each iteration
    data = sc.textFile(DATA_PATH).map(
            lambda line: np.array([float(x) for x in line.split(' ')])
            ).cache()
    # Load the initial centroids c1, split into a list of np arrays
    centroids1 = sc.textFile(C1_PATH).map(
            lambda line: np.array([float(x) for x in line.split(' ')])
            ).collect()
    # Load the initial centroids c2, split into a list of np arrays
    centroids2 = sc.textFile(C2_PATH).map(
            lambda line: np.array([float(x) for x in line.split(' ')])
            ).collect()

    clustered, updated_centroids = kmeans(data, centroids1, NORM)
    # clustered, updated_centroids = kmeans(data, centroids2, NORM)
    
    # t-SNE visualization
    tSNE_vis(clustered)
    
    
    
    
    

if __name__ == "__main__":
    main()
