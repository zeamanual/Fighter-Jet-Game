# a fighter jet game basic implementation with 2d graphics using OpenGL API library

from matplotlib.pyplot import sca
import pygame
from sympy import N
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

import numpy as np

plane_vertices=[
(162,-4),
(174,-29),
(177,-89),
(192,-130),
(193,-159),
(229,-174),
(231,-188),
(291,-232),
(298,-265),
(199,-238),
(197,-258),
(234,-300),
(232,-317),
(194,-300),
(193,-288),
(184,-283),
(186,-300),
(172,-300),
(165,-287),
(155,-285),
(150,-302),
(135,-301),
(137,-285),
(127,-288),
(126,-298),
(91,-316),
(87,-301),
(122,-260),
(121,-240),
(21,-267),
(29,-233),
(89,-189),
(96,-171),
(129,-163),
(129,-132),
(145,-89),
(150,-27)]



def init():
    pygame.init()
    display = (700, 600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    # gluOrtho2D(-1.0, 1.0, -1.0, 1.0)

def border():

   
    glColor3f(1,0,0)
    # glLineWidth(10)
    glBegin(GL_LINES)

    
    glVertex2fv((-1,1))    
    glVertex2fv((1,1)) 
    glVertex2fv((-1,-1))    
    glVertex2fv((1,-1))
 

    glVertex2fv((-1,1))    
    glVertex2fv((-1,-1)) 
    glVertex2fv((1,-1))    
    glVertex2fv((1,1))
    glEnd()

# this function will draw a line with a provided rotation and translation value
def draw_line(initial_point,direction_vector,rotation=0,translation=(0,0)):
    matrix = rotationMatrix(rotation)
    range =np.arange(0,1.1,0.1)
    glLineWidth(2)
    glBegin(GL_LINE_STRIP)
    for i in range:
        temp = np.array([i,i])
        result = np.multiply(direction_vector,temp)
        result = np.add(result,initial_point)

        #applying rotation
        result = np.dot(matrix,np.array( [ [ result[0] ],[result[1]] ]))
        
        #applying translation
        result[0]=result[0]+translation[0]
        result[1]=result[1]+translation[1]

        glVertex2f(result[0],result[1])
    glEnd()


def draw_firing_plane():
    pass

def draw_shappe(vertices,scale=(1,1),rotation=0,transformation=(0,0)):
    vertices= np.array(vertices)
    vertices=np.multiply(vertices,scale)
    vertices = np.add(vertices,transformation)
    rotation_mat= rotationMatrix(rotation)
    glLineWidth(2)
    glBegin(GL_POLYGON)
    glColor(1,0,1)

    for vertice in vertices:
        vertice=np.dot(rotation_mat,np.array([ [vertice[0]],[vertice[1]] ]))
        glVertex2fv(vertice)

    glEnd()
    # print(vertices)


def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        [np.cos(radian), -np.sin(radian)],
        [np.sin(radian), np.cos(radian)],
    ])
    return mat

def draw():
    glClear(GL_COLOR_BUFFER_BIT)
    x_y_plane()
    glFlush()

# print(input)
def main():
    init()
    glClearColor(1,1,1,1)
    glClear(GL_COLOR_BUFFER_BIT)
    # glScalef(0.5,0.5,1)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        # draw()
        border()
        input = []
        input.extend(plane_vertices[:3])
        input.extend(plane_vertices[-2:])
        draw_shappe(input,scale=(0.004,0.004),transformation=(-0.5,0.5))
        input = []
        input.extend(plane_vertices[2:5])
        input.extend(plane_vertices[-4:])
        draw_shappe(input,scale=(0.004,0.004),transformation=(-0.5,0.5))
        input = []
        input.extend(plane_vertices[4:8])
        input.extend(plane_vertices[-7:-3])
        draw_shappe(input,scale=(0.004,0.004),transformation=(-0.5,0.5))
        input = []
        input.extend(plane_vertices[7:-12])
        # input.extend(plane_vertices[-7:-3])
        draw_shappe(input,scale=(0.004,0.004),transformation=(-0.5,0.5))   
        pygame.display.flip()
        pygame.time.wait(10)

main()

