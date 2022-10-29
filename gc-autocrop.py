'''GC-Autocrop: Automatically crop a photo to a size of 600x600 pixels.'''

import cv2
from PIL import Image
import numpy as np
import sys, os


def detect_face(image):
    face_Cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    face = face_Cascade.detectMultiScale(image, scaleFactor = 1.3, minNeighbors = 5)
    return face


def lines_eyes(face):
    if len(face) < 1:
        raise Exception('Face not found.')
        
    # Horizontal line eyes
    hl = face[0][3] * 40.2 // 100 + face[0][1]

    # Vertical line eyes
    vl = face[0][2] // 2 + face[0][0]
    return int(hl), int(vl)


def main():
    path = sys.argv[-1]
    try:
        img = Image.open(path)
    except Exception:
        print('Photo not found.')

    fs = img.size

    if img.format != 'JPEG':
        raise Exception('Photo must be in JPEG (.jpg) format.')

    if img.mode != 'RGB':
        raise Exception('Photo must be in RGB color mode.')

    if fs[0] < 600 or fs[1] < 600:
        raise Exception('Photo must be 600x600 px or larger.')

    if fs[0] == 600 and fs[1] == 600:
        raise Exception ('This photo is already the correct size.')

    filename = path.split('.')[0]
    image = np.array(img)
    min_r = fs[1]*32.5 // 100
    max_r = fs[1]*42.5 // 100
    center = fs[0] // 2
    hl = lines_eyes(detect_face(image))[0]
    vl = lines_eyes(detect_face(image))[1]

    # Сroping the image the top and bottom so that the line of the eyes falls into the desired range.
    if hl < min_r:
        delta = int(fs[1] - hl * 100 / 32.5)
        box = (0, 0, fs[0], fs[1] - delta)
        img = img.crop(box)
        
    if hl > max_r:
        delta = int(fs[1]-((fs[1] - hl) * 100 / 57.5))
        box = (0, delta, fs[0], fs[1])
        img = img.crop(box)
        
    # Croping the image the left and right so that the face is centered.
    fs = img.size
    if vl > center and vl != center + 1:
        delta = vl - (fs[0] - vl)
        box = (delta, 0, fs[0], fs[1])
        img = img.crop(box)

    if vl < center:
        delta = fs[0] - vl * 2
        box = (0, 0, fs[0] - delta, fs[1])
        img = img.crop(box)
    
    # Making the image square.
    fs = img.size
    image = np.array(img)
    hl = lines_eyes(detect_face(image))[0]
    
    if fs[0] > fs[1]:
        delta = (fs[0] - fs[1]) / 2
        box = (delta, 0, fs[0] - delta, fs[1])
        img = img.crop(box)
    
    if fs[0] < fs[1]:
        hlp = round(hl * 100 / fs[1], 2)
        hl2 = int(fs[0] * hlp // 100)
        delta = hl - hl2
        box = (0, delta, fs[0], fs[0] + delta)
        img = img.crop(box)
    
    if img.size[0] < 600 or img.size[1] < 600:
        raise Exception('This photo cannot be properly cropped.')

    img = img.resize((600, 600))
    image = np.array(img)
    hl = lines_eyes(detect_face(image))[0]
    
    if hl < 190 or hl > 260:
        raise Exception('This photo cannot be properly cropped.')

    img.save(f'{filename}_cropped.jpg',
                format = 'JPEG',
                dpi=[300, 300],
                quality = 95,
                icc_profile = img.info.get('icc_profile',''))
    
    if os.stat(f'{filename}_cropped.jpg').st_size >= 240000:
        print('Warning! The cropped photo is larger than 240 kB.')
    

if __name__ == '__main__':
    main()