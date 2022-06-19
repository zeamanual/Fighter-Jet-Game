import time
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import compileProgram,compileShader
import numpy as np
import random
from pygame.locals import *

class Game:
    def __init__(self):

        #initialise pygame
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
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

        #initial opengl setup
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #setting up game textures and images
        self.texture_shader = self.createShader("TextureShader/vertex.shader", "TextureShader/fragment.shader")
        self.bg_texture = Texture('assets/images/space2.jpg')
        self.bullet_texture= Texture('assets/images/rocket.png')
        self.fighter_plane_texture = Texture("assets/images/fighterJet.png")
        self.enemy_plane_texture = Texture("assets/images/enemy plane.png")
        self.bg = Background()

        #creating initial game objects
        self.fighter = FighterPlane(scale=0.6)
        self.enemies = []
        self.create_additional_enemies(1)
        self.bullets=[]
        self.create_additional_bullets(self.fighter,1)
        self.start_game()

    def create_additional_enemies(self,speed):
            enemy = EnemyPlane(scale=0.6,speed=speed)
            x_coordinates= [-0.8,-0.4,-0.1,0.2,0.8]
            rand = random.randint(0,len(x_coordinates)-1)
            enemy.transform(translate=(x_coordinates[rand],0))
            self.enemies.append(enemy)

    def create_additional_bullets(self,fighter,speed):
            bullet = Bullet((fighter.vertice[(3*8)]+fighter.vertice[5*8])/2,fighter.vertice[(3*8)+1]-0.1,speed)
            self.bullets.append(bullet)

    def createShader(self, vertexFilepath, fragmentFilepath):
        with open(vertexFilepath,'r') as file:
            vertex_src = file.readlines()
        with open(fragmentFilepath,'r') as file:
            fragment_src = file.readlines()
        shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER),
                                compileShader(fragment_src, GL_FRAGMENT_SHADER))
        return shader

    def start_game(self):
        running = True
        start_time = time.time()
        self.speed =1
        initial_level_time=time.time()
        initial_time_for_bullet= time.time()
        vertical_movt=0
        horizontal_movt=0
        while (running):
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

            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.texture_shader)

            #setting up background
            self.bg_texture.use()
            glBindVertexArray(self.bg.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.bg.vertex_count)

            #using fighter plane texture
            self.fighter_plane_texture.use()
            glBindVertexArray(self.fighter.vao)
            self.fighter.transform(translate=(horizontal_movt,vertical_movt))
            glDrawArrays(GL_TRIANGLES, 0, self.fighter.vertex_count)
            
           #drawing bullet
            self.bullet_texture.use()
            for bullet in self.bullets:
                glBindVertexArray(bullet.vao)
                glDrawArrays(GL_TRIANGLES, 0, bullet.vertex_count)
                bullet.update()

            #drawing enemy planes
            self.enemy_plane_texture.use()
            for enemy in self.enemies:
                glBindVertexArray(enemy.vao)
                glDrawArrays(GL_TRIANGLES, 0, enemy.vertex_count)
                enemy.update(self)
            
            pg.display.flip()
            end_time=time.time()

            #creating additional enemies
            if(end_time-start_time > (1.8-self.speed*0.2) ):
                self.create_additional_enemies(self.speed)
                start_time=time.time()

            #adjusting game speed
            if(end_time-initial_level_time > 5):
                initial_level_time=time.time()
                self.speed+=0.1
                self.level_up_sound.play()
                self.level_up_sound.set_volume(100)

            #creating additional bullets 
            if(end_time-initial_time_for_bullet > (1-0.2*(self.speed))):
                initial_time_for_bullet=time.time()
                self.create_additional_bullets(self.fighter,self.speed)

            #checking if game is over
            if(self.lost):
                running=False
                promp_screen(self)

            self.clock.tick(60)
        self.quit()


class FighterPlane:
    def __init__(self,scale=1):
        # x, y, z, r, g, b, s, t
        self.vertice=  [
            -0.5,-0.5,0,   0,0,1,  0,1,
            0.5,-0.5,0,    0,1,0,  1,1,
            -0.5,0.5,0,    1,0,0,  0,0,

            -0.5,0.5,0,    1,0,0,  0,0,
            0.5,-0.5,0,    0,1,0,  1,1,
            0.5,0.5,0,     0,1,0,  1,0
        ]
       
        self.scale = scale
        self.vertices = np.array(self.vertice, dtype=np.float32)
        self.vertex_count = len(self.vertice)//8

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
        self.transform(scale=(self.scale*0.5,self.scale*0.8))
        self.transform(translate=(0,-0.7))

    def transform(self,translate=(0,0),scale=(1,1)):
        x,y = translate
        sx,sy=scale
        if(self.vertice[0] < -1):
            if(x<0):
                x=0
        if(self.vertice[1*8] > 1):
            if(x>0):
                x=0
        if(self.vertice[1] < -1):
            if(y<0):
                y=0
        if(self.vertice[3*8+1] > 1):
            if(y>0):
                y=0
        
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%8
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
                temp = (i)%8
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


