import cv2
import numpy as np
from PIL import Image

# Using OpenCV Haar cascade for face detection (works offline)
# This method performs a simple swap: it finds the largest face in each image,
# resizes the source face to the target face size, and blends using seamlessClone.

cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def _detect_face_bbox(img_gray):
    faces = cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    # return the largest face
    faces = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
    x, y, w, h = faces[0]
    return (x, y, w, h)


def perform_face_swap(base_path: str, selfie_path: str, output_path: str):
    # read images
    base = cv2.imread(base_path, cv2.IMREAD_COLOR)
    selfie = cv2.imread(selfie_path, cv2.IMREAD_COLOR)
    if base is None or selfie is None:
        raise Exception("Failed to read one or both images")

    base_gray = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
    selfie_gray = cv2.cvtColor(selfie, cv2.COLOR_BGR2GRAY)

    base_bbox = _detect_face_bbox(base_gray)
    selfie_bbox = _detect_face_bbox(selfie_gray)

    if base_bbox is None:
        raise Exception("no_face_detected_in_base")
    if selfie_bbox is None:
        raise Exception("no_face_detected_in_selfie")

    bx, by, bw, bh = base_bbox
    sx, sy, sw, sh = selfie_bbox

    # Crop face from selfie
    face_src = selfie[sy:sy+sh, sx:sx+sw]
    # Resize source face to target face size
    face_src_resized = cv2.resize(face_src, (bw, bh))

    # Create mask for seamlessClone
    mask = 255 * np.ones(face_src_resized.shape[:2], face_src_resized.dtype)

    # center point where to clone on base image
    center = (bx + bw // 2, by + bh // 2)

    # Region on base where we'll place the face
    # First, create a temporary image that contains the face in correct position
    temp = base.copy()
    temp[by:by+bh, bx:bx+bw] = face_src_resized

    # Use seamlessClone to blend
    output = cv2.seamlessClone(face_src_resized, base, mask, center, cv2.NORMAL_CLONE)

    # Save output as PNG
    cv2.imwrite(output_path, output)

