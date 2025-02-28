import numpy as np
import pandas as pd
import os
from matplotlib import pyplot as plt
import random
import math
import copy
import Kmeans


# diverHussain
def fun(X, lb, ub):

    dim = X.shape[1]
    vMedia = np.median(X, axis=0)
    divJ = np.average(np.abs(X - vMedia), axis=0)

    lb = lb * np.ones(dim)
    ub = ub * np.ones(dim)

    bd = np.abs(ub - lb).reshape(1, dim)
    divJ_normalized = np.divide(divJ, bd)

    div = np.average(divJ_normalized)
    return div


def initialization(pop, dim, cluster_result):

    X = np.zeros([pop, dim])
    for i in range(pop):

        j = 0
        for cluster_list in cluster_result.values():
            if cluster_list:
                random_formula = random.choice(cluster_list)
                X[i, j] = random_formula
                j += 1

    return X


def CalculateFitness_Susp(X, dim, fun, dataset):

    pop = X.shape[0]
    fitness = np.zeros([pop, 1])
    dataset = dataset.values

    for i in range(pop):

        selected_matrix = np.zeros((dataset.shape[0], dim))
        j = 0
        for f in X[i, :]:
            index = int(f) - 1
            selected_matrix[:, j] = dataset[:, index]
            j += 1

        if selected_matrix.size > 0:
            ub = np.amax(selected_matrix)
            lb = np.amin(selected_matrix)
            fitness[i] = fun(selected_matrix, lb, ub)
        else:

            fitness[i] = 0

    return fitness


def updateCheck(X, pop, dim, cluster_result):
    for i in range(pop):
        for j in range(dim):
            X[i, j] = round(X[i, j])

            update_number = min(cluster_result['Cluster' + str(j)], key=lambda x: abs(x - X[i, j]))
            X[i, j] = update_number

    return X


def SortFitnessDec(Fit):

    fitness = np.sort(Fit, axis=0)[::-1]
    index = np.argsort(Fit, axis=0)[::-1]
    return fitness, index


def SortFitnessInc(Fit):

    fitness = np.sort(Fit, axis=0)
    index = np.argsort(Fit, axis=0)
    return fitness, index


def SortPosition(X, index):

    Xnew = np.zeros(X.shape)
    for i in range(X.shape[0]):
        Xnew[i, :] = X[index[i], :]

    return Xnew


def WOA(pop, dim, MaxIter, fun, dataset, cluster_result):

    X = initialization(pop, dim, cluster_result)
    Curve = np.zeros([MaxIter, 1])

    fitness = CalculateFitness_Susp(X, dim, fun, dataset)

    fitness, sortIndex = SortFitnessDec(fitness)
    X = SortPosition(X, sortIndex)

    GbestScore = copy.copy(fitness[0])
    GbestPosition = np.zeros([1, dim])
    GbestPosition[0, :] = copy.copy(X[0, :])

    for t in range(MaxIter):

        Leader = X[0, :]
        a = 2 - t * (2 / MaxIter)
        for i in range(pop):
            r1 = random.random()
            r2 = random.random()

            A = 2 * a * r1 - a
            C = 2 * r2
            b = 1
            l = 2 * random.random() - 1

            for j in range(dim):
                p = random.random()
                if p < 0.5:
                    if np.abs(A) >= 1:
                        rand_leader_index = min(int(np.floor(pop * random.random() + 1)),
                                                pop - 1)
                        X_rand = X[rand_leader_index, :]
                        D_X_rand = np.abs(C * X_rand[j] - X[i, j])
                        X[i, j] = X_rand[j] - A * D_X_rand
                    elif np.abs(A) < 1:
                        D_Leader = np.abs(C * Leader[j] - X[i, j])
                        X[i, j] = Leader[j] - A * D_Leader
                elif p >= 0.5:
                    distance2Leader = np.abs(Leader[j] - X[i, j])
                    X[i, j] = distance2Leader * np.exp(b * l) * np.cos(l * 2 * math.pi) + Leader[j]

        X = updateCheck(X, pop, dim, cluster_result)
        fitness = CalculateFitness_Susp(X, dim, fun, dataset)
        fitness, sortIndex = SortFitnessDec(fitness)

        X = SortPosition(X, sortIndex)

        if fitness[0] >= GbestScore:
            GbestScore = copy.copy(fitness[0])
            GbestPosition[0, :] = copy.copy(X[0, :])
        Curve[t] = GbestScore

    return GbestScore, GbestPosition, Curve


if __name__ == "__main__":

    df_normalized_data = pd.read_csv('df_normalized_data_RM2.csv', index_col=0)      # ！！！！
    n_clusters, cluster_result = Kmeans.Kmeans(df_normalized_data)

    dataset = df_normalized_data.T

    for i in range(30):

        # 设置参数
        pop = 30
        MaxIter = 100
        dim = n_clusters

        fobj = fun
        GbestScore, GbestPosition, Curve = WOA(pop, dim, MaxIter, fobj, dataset, cluster_result)

        integer_formula = [int(value) for value in GbestPosition[0]]

        plt.clf()

        plt.figure(1)
        plt.plot(Curve, 'r-', linewidth=2)
        plt.xlabel('Iteration', fontsize='medium')
        plt.ylabel("Fitness", fontsize='medium')
        plt.rcParams['font.family'] = 'Times New Roman'
        plt.rcParams['axes.unicode_minus'] = False
        plt.grid()
        plt.title('KWOA', fontsize='large')
        figName = 'KWOA_RM2_{0}.png'.format(str(i+1))     # !!!!
        plt.savefig(figName, transparent=True)
        # plt.show()

        resultKWOA = r'D:\pythonProject\WOA_modelSpectrum\RM2(250)\KWOA\resultKWOA.txt'    # !!!!!
        with open(resultKWOA, 'a', encoding='utf-8') as file:
            file.write(str(i+1) + '\n')
            file.write('best fitness：'+str(GbestScore) + '\n')
            file.write('best solution：' + str(integer_formula) + '\n')
            file.write('\n')


