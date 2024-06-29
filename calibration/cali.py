import sys
import json
import os
import cv2
import numpy as np
import base64

def calibrate(image_folder, chessboard_size, square_size):
    chessboard_size = tuple(map(int, chessboard_size.split('x')))
    square_size = float(square_size)

    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
    objp = objp * square_size

    objpoints = []  
    imgpoints = []  

    images = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.endswith('.jpg') or f.endswith('.png')]

    processed_images = []

    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

        if ret:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
            imgpoints.append(corners2)

            img = cv2.drawChessboardCorners(img, chessboard_size, corners2, ret)
        
            _, buffer = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
        processed_images.append(img_base64)

    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


    result = {
        "camera_matrix": mtx.tolist(),
        "distortion_coefficients": dist.tolist(),
        "processed_images": processed_images
    }
    return result

if __name__ == "__main__":
    image_folder = sys.argv[1]
    chessboard_size = sys.argv[2]
    square_size = sys.argv[3]
    result = calibrate(image_folder, chessboard_size, square_size)
    debug = False
    if (debug):
        #show the images
        for img in result["processed_images"]:
            img = base64.b64decode(img)
            img = cv2.imdecode(np.frombuffer(img, np.uint8), -1)
            cv2.imshow("img", img)
            cv2.waitKey(0)
    print(json.dumps(result))