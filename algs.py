from PIL import Image, ImageFilter

import sys

argnum = len(sys.argv)

if(argnum > 1):
    imagepath = sys.argv[1]
else:
    print("NO PATH SPECIFIED! PLEASE SPECIFY A PATH AND TRY AGAIN\n")
    sys.exit()

im = Image.open(imagepath)
im = im.resize([int(im.width / 2), int(im.height / 2)])

im = im.convert('L')

#im = im.filter(ImageFilter.MedianFilter(5))
#im = im.filter(ImageFilter.SMOOTH_MORE)

def inbounds(x, y, width, height):
    return not (x >= width or x < 0 or y >= height or y < 0)
        

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
    
    pix = image.load()
    for y in range(0, image.height):
        for x in range(0, image.width):
            if((pix[x, y] / 4) > bayer8[x % 4][y % 4]): im2.putpixel([x, y], 255)
            else: im2.putpixel([x, y], 0)
    return im2

ic = [0, 0, 0]

def generalpurpose_dither(image, matrix, divisor):
    im2 = Image.new('L', image.size)
    error = [[0 for j in range(im.height)] for i in range(im.width)]
    
    pix = image.load()
    for y in range(0, image.height):
        for x in range(0, image.width):
            pe = pix[x, y] + error[x][y]
            p = 255 if (pe > 127) else 0
            
            err = pix[x, y] - p
            
            for i in range(len(matrix)):
                for j in range(len(matrix[0])):
                    xi = i + (x - 2)
                    yj = j + (y - 2)
                    
                    if inbounds(xi, yj, im.width, im.height):
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

def jjn_dither(image):
    matrix = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 7, 5],
        [3, 5, 7, 5, 3],
        [1, 3, 5, 3, 1]
    ]
    return generalpurpose_dither(image, matrix, 1.0 / 48)

def atkinson_dither(image):
    matrix = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0]
    ]
    return generalpurpose_dither(image, matrix, 1.0 / 8)

if(False):
    jjn_dither(im).show()
    atkinson_dither(im).show()
    bayer8_dither(im).show()
    floyd_stienburg(im).show()
    sierra_dither(im).show()

dxfimg = jjn_dither(im)
#dxfimg.show()

trans_matrix = [
    [-1, -1],
    [ 0, -1],
    [ 1, -1],
    [-1,  0]
]

import ezdxf
from ezdxf import colors

doc = ezdxf.new(dxfversion="R2010")

msp = doc.modelspace()

dxfimg = sierra_dither(im)
ps = dxfimg.load()
dxfimg.save("test.png")

scale = 3

points = []
lines = []
#example line:
__exline = ((0, 0), (1, 1), 3)

def findpoint(arr, p):
    x, y = p[0], p[1]
    i = 0
    while i < len(arr):
        #if(arr[i][0] >= x and arr[i][1] >= y): break
        if(arr[i][0] == x and arr[i][1] == y): return i
        i += 1
    return -1

def findendpoint(arr, p, dir):
    x, y = p[0], p[1]
    i = 0
    while i < len(arr):
        if arr[i][1][0] >= x and arr[i][1][1] >= y: break
        if(arr[i][1][0] == x and arr[i][1][1] == y and arr[i][2] == dir): return i
        i += 1
    return -1

for y in range(0, dxfimg.height):
    for x in range(0, dxfimg.width):
        if(ps[x, y] > 127):
            cont = False
            #do all lines first
            #for i, pos in enumerate(trans_matrix):
            #    pos = (pos[0] + x, pos[1] + y)
            #    if inbounds(pos[0], pos[1], dxfimg.width, dxfimg.height):
            #        ep = findendpoint(lines, pos, i)
            #        if ep != -1:
            #            lines[ep] = (lines[ep][0], (x, y), i)
            #            cont = True
            #if cont: continue        

            #do all points next (and generate new lines)
            #for i, pos in enumerate(trans_matrix):
            #    pos = (pos[0] + x, pos[1] + y)
            #    if inbounds(pos[0], pos[1], dxfimg.width, dxfimg.height):
            #        p = findpoint(points, pos)
            #        if p != -1:
            #            del points[p]
            #            lines.append((pos, (x, y), i))
            #            cont = True
            #if cont: continue

            points.append((x, y))

    print(str(y) + " out of " + str(dxfimg.height))
           
for point in points:
    x, y = point[0] * scale, (dxfimg.height - point[1]) * scale
    msp.add_line((x, y), (x, y), dxfattribs={"color": colors.WHITE})

for line in lines:
    x, y, x2, y2 = line[0][0] * scale, (dxfimg.height - line[0][1]) * scale, line[1][0] * scale, (dxfimg.height - line[1][1]) * scale
    msp.add_line((x, y), (x2, y2), dxfattribs={"color": colors.WHITE})

doc.saveas("test.dxf")