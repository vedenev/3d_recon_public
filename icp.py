import numpy as np
from sklearn.neighbors import NearestNeighbors
import constants
# got here: https://github.com/ClayFlannigan/icp/blob/master/icp.py


def best_fit_transform(A, B):
    '''
    Calculates the least-squares best-fit transform that maps corresponding points A to B in m spatial dimensions
    Input:
      A: Nxm numpy array of corresponding points
      B: Nxm numpy array of corresponding points
    Returns:
      R: mxm rotation matrix
      t: mx1 translation vector
    '''

    assert A.shape == B.shape

    # get number of dimensions
    m = A.shape[1]

    # translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
       Vt[m-1,:] *= -1
       R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    return R, t


def icp(xyz_1, xyz_2):
    neigh = NearestNeighbors(n_neighbors=1)
    neigh.fit(xyz_1.T)

    prev_error = 0

    for iteration_index in range(constants.ICP_MAX_INTERATION):

        distances, indices = neigh.kneighbors(xyz_2.T, return_distance=True)
        distances = distances.ravel()
        indices = indices.ravel()
        mean_error = np.mean(distances)
        condition = distances <= constants.ICP_DISTANCE_THRESHOLD
        xyz_2_paired = xyz_2[:, condition]
        indices = indices[condition]
        xyz_1_paired = xyz_1[:, indices]


        R, t = best_fit_transform(xyz_2_paired.T, xyz_1_paired.T)
        xyz_2 = np.matmul(R, xyz_2)
        xyz_2[0, :] += t[0]
        xyz_2[1, :] += t[1]
        xyz_2[2, :] += t[2]


        if np.abs(prev_error - mean_error) < constants.ICP_TOLERANCE:
            break
        prev_error = mean_error

    return xyz_2, mean_error