class EnemyPlane:
    def __init__(self,speed=1,scale=1):
         # x, y, z, r, g, b, s, t
        self.vertice= [
            -0.5,-0.5,0,   0,0,1,  0,1,
            0.5,-0.5,0,    0,1,0,  1,1,
            -0.5,0.5,0,    1,0,0,  0,0,

            -0.5,0.5,0,    1,0,0,  0,0,
            0.5,-0.5,0,    0,1,0,  1,1,
            0.5,0.5,0,     0,1,0,  1,0
        ]
        self.scale = scale
        self.speed = speed
        self.vertices = np.array(self.vertice, dtype=np.float32)
        self.vertex_count = len(self.vertice)//8
     
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
        self.rotate(180)
        self.transform(scale=(self.scale*0.5,self.scale*0.7))
        self.transform(translate=(0,1))

    def transform(self,translate=(0,0),scale=(1,1)):
        x,y = translate
        sx,sy=scale
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%8
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
                temp = (i)%8
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
            if(
                ( bullet.vertice[(4)*8] <= self.vertice[(0)*8] and  bullet.vertice[(4)*8] >= self.vertice[(1)*8]   )
             and
              ( bullet.vertice[(4)*8+1] <= self.vertice[0+1] and  bullet.vertice[(4)*8+1] >= self.vertice[(3)*8+1] +0.1   )
              ):
                game.bullets.remove(bullet)
                game.enemies.remove(self)
                game.score+=1
                game.explosion_sound.play()
            else:
                if(bullet.vertice[(0)*8+1] >=1):

                    game.bullets.remove(bullet)
                if(self.vertice[(5)*8+1] < -1.4 and self in game.enemies):
                    print("i am about to be deleted")
                    print(self.vertice[5*8+1])
                    game.enemies.remove(self)
                    game.lost=True


class Bullet:
    def __init__(self,x,y,speed):
         # x, y, z, r, g, b, s, t
        self.vertice=  [
            x-0.05,y,    0,    0,0,1,    0,1,
            x+0.05,y,    0,    0,1,0,    1,1,
            x+0.05,y+0.2,0,    0,1,1,     1,0,

            x-0.05,y,    0,    0,0,1,     0,1,
            x-0.05,y+0.2, 0,   1,1,0,     0,0,
            x+0.05,y+0.2, 0,   0,1,1,    1,0
        ]
        self.speed = speed
        self.vertices = np.array(self.vertice, dtype=np.float32)
        self.vertex_count = len(self.vertice)//8

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))

    def transform(self,translate=(0,0),scale=(1,1)):
        x,y = translate
        sx,sy=scale
        for i in range(len(self.vertice)):
            if(i>= 5):
                temp = (i)%8
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


class Texture:
    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        image = pg.image.load(filepath).convert_alpha()
        image_width,image_height = image.get_rect().size
        img_data = pg.image.tostring(image,'RGBA')
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self):
        glBindTexture(GL_TEXTURE_2D,self.texture)


class Background:
    def __init__(self):
         # x, y, z, r, g, b, s, t
        self.vertice=  [
            -1,-1,0,   0,0,1,  0,1,
            1,-1,0,    0,1,0,  1,1,
            -1,1,0,    1,0,0,  0,0,

            -1,1,0,    1,0,0,  0,0,
            1,-1,0,    0,1,0,  1,1,
            1,1,0,     0,1,0,  1,0
        ]
       
        self.vertices = np.array(self.vertice, dtype=np.float32)
        self.vertex_count = len(self.vertice)//8
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))


def rotationMatrix(degree):
    radian = degree * np.pi / 180.0
    mat = np.array([
        np.cos(radian), -np.sin(radian),
        np.sin(radian), np.cos(radian),
    ])
    return mat

def draw_text(text,x,y,size=30):
    font = pg.font.SysFont('arial', size)
    textSurface = font.render(text, True, (255,255,255, 255), (25.5, 51, 51, 255))
    textData = pg.image.tostring(textSurface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def promp_screen(game):
    pg.init()
    clock = pg.time.Clock()
    display = (645, 480)
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
                    Game()
                if event.key == pg.K_q:
                    pg.quit()
                    exit()

        glClearColor(0.1, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_text( "Game Over",220, 320)
        draw_text( f"Score : {game.score}",220, 290)
        draw_text("Press :",160, 210,size=20)
        draw_text("Space To Play Again",220, 190,size=20)
        draw_text("q To Quit The Game",220, 160,size=20)
        pg.display.flip()

    pg.quit()
    exit()

def start_screen():
    pg.init()
    clock = pg.time.Clock()
    display = (640, 480)
    dis = pg.display.set_mode(display, DOUBLEBUF | OPENGL)
    # background_image = pg.image.load("assets/images/space2.bmp").convert()
    run = True
    while run:
        clock.tick(100)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    Game()
                if event.key == pg.K_q:
                    pg.quit()
                    exit()

        glClearColor(0.1, 0.2, 0.2, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        draw_text( "Welcome To The Fighter Jet Game",30, 220,size=45)
        draw_text( "Press Space Bar To Start The Game",120, 160)
        pg.display.flip()

    pg.quit()
    exit()

def start():
    start_screen()

start()