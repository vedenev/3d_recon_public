import cv2
import numpy as np

def read_depth_file(file):
    file = str(file)
    depth = cv2.imread(file, cv2.IMREAD_ANYDEPTH)
    depth = depth.astype(np.float64)
    return depth

def write_ply(path, point_cloud, point_cloud_colors, thinning=1):
    if thinning != 1:
        point_cloud = point_cloud[:,::thinning]
        point_cloud_colors = point_cloud_colors[:, ::thinning]
    n_points = point_cloud.shape[1]
    file = open(path, 'w')
    file.write("ply\n")
    file.write("format ascii 1.0\n")
    file.write("element vertex " + str(n_points) + "\n")
    file.write("property float x\n")
    file.write("property float y\n")
    file.write("property float z\n")
    file.write("property uchar diffuse_red\n")
    file.write("property uchar diffuse_green\n")
    file.write("property uchar diffuse_blue\n")
    file.write("end_header\n")
    for point_index in range(n_points):
        point = point_cloud[:, point_index]
        color = point_cloud_colors[:, point_index]
        line = str(point[0]) + " " +\
               str(point[1]) + " " +\
               str(point[2]) + " " + \
               str(color[0]) + " " + \
               str(color[1]) + " " + \
               str(color[2]) + "\n"

        file.write(line)
    file.close()



