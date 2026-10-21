import pathlib as pt
import random as rn
import core
import cv2

model = core.tools_dir / "yunet.onnx"
detector = cv2.FaceDetectorYN.create(model, "", (320, 320), 0.5, 0.3, 5000)

if not model.is_file():
    raise Exception('Missing yunet.onnx')

def process(img, rotate=False):
    if img is None:
        print("Could not read")
        return None

    h, w = img.shape[:2]
    detector.setInputSize((w, h))
    faces = detector.detect(img)[1]
    
    if faces is None:
        print("No face found")
        return None
        
    x, y, fw, fh = max(faces, key=lambda f: f[2] * f[3])[:4]
    x, y, fw, fh = map(int, (x, y, fw, fh))
    pad_x = int(fw * 0.25)
    pad_y = int(fh * 0.25)
    left = max(0, x - pad_x)
    top = max(0, y - pad_y)
    right = min(w, x + fw + pad_x)
    bottom = min(h, y + fh + pad_y)
    crop = frame[top:bottom, left:right]
    
    if crop.size == 0:
        print("Invalid face crop")
        return None
        
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    equal = cv2.histEqualize(gray)
    resized = cv2.resize(equal, (224, 224), interpolation = cv2.INTER_AREA)
    
    if rotate:
        h, w = resized.shape[:2]
        angle = rn.randint(10, 15) * rn.choice([1, -1])
        rotation_matrix = cv.getRotationMatrix2D((w/2,h/2), angle, 1)
        face = cv.warpAffine(resized, rotation_matrix, (w, h))
    
    return face
