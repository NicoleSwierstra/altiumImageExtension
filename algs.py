from PIL import Image, ImageFilter
im = Image.open("caroline.jpg")
im = im.resize([int(im.width / 4), int(im.height / 4)])

im = im.convert('L')

im = im.filter(ImageFilter.MedianFilter(5))
im = im.filter(ImageFilter.SMOOTH_MORE)
        

def bayer4_dither(image):
    im2 = Image.new('L', im.size)
    
    bayer4 = [[  1,  9, 13, 11],
              [ 13,  5, 15,  7],
              [  4, 12,  2, 10],
              [ 16,  8, 14,  6]]
    
    pix = im.load()
    for y in range(0, im.height):
        for x in range(0, im.width):
            if((pix[x, y] / 16) > bayer4[x % 4][y % 4]): im2.putpixel([x, y], 255)
            else: im2.putpixel([x, y], 0)
    return im2

def bayer8_dither(image):
    im2 = Image.new('L', im.size)
    
    bayer8 = [[ 0, 32,  8, 40,  2, 34, 10, 42],
              [48, 16, 56, 24, 50, 18, 58, 26],
              [12, 44,  4, 36, 14, 46,  6, 38],
              [60, 28, 52, 20, 62, 30, 54, 22],
              [ 3, 35, 11, 43,  1, 33,  9, 41],
              [51, 19, 59, 27, 49, 17, 57, 25],
              [15, 47,  7, 39, 13, 45,  5, 37],
              [63, 31, 55, 23, 61, 29, 53, 21]]
    
    pix = im.load()
    for y in range(0, im.height):
        for x in range(0, im.width):
            if((pix[x, y] / 4) > bayer8[x % 4][y % 4]): im2.putpixel([x, y], 255)
            else: im2.putpixel([x, y], 0)
    return im2

ic = [0, 0, 0]

def generalpurpose_dither(image, matrix, divisor):
    im2 = Image.new('L', im.size)
    error = [[0 for j in range(im.height)] for i in range(im.width)]
    
    pix = im.load()
    for y in range(0, im.height):
        for x in range(0, im.width):
            pe = pix[x, y] + error[x][y]
            p = 255 if (pe > 127) else 0
            
            err = pix[x, y] - p
            
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    xi = i + (x - 2)
                    yj = j + (y - 2)
                    
                    if not(xi >= im.width or xi < 0 or yj >= im.height or yj < 0):
                        error[xi][yj] += int(err * divisor * matrix[i][j])
                        #print(error[xi][yj])
            
            im2.putpixel([x, y], p)
            #print(p)
    
    return im2

def floyd_stienburg(image):
    matrix = [
        [1, 2, 4, 2, 1],
        [2, 4, 8, 4, 2],
        [4, 8, 0, 8, 4],
        [2, 4, 8, 4, 2],
        [1, 2, 4, 2, 1]
    ]
    return generalpurpose_dither(image, matrix, 1.0/42)

def sierra_dither(image):
    matrix = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 5, 3],
        [2, 4, 5, 4, 2],
        [0, 2, 3, 2, 0]
    ]
    return generalpurpose_dither(image, matrix, 1.0 / 32)


dxfimg = sierra_dither(im)

import ezdxf
from ezdxf import colors

doc = ezdxf.new(dxfversion="R2010")

msp = doc.modelspace()

dxfimg = sierra_dither(im)
ps = dxfimg.load()

scale = 3

for y in range(0, dxfimg.height):
    for x in range(0, dxfimg.width):
        if(ps[x, y] > 127):
            msp.add_point((x * scale, dxfimg.height - y * scale), dxfattribs={"color": colors.WHITE, "lineweight": 20})

doc.saveas("test.dxf")