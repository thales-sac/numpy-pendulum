from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

import argparse
import numpy as np
import math


class NewtonCradle():
    
    def __init__(self):
        self.textureId = None

        ###CONSTANTES
        self.quadratic = None   #Necesario para desenhar cilindros con glu
        #GLuint _textureId          #The OpenGL id of the texture
        #textureId = glGenTextures(1)

        self.milisegundos = 20      #Tempo para cada atualização da tela
        self.angulomax = 50       #Valor máximo para o ângulo do pêndulo
        self.incrementomax = 6.5  #Valor máximo para os incrementos do ângulo
        self.angulo = -self.angulomax  #A esfera mais a esquerda começa suspensa pelo maior ângulo
        self.clockwise = False     #Esfera tem transalação no sentido anti-horário 

        self.esferas = 5            #Quantidade de esferas
        self.is_moving = 1           #Quantidade de esferas em movimento
        self.esf_diam = 1.0       #Diâmetro de cada esfera
        self.cuboamarrar = 0.125   #Tamanho do cubo incrustado sobre cada esfera

        #Base                      #Tamanho da base
        self.base_tamX = 7.5
        self.base_tamY = 0.8
        self.base_tamZ = 5.5

        self.dist_esf_base = 1.0  #Distância entre as esferas e a base quando o ângulo é 0

        #Tubos
        self.tub_radio = 0.125    #Raio de cada cilindro
        self.slices = 32          #Quantidade de subdivisçies ao redor do eixo z para desenhar cada cilindro
        self.stacks = 32          #Quantidade de subdivisçies ao longo do eixo z para desenhar cada cilindro

        self.tub_tamX = 6.5       # Tamanhoo da haste retangular 
        self.tub_tamY = 5      # formada por tudos (incluindo
        self.tub_tamZ = 4.5       # o diâmetro de cada tubo)


        #A largura do fio se calcula com base no tamanho dos tubos, 
        # o diâmetro das esferas e a distancia entre as esferas e a base
        self.largura_fio = self.tub_tamY - self.tub_radio - self.dist_esf_base - self.esf_diam - self.cuboamarrar/2

        #Camara - define perspectiva padrão de visualização
        self.camposx = 0.0
        self.camposy = 0.5
        self.camposz = 15.0
        self.camrotx = 6.0
        self.camroty = 40.0
        self.camrotz = 0.0

        #Eixos
        self.drawAxes = False

    #Menus
    #static int menuPrincipal, menuTotalEsf, menuEnMovimiento

    def loadTexture(self, img):
        textureId = glGenTextures(1)
        img_data = np.array(list(img.getdata()), np.int8)
        glBindTexture(GL_TEXTURE_2D, textureId)  
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        self.textureId = textureId
        return textureId

    def initRendering(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        
        self.quadratic=gluNewQuadric()
        gluQuadricNormals(self.quadratic, GLU_SMOOTH)
        gluQuadricTexture(self.quadratic, GL_TRUE)
        
        #image = Image.open('madera.bmp')
        #self.textureId = self.loadTexture(image)
        return

    def posicionarCamara(self): 
        glTranslatef(-self.camposx, -self.camposy, -self.camposz)
        glRotatef(self.camrotx, 1.0, 0.0, 0.0)
        glRotatef(self.camroty, 0.0, 1.0, 0.0)
        glRotatef(self.camrotz, 0.0, 0.0, 1.0)

    def toDeg(self, radian):
        return radian*180/math.pi

    def toRad(self, degree): 
        return degree*math.pi/180


    def mediana(self, n):
        #Encontrar a posição central para una sequência de n números
        if(n%2 == 0):
            return n/2
        else:
            return (n+1)/2


    def defineAxes(self):
        #Eixo X - vermelho
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(-500.0,0.0,0.0)
        glVertex3f(500.0,0.0,0.0)
        glEnd()
        
        #Eixo Y - verde
        glColor3f(0.0, 1.0, 0.0)
        glBegin(GL_LINES)
        glVertex3f(0.0,-500.0,0.0)
        glVertex3f(0.0,500.0,0.0)
        glEnd()
        
        #Eixo Z - azul
        glColor3f(0.0, 0.0, 1.0)
        glBegin(GL_LINES)
        glVertex3f(0.0,0.0,-500.0)
        glVertex3f(0.0,0.0,500.0)
        glEnd()


    def drawBase(self): 
        glPushMatrix()
        glTranslatef(0.0, -(self.esf_diam/2 + self.dist_esf_base + self.base_tamY/2), 0.0) #Centro Geométrico de la Base
        
        glEnable(GL_TEXTURE_2D)
        #glBindTexture(GL_TEXTURE_2D, self.textureId)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        glColor3f(1.0,1.0,1.0)
        
        glBegin(GL_QUADS)
        #Cara Superior
        glNormal3f(0.0, 1.0, 0.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2) #Bottom Left of Texture & Plane
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2) # Bottom Right of Texture & Plane
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2) # Top Right of Texture & Plane
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2) # Top Left of Texture & Plane
        #Cara Inferior
        glNormal3f(0.0, -1.0, 0.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2)
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2)
        #Cara Izq
        glNormal3f(-1.0, 0.0, 0.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2)
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2)
        #Cara Der
        glNormal3f(-1.0, 0.0, 0.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2)
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2)
        #Cara Frontal
        glNormal3f(0.0, 0.0, 1.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2) 
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2)
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, self.base_tamZ/2)
        #Cara Posterior
        glNormal3f(0.0, 0.0, 1.0)
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(-self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2) 
        glTexCoord2f(1.0, 0.0) 
        glVertex3f(self.base_tamX/2, -self.base_tamY/2, -self.base_tamZ/2)
        glTexCoord2f(1.0, 1.0) 
        glVertex3f(self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2)
        glTexCoord2f(0.0, 1.0) 
        glVertex3f(-self.base_tamX/2, self.base_tamY/2, -self.base_tamZ/2)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)    
        glPopMatrix()

    def drawTubos(self): 
        glPushMatrix()
        glTranslatef(0.0, self.tub_tamY/2 - self.esf_diam/2 - self.dist_esf_base, 0.0) #Centro Geométrico
        
        glColor3f(0.069, 0.069, 0.069)
        
        #Iluminacao
        mat_ambient = [0.0, 0.0, 0.0, 0.0]
        mat_diffuse = [0.5, 0.5, 0.5, 1.0]    
        mat_specular =  [1.0, 1.0, 1.0, 1.0]
        mat_shininess = [300.0 ]
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        #glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)
        
        #Superior Dianteiro
        glPushMatrix()
        glTranslatef(-self.tub_tamX/2, self.tub_tamY/2-self.tub_radio, self.tub_tamZ/2-self.tub_radio)
        glRotatef(90.0, 0.0, 1.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamX,self.slices, self.stacks)
        glPopMatrix()
        
        #Superior Posterior
        glPushMatrix()
        glTranslatef(-self.tub_tamX/2, self.tub_tamY/2-self.tub_radio, -(self.tub_tamZ/2-self.tub_radio))
        glRotatef(90.0, 0.0, 1.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamX,self.slices, self.stacks)
        glPopMatrix()
        
        #Esquerdo Dianteiro
        glPushMatrix()
        glTranslatef(-(self.tub_tamX/2-self.tub_radio), self.tub_tamY/2-self.tub_radio, self.tub_tamZ/2-self.tub_radio)
        glRotatef(90.0, 1.0, 0.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamY-self.tub_radio,self.slices, self.stacks)
        glPopMatrix()
        
        #Esquerdo Posterior
        glPushMatrix()
        glTranslatef(-(self.tub_tamX/2-self.tub_radio), self.tub_tamY/2-self.tub_radio, -(self.tub_tamZ/2-self.tub_radio))
        glRotatef(90.0, 1.0, 0.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamY-self.tub_radio,self.slices, self.stacks)
        glPopMatrix()
        
        #Direito Dianteiro
        glPushMatrix()
        glTranslatef((self.tub_tamX/2-self.tub_radio), self.tub_tamY/2-self.tub_radio, self.tub_tamZ/2-self.tub_radio)
        glRotatef(90.0, 1.0, 0.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamY-self.tub_radio,self.slices, self.stacks)
        glPopMatrix()
        
        #Direito Posterior
        glPushMatrix()
        glTranslatef((self.tub_tamX/2-self.tub_radio), self.tub_tamY/2-self.tub_radio, -(self.tub_tamZ/2-self.tub_radio))
        glRotatef(90.0, 1.0, 0.0, 0.0)
        gluCylinder(self.quadratic,self.tub_radio,self.tub_radio,self.tub_tamY-self.tub_radio,self.slices, self.stacks)
        glPopMatrix()
        
        glPopMatrix()


    def esferaAmarrada(self, angulo):
        glPushMatrix()
        
        glRotatef(angulo, 0.0, 0.0, 1.0)
        glTranslatef(0.0, -self.largura_fio, 0.0)
        
        glColor3f(0.8, 0.8, 0.8)
        
        #Iluminação
        mat_ambient = [ 0.0, 0.0, 0.0, 0.0 ]
        mat_diffuse = [ 0.5, 0.5, 0.5, 1.0 ]
        mat_specular = [ 1.0, 1.0, 1.0, 1.0 ]
        mat_shininess = [ 300.0 ]
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
        #glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess) -- bug a corrigir
        
        #Desenhar Cubo Para Amarrar
        glutSolidCube(self.cuboamarrar)
        
        #Desenhar Esfera
        glPushMatrix()
        glTranslatef(0.0, -(self.esf_diam/2), 0.0)
        glutSolidSphere(self.esf_diam/2, 20, 20)
        glPopMatrix()
        
        glRotatef(-angulo, 0.0, 0.0, 1.0)
        
        #Desenhar fios
        distX = math.sin(self.toRad(angulo))*self.largura_fio
        distY = math.cos(self.toRad(angulo))*self.largura_fio
        distZ = self.tub_tamZ/2-self.tub_radio
        
        glColor3f(0.72, 0.54, 0.0)
        glBegin(GL_LINES)
        #Tubo posterior
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-distX, distY, -distZ)
        #Tubo frontal
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-distX, distY, distZ)
        glEnd()
        
        glPopMatrix()

    def drawEsferas(self): 
        glPushMatrix()
        glTranslatef(0.0, self.tub_tamY-self.tub_radio-self.dist_esf_base-self.esf_diam/2, 0.0) #Altura dos tubos
        
        for i in range(1, self.esferas+1):
            glPushMatrix()
            glTranslatef(-self.esferas/2.0-self.esf_diam/2.0+i*self.esf_diam,0.0,0.0) #Centro em X
            if(i<=self.is_moving and self.angulo<0):
                self.esferaAmarrada(self.angulo)
            elif (i>self.esferas-self.is_moving and self.angulo>0):
                self.esferaAmarrada(self.angulo)
            else:
                self.esferaAmarrada(0)
            glPopMatrix()
        

        glPopMatrix()


    def drawScene(self): 
        glClearColor(0.0,0.0,0.0,1.0) #COR DO FUNDO (preto)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        #Iluminacao
        ambientLight = [0.1, 0.1, 0.1, 1.0]
        diffuseLight = [1.0, 1.0, 1.0, 1.0]
        specularLight = [1.0, 1.0, 1.0, 1.0]
        lightPos = [-self.camposx+self.tub_tamX, -self.camposy+self.tub_tamY, -self.camposz+self.tub_tamZ, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, lightPos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambientLight)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuseLight)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specularLight)
        
        # Viewing 
        self.posicionarCamara()
        
        #Modeling 
        if(self.drawAxes):
            self.defineAxes()
        self.drawBase()
        self.drawTubos()
        self.drawEsferas()

        glutSwapBuffers()
        

    def update(self, value): 
        
        incremento = self.incrementomax-abs(self.angulo)/self.angulomax*self.incrementomax*0.85
        
        if(self.clockwise and self.angulo <=-self.angulomax):
            self.clockwise = False
        
        elif(not self.clockwise and self.angulo >= self.angulomax): 
            self.clockwise = True
        
        
        if(self.clockwise):
            self.angulo -= incremento
        else:
            self.angulo += incremento
            
        glutPostRedisplay()
        glutTimerFunc(self.milisegundos, self.update, 0)


    def handleSpecialKeys (self, key, x, y): 
        inc = 2.0
        
        if (key==GLUT_KEY_RIGHT):
            self.camroty += inc
            glutPostRedisplay()
        
        elif (key==GLUT_KEY_LEFT):
            self.camroty -= inc
            glutPostRedisplay()
        
        elif (key==GLUT_KEY_UP):
            self.camrotx -= inc 
            glutPostRedisplay()
        
        elif (key==GLUT_KEY_DOWN):
            self.camrotx += inc 
            glutPostRedisplay()
        
        
    def handleResize(self, w, h): 
        #Projection 
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(w) / float(h), 1.0, 200.0)
        
        # ViewPort 
        glViewport(0, 0, w, h)


    def handleMenuPrincipal(self, m):
        
        if (m==0):
            exit(0)
        elif (m==1):
            self.drawAxes =  not self.drawAxes
        

    def handleMenuTotalEsf(self, m):
        self.esferas = m-10
        glutPostRedisplay()


    def handleMenuEmMovimiento(self, m):
        self.is_moving = m-20
        glutPostRedisplay()


    def prepararMenu(self): 
        menuTotalEsf = glutCreateMenu(self.handleMenuTotalEsf)
        glutAddMenuEntry("1", 11)
        glutAddMenuEntry("2", 12)
        glutAddMenuEntry("3", 13)
        glutAddMenuEntry("4", 14)
        glutAddMenuEntry("5", 15)
        glutAddMenuEntry("6", 16)
        glutAddMenuEntry("7", 17)
        
        menuEnMovimiento = glutCreateMenu(self.handleMenuEmMovimiento)
        glutAddMenuEntry("1", 21)
        glutAddMenuEntry("2", 22)
        glutAddMenuEntry("3", 23)
        glutAddMenuEntry("4", 24)
        glutAddMenuEntry("5", 25)
        glutAddMenuEntry("6", 26)
        glutAddMenuEntry("7", 27)
        
        menuPrincipal = glutCreateMenu(self.handleMenuPrincipal)
        glutAddSubMenu("Total de esferas", menuTotalEsf)
        glutAddSubMenu("Em Movimiento", menuEnMovimiento)
        glutAddMenuEntry("Mostrar Eixos", 1)
        glutAddMenuEntry("Sair", 0)
        glutAttachMenu(GLUT_RIGHT_BUTTON)


    def main(self):
        # parse args
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--track", action="store_true")
        args = parser.parse_args()
        # set up the GLUT window
        glutInit(sys.argv)

        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        
        glutCreateWindow("EP2 - Computacao Grafica - Pendulo de Newton")
        self.initRendering()
        self.prepararMenu()
        
        glutDisplayFunc(self.drawScene)
        glutReshapeFunc(self.handleResize)
        glutSpecialFunc(self.handleSpecialKeys)
        glutTimerFunc(self.milisegundos, self.update, 0)

        glutMainLoop()
        return 0


newtoncradle = NewtonCradle()
newtoncradle.main()