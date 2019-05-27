# Sebastián Galindo 15452
# Gráficas por computadora
# Código obtenido de http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
import sys
import copy
from Bitmap import *
from Lib import *
from object import *

screen = None
viewPort = {"x": 0, "y": 0, "width": 0, "heigth": 0}
blue = color(0, 0, 255)
red = color(255, 0, 0)
green = color(0, 255, 0)
colorStandard = 255
vertexBuffer = []
zBuffer = []
surface = Texture("PenguinTexture.bmp")

sign = lambda a: (a > 0) - (a < 0)

def glInit():
    pass


def glCreateWindow(width, heigth):
    global screen
    screen = Bitmap(width, heigth)


def glViewPort(x, y, width, heigth):
    global viewPort, zBuffer
    viewPort["x"] = x
    viewPort["y"] = y
    viewPort["width"] = width
    viewPort["heigth"] = heigth
    zBuffer = [[-999 for x in range(0, width+ 1)] for y in range(0, heigth + 1)]


def glClear():
    screen.clear()


def glClearColor(r, g, b):
    screen.color = color(r, g, b)


# Recibe parametros entre -1 y 1
def glVertex(x, y):
    global viewPort
    global screen
    newX = int((x + 1) * (viewPort["width"] / 2) + viewPort["x"])
    newY = int((y + 1) * (viewPort["heigth"] / 2) + viewPort["y"])
    screen.point(newX, newY, screen.currentColor)


def glColor(r, g, b):
    r = int(r * colorStandard)
    g = int(g * colorStandard)
    b = int(b * colorStandard)
    screen.currentColor = color(r, g, b)


def glLine(x0, y0, x1, y1):
    global viewPort
    global screen
    x0, y0 = normalize(x0, y0, viewPort)
    x1, y1 = normalize(x1, y1, viewPort)

    # Setup initial conditions
    dx = x1 - x0
    dy = y1 - y0

    # Determine how steep the line is
    is_steep = abs(dy) > abs(dx)

    # Rotate line
    if is_steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    # Swap start and end points if necessary and store swap state
    swapped = False
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        swapped = True

    # Recalculate differentials
    dx = x1 - x0
    dy = y1 - y0

    # Calculate error
    error = int(dx / 2.0)
    ystep = 1 if y0 < y1 else -1

    # Iterate over bounding box generating points between start and end
    y = y0
    points = []
    for x in range(x0, x1 + 1):
        coord = (y, x) if is_steep else (x, y)
        points.append(coord)
        error -= abs(dy)
        if error < 0:
            y += ystep
            error += dx

    # Reverse the list if the coordinates were swapped
    if swapped:
        points.reverse()

    for point in points:
        screen.point(point[0], point[1], screen.currentColor)


def glFinish():
    screen.write('out.bmp')


def glLoad(name, scale, translateX, translateY, translateZ):
    global screen, vertexBuffer
    model = Obj(name)
    for face in model.vfaces:
        vcount = len(face)
        for j in range(vcount):
            f1 = face[j][0] #vertex value
            t1 = face[j][1] #texture value
            v1 = copy.copy(model.vertices[f1 - 1])
            vt1 = copy.copy(model.vtextures[t1 - 1])
            # v1 = [(x * scale) + translateX for x in v1]
            v1[0] = (v1[0] * scale) + translateX
            v1[1] = (v1[1] * scale) + translateY
            v1[2] = (v1[2] * scale) + translateZ
            vertexBuffer.append(v1)
            vertexBuffer.append(vt1)
    vertexBuffer = iter(vertexBuffer)

def length(v0):
  return (v0[0]**2 + v0[1]**2 + v0[2]**2)**0.5

def norm(v0):
    v0length = length(v0)

    if not v0length:
        return [0, 0, 0]

    return [v0[0] / v0length,
            v0[1] / v0length,
            v0[2] / v0length]

def cross(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def dot(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def barycentric(A, B, C, P):
    v1 = [C[0] - A[0], B[0] - A[0], A[0] - P[0]]
    v2 = [C[1] - A[1], B[1] - A[1], A[1] - P[1]]

    b = cross(v1, v2)

    if(abs(b[2]) < 1):
        return -1, -1, -1

    return (1 - (b[0] + b[1]) / b[2], b[1] / b[2], b[0] / b[2])

def sub(v1, v2):
    return [v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]]

def getPixels(x, y):
    global viewPort
    newX = int((x + 1) * (viewPort["width"] / 2) + viewPort["x"])
    newY = int((y + 1) * (viewPort["heigth"] / 2) + viewPort["y"])
    return newX, newY

def glTriangle():
    global vertexBuffer, viewPort, zBuffer, surface
    A = next(vertexBuffer)
    tA = next(vertexBuffer)
    B = next(vertexBuffer)
    tB = next(vertexBuffer)
    C = next(vertexBuffer)
    tC = next(vertexBuffer)

    light = [0,0,1]
    normal = norm(cross(sub(B, A), sub(C, A))) #Falta el norm
    intensity = dot(light, normal)

    minX = round(min(A[0], B[0], C[0]))
    minY = round(min(A[1], B[1], C[1]))
    maxX = round(max(A[0], B[0], C[0]))
    maxY = round(max(A[1], B[1], C[1]))

    for x in range(minX, maxX + 1):
        for y in range(minY, maxY + 1):
            w, v, u = barycentric(A, B, C, [x, y])
            if u >= 0 and v >= 0 and w >= 0:
                z = w * A[2] + v * B[2] + u * C[2]
                tx = float(tA[0]) * float(w) + float(tB[0]) * float(v) + float(tC[0]) * float(u)
                ty = float(tA[1]) * float(w) + float(tB[1]) * float(v) + float(tC[1]) * float(u)
                surface_color = surface.get_color(tx, ty, intensity)
                if 0 < x < viewPort["width"] and  0 < y < viewPort["heigth"] and zBuffer[y][x] < z:
                    screen.point(x, y, surface_color)
                    zBuffer[y][x] = z
            #algoritmo para cambiar color del punto dependiendo de la direccion de la luz

def glDraw():
    while True:
        try:
            glTriangle()
        except StopIteration:
            break
