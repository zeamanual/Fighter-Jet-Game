import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import planeVertex
import random
from pygame.locals import *

class App:
    def __init__(self):
        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        # pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK,
                                    pg.GL_CONTEXT_PROFILE_CORE)
        display= (640,480)
        self.screen = pg.display.set_mode(display, OPENGL| DOUBLEBUF)
        self.clock = pg.time.Clock()

        #setting up game sound
        pg.mixer.init()
        self.explosion_sound=pg.mixer.Sound('assets/sounds/explosion.wav')
        self.level_up_sound=pg.mixer.Sound('assets/sounds/levelUp.mp3')
        self.background_sound = pg.mixer.Sound('assets/sounds/bg.mp3')
        self.background_sound.play()
        self.score=0
        self.lost=False

        #initialise opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


        self.shader = self.createShader("shaders2/vertex.txt", "shaders2/fragment.txt")
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)
    
        self.fighter = FighterPlane(scale=0.7)
        self.enemies = []
        self.create_additional_enemies(1)

        self.bullets=[]
        self.create_additional_bullets(self.fighter,1)

        self.mainLoop()
    def create_additional_enemies(self,speed):
            enemy = EnemyPlane(scale=0.7,speed=speed)
            x_coordinates= [-0.4,-0.1,0.2,0.6,1]
            rand = random.randint(0,len(x_coordinates)-1)
            enemy.transform(translate=(x_coordinates[rand],0))
            self.enemies.append(enemy)
    def create_additional_bullets(self,fighter,speed):
            bullet = Bullet(fighter.vertice[0],fighter.vertice[1],speed)
            self.bullets.append(bullet)


    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath,'r') as f:
            vertex_src = f.readlines()

        with open(fragmentFilepath,'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        
        return shader

    def mainLoop(self):
        running = True
        # self.enemy.transform(translate=(-0.4,0))
        start_time = time.time()
        self.speed =1
        initial_level_time=time.time()
        initial_time_for_bullet= time.time()
        vertical_movt=0
        horizontal_movt=0
        while (running):
            #check events
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                    promp_screen(self)
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_LEFT:
                      horizontal_movt=-0.015
                    if event.key == pg.K_RIGHT:
                        horizontal_movt=0.015
                    if event.key == pg.K_UP:
                        vertical_movt=0.015
                    if event.key == pg.K_DOWN:
                        vertical_movt=-0.015
                if event.type == pg.KEYUP:
                    if event.key == pg.K_LEFT:
                        horizontal_movt=-0
                    if event.key == pg.K_RIGHT:
                        horizontal_movt=0
                    if event.key == pg.K_UP:
                        vertical_movt=0
                    if event.key == pg.K_DOWN:
                        vertical_movt=-0
            #refresh screen
            glClear(GL_COLOR_BUFFER_BIT)

            glUseProgram(self.shader)
            # self.texture.use()
            # self.secondTexture.use()
            # self.fighter.transform(scale=(1,0.99))
            
            glBindVertexArray(self.fighter.vao)
            self.fighter.transform(translate=(horizontal_movt,vertical_movt))
            glDrawArrays(GL_LINE_LOOP, 0, self.fighter.vertex_count)
         

            for enemy in self.enemies:
                glBindVertexArray(enemy.vao)
                glDrawArrays(GL_LINE_LOOP, 0, enemy.vertex_count)
                enemy.update(self)


            for bullet in self.bullets:
                glBindVertexArray(bullet.vao)
                glDrawArrays(GL_TRIANGLES, 0, bullet.vertex_count)
                bullet.update()


            pg.display.flip()
            end_time=time.time()
            if(end_time-start_time > 1.8 ):
                self.create_additional_enemies(self.speed)
                start_time=time.time()

            if(end_time-initial_level_time > 3):
                initial_level_time=time.time()
                self.speed+=0.1
                self.level_up_sound.play()

            if(end_time-initial_time_for_bullet > 1):
                initial_time_for_bullet=time.time()
                self.create_additional_bullets(self.fighter,self.speed)


            if(self.lost):
                running=False
                promp_screen(self)

            self.clock.tick(60)
        self.quit()

    def quit(self):
        # self.shape.destroy()
        # self.texture.destroy()
        glDeleteProgram(self.shader)
        pg.quit()


class FighterPlane:
    def __init__(self,scale=1):
        # x, y, , r, g, b, s, t
  
        self.vertice=  planeVertex.vertice.copy()
       
        self.scale = scale
        self.vertices = np.array(self.vertice, dtype=np.float32)

        self.vertex_count = len(self.vertice)//5

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        self.transform(scale=(self.scale*0.002,self.scale*0.002))

    def track_mouse(self, x_pos,y_pos):
        x_translate = x_pos-self.vertice[0]
        y_translate= y_pos-self.vertice[1]
        self.transform(translate=(x_translate,y_translate))

    def transform(self,translate=(0,0),scale=(1,1)):

        x,y = translate
        sx,sy=scale
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy

    
        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)


    def rotate(self,theta):
        prv_x = None
        prv_y = None
        rotation_mat = rotationMatrix(theta)
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )


        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))


def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        np.cos(radian), -np.sin(radian),
        np.sin(radian), np.cos(radian),
    ])
    return mat
class EnemyPlane:
    def __init__(self,speed=1,scale=1):
        # x, y, , r, g, b, s, t
  
        self.vertice= planeVertex.vertice.copy()
        self.scale = scale
        self.speed = speed
        self.vertices = np.array(self.vertice, dtype=np.float32)

        self.vertex_count = len(self.vertice)//5
     
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))

        self.rotate(180)
        self.transform(scale=(self.scale*0.002,self.scale*0.002))
        self.transform(translate=(0,1))

    def transform(self,translate=(0,0),scale=(1,1)):

        x,y = translate
        sx,sy=scale
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy


        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)


    def rotate(self,theta):
        prv_x = None
        prv_y = None
        rotation_mat = rotationMatrix(theta)
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )


        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
    
    def update(self,game):
        self.transform(translate=(0,self.speed*-0.005))
        for bullet in game.bullets:
            # print("start -----------")
            # print(bullet.vertice[(4-1)*5])
            # print(self.vertice[(29-1)*5])
            # print("end -----------")
            if(
                ( bullet.vertice[(4-1)*5] >= self.vertice[(8-1)*5] and  bullet.vertice[(4-1)*5] <= self.vertice[(29-1)*5]   )
             and
              ( bullet.vertice[(4-1)*5+1] >= self.vertice[0+1] and  bullet.vertice[(4-1)*5+1] <= self.vertice[(20-1)*5+1]   )
              ):
                game.bullets.remove(bullet)
                game.enemies.remove(self)
                game.score+=1
                game.explosion_sound.play()
            else:
                if(bullet.vertice[(4-1)*5+1] >=1):
                    game.bullets.remove(bullet)
                if(self.vertice[(20-1)*5+1] < -1 and self in game.enemies):
                    game.enemies.remove(self)
                    game.lost=True





    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))

def draw_text(text,x,y):
    font = pg.font.SysFont('arial', 30)
    textSurface = font.render(text, True, (152,251,152, 255), (25.5, 51, 51, 255))
    textData = pg.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)


class Bullet:
    def __init__(self,x,y,speed):
        # x, y, , r, g, b, s, t
  
        # self.vertice=  planeVertex.vertice.copy()
        self.vertice=  [
            x-0.025,y, 0,0,1,
            x+0.025,y,0,1,0,
            x+0.025,y+0.1,0,1,1,

            x-0.025,y, 0,0,1,
            x-0.025,y+0.1,1,1,0,
            x+0.025,y+0.1,0,1,1,

        ]
       
        self.speed = speed
        self.vertices = np.array(self.vertice, dtype=np.float32)

        self.vertex_count = len(self.vertice)//5

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))

    def transform(self,translate=(0,0),scale=(1,1)):

        x,y = translate
        sx,sy=scale
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        self.vertice[i]+=x
                        self.vertice[i]*=sx
                    else:
                        self.vertice[i]+=y
                        self.vertice[i]*=sy

    
        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def update(self):
        self.transform(translate=(0,self.speed*0.005))

    def rotate(self,theta):
        prv_x = None
        prv_y = None
        rotation_mat = rotationMatrix(theta)
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%5
                if(temp >=2):
                    continue
                else:
                    if(temp==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )
            else:
                if(i>=2):
                    continue
                else:
                    if(i==0):
                        prv_x=self.vertice[i]
                        self.vertice[i]=(self.vertice[i]*rotation_mat[0] + self.vertice[i+1]*rotation_mat[1] )
                    else:
                        self.vertice[i]=(prv_x*rotation_mat[2]+ self.vertice[i]*rotation_mat[3] )


        self.vertices = np.array(self.vertice, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1,(self.vbo,))


def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        np.cos(radian), -np.sin(radian),
        np.sin(radian), np.cos(radian),
    ])
    return mat

def start():
    myApp = App()

def promp_screen(game):
    pg.init()
    clock = pg.time.Clock()
    display = (400, 300)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)
    run = True

    while run:
        clock.tick(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    game.background_sound.fadeout(4000)
                    App()
                if event.key == pg.K_q:
                    pg.quit()
                    exit()


        glClearColor(0.1, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_text( "Game Over",120, 220)
        draw_text( f"Score : {game.score}",120, 190)
        draw_text("Press :",40, 120)
        draw_text("Space To Play Again",120, 80)
        draw_text("q To Quit The Game",120, 40)
        pg.display.flip()

    pg.quit()
    exit()

start()

