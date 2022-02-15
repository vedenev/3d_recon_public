from pathlib import Path
import constants
from input_output import read_depth_file, write_ply
import cv2
import numpy as np


def reconstruct(data_dir):
    """
    Reconstruct and save result to ./results
    :param data_dir:
    :return: None

    """

    u = np.arange(constants.WIDTH).astype(np.float64)
    v = np.arange(constants.HEIGHT).astype(np.float64)
    U, V = np.meshgrid(u, v)

    data_dir = Path(data_dir)

    log_path = data_dir / constants.LOG_BASENAME
    log = np.loadtxt(log_path)
    log_numbers = np.round(log[:, 0])
    log_numbers = log_numbers.astype(np.int64)
    log_numbers_enumerated = np.zeros((log_numbers.size, 2), np.int64)
    log_numbers_enumerated[:, 0] = log_numbers
    log_numbers_enumerated[:, 1] = np.arange(log_numbers.size)
    log_numbers_dict = dict(log_numbers_enumerated)

    files = data_dir.glob(constants.DEPTH_PATTERN)
    files = sorted(files)
    for file_index in range(len(files)):
        file = files[file_index]

        print("frame:", file_index, "of", len(files) - 1, file)

        depth = read_depth_file(file)

        mask = (constants.DEPTH_THRESHOLD_MIN <= depth) &\
               (depth <= constants.DEPTH_THRESHOLD_MAX)

        index_number = file.stem.find('-')
        number_str = file.stem[index_number + 1: ]
        number = int(number_str)
        file_stem_rgb = constants.RGB_PREFIX + number_str
        file_rgb = data_dir / file_stem_rgb
        file_rgb = file_rgb.with_suffix('.png')
        image = cv2.imread(str(file_rgb))
        R = image[:, :, 2]
        G = image[:, :, 1]
        B = image[:, :, 0]

        Z = depth
        X = Z * (U - constants.CX) / constants.FX
        Y = Z * (V - constants.CY) / constants.FY

        x = X[mask]
        y = Y[mask]
        z = Z[mask]

        r = R[mask]
        g = G[mask]
        b = B[mask]

        log_index = log_numbers_dict[number]

        record = log[log_index, 1: ]
        position = record[1: 4]
        position = position * 1000.0
        orientation = record[4: 7]
        rotation_matrix, _ = cv2.Rodrigues(orientation)

        xyz = np.zeros((3, x.size))
        xyz[0, :] = x
        xyz[1, :] = y
        xyz[2, :] = z
        xyz = np.matmul(rotation_matrix, xyz)

        xyz[0, :] += position[0]
        xyz[1, :] += position[1]
        xyz[2, :] += position[2]

        rgb = np.zeros((3, r.size), np.uint8)
        rgb[0, :] = r
        rgb[1, :] = g
        rgb[2, :] = b

        write_ply(constants.RESULT_DIR + '/' + number_str + '.ply', xyz, rgb)
