import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


def all_path(dirname):

    result = []
    for maindir, subdir, file_name_list in os.walk(dirname):
        for filename in file_name_list:
            apath = os.path.join(maindir, filename)
            result.append(apath)

    return result


def dataprocess(dataFiles):

    dataset = []
    i = 0
    for csvFile in dataFiles:
        print(csvFile)
        data_raw = pd.read_csv(csvFile)

        data_raw = data_raw.drop('transition', axis=1)

        data_raw.index = range(1, len(data_raw) + 1)        # without class2

        df_normalized_data = data_raw.apply(lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)))
        df_normalized_data.index = range(1, len(df_normalized_data) + 1)         # without class2

        df_normalized_data = df_normalized_data.T
        dataset.append(df_normalized_data)
        i = i + 1

    return dataset


def combination(dataset):

    merged_df = pd.concat(dataset, axis=1, ignore_index=True)

    return merged_df


def elbowSSE(df_normalized_data, K):

    distortions = []
    for i in K:
        kmModel = KMeans(n_clusters=i)
        kmModel.fit(df_normalized_data)
        distortions.append(kmModel.inertia_)

    plt.plot(K, distortions, marker="o")
    # Set font to Times New Roman
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.unicode_minus'] = False
    plt.xlabel("Number of clusters")
    plt.ylabel("SSE")
    plt.tight_layout()
    plt.savefig('RM2_elbow.png', transparent=True)  # !!!
    plt.show()


def Kmeans(df_normalized_data):

    n_clusters = 8                         # !!!!
    kms = KMeans(n_clusters=n_clusters, init='k-means++')
    data_fig = kms.fit(df_normalized_data)
    centers = kms.cluster_centers_
    labels = kms.labels_

    df_datalable = df_normalized_data
    df_normalized_data['label'] = labels

    df_sorted = df_normalized_data.sort_values(by='label')
    df_sorted.to_csv('data_labeled_RM2.csv', mode='w')                      # ！！！！

    df_centers = pd.DataFrame(kms.cluster_centers_)
    df_centers.columns = range(1, len(df_centers.columns) + 1)  # without class2
    df_centers.to_csv('data_center_RM2.csv', mode='w')                      #  ！！！！

    cluster_result = dict()
    for i in range(n_clusters):
        cluster_indices = df_normalized_data[df_normalized_data['label'] == i].index
        cluster_indices = cluster_indices.tolist()
        cluster_indices = [int(x) for x in cluster_indices]
        cluster_result['Cluster' + str(i)] = cluster_indices
        # print(f'Cluster {i} : {cluster_indices}')

    return n_clusters, cluster_result


if __name__ == "__main__":

    ''' ----------------- pre-processing -------------------- '''
    suspFiles = r"RM2(250)/TrainSusp"           # !!!!
    suspFiles = all_path(suspFiles)
    dataset = dataprocess(suspFiles)

    df_normalized_data = combination(dataset)
    if df_normalized_data.isnull().values.any() or not np.isfinite(df_normalized_data.values).all():

        df_normalized_data.fillna(0, inplace=True)
        df_normalized_data = df_normalized_data.replace([np.inf, -np.inf], np.nan)
        df_normalized_data.fillna(df_normalized_data.mean(), inplace=True)

    df_normalized_data.to_csv('df_normalized_data_RM2.csv', mode='w')                     # !!!

    ''' ----------------- SSE-------------------- '''
    df_normalized_data = pd.read_csv('df_normalized_data_RM2.csv', index_col=0)    # !!!
    K = range(3, 15)                            # !!!!
    elbowSSE(df_normalized_data, K)









