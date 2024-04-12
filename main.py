import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, pi

# Inicjalizacja biblioteki Pygame
pygame.init()

# Ustawienie szerokości i wysokości okna
width, height = 1400, 600
screen = pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)

# Inicjalizacja kamery
camera_x, camera_y, camera_z = 8, 1, 30
camera_yaw, camera_pitch, camera_roll = 0, 0, 0
# Macierze do obliczeń
rotation_matrix = np.identity(4)
translation_matrix = np.identity(4)

zoom = 1.0  # Domyślna ogniskowa
fov = 45  # Początkowy kąt widzenia
speed = 0.25 # Kamera AWSD
rotation_speed = 0.01 # Kamera strzalki
translation_speed = 0.5  # Prędkość translacji góra-dół

def set_perspective():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fov + zoom, (width / height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def draw_board(board_size=80, pattern_size=4):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE) 

    glBegin(GL_QUADS)

    # Ustawiamy kolor tła
    glColor3f(0.2, 0.2, 0.2)

    # Rysujemy większe pole
    glVertex3f(-board_size, -0.5, -board_size)
    glVertex3f(board_size, -0.5, -board_size)
    glVertex3f(board_size, -0.5, board_size)
    glVertex3f(-board_size, -0.5, board_size)

    glEnd()

    # Dodajemy wzór na powierzchni pola
    glBegin(GL_QUADS)
    glColor3f(0.6, 0.6, 0.6)
    for i in range(-board_size, board_size, pattern_size):
        for j in range(-board_size, board_size, pattern_size):
            glVertex3f(i, -0.49, j)
            glVertex3f(i + pattern_size, -0.49, j)
            glVertex3f(i + pattern_size, -0.49, j + pattern_size)
            glVertex3f(i, -0.49, j + pattern_size)
    glEnd()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Przywrócenie trybu rysowania wypełnionego

def draw_cube(x, y, z, color=(0.2, 0.5, 0.5), line_width=2.0):
    global vertices

    size = 2.0  # Wielkość prostopadłościanu

    vertices = [
        [x - size, y - size, z - size],
        [x + size, y - size, z - size],
        [x + size, y + 3 * size, z - size],
        [x - size, y + 3 * size, z - size],
        [x - size, y - size, z + size],
        [x + size, y - size, z + size],
        [x + size, y + 3 * size, z + size],
        [x - size, y + 3 * size, z + size],
    ]

    faces = (
        (0, 1, 2, 3),
        (3, 2, 6, 7),
        (7, 6, 5, 4),
        (4, 5, 1, 0),
        (1, 5, 6, 2),
        (4, 0, 3, 7)
    )

    edge_color = (0, 0, 0)  # Kolor krawędzi (czarny)

    # Rysowanie ścian
    glBegin(GL_QUADS)
    glColor3fv(color)
    for i, face in enumerate(faces):
        for vertex in face:
            glVertex3fv(vertices[vertex])
    glEnd()

    # Ustawianie szerokości krawędzi
    glLineWidth(line_width)

    # Rysowanie krawędzi górnej podstawy
    glBegin(GL_LINES)
    glColor3fv(edge_color)
    for i in range(4):
        glVertex3fv(vertices[i])
        glVertex3fv(vertices[(i + 1) % 4])
    glEnd()

    # Rysowanie krawędzi dolnej podstawy
    glBegin(GL_LINES)
    for i in range(4, 8):
        glVertex3fv(vertices[i])
        glVertex3fv(vertices[(i + 1) % 4 + 4])
    glEnd()

    # Rysowanie krawędzi pionowych
    glBegin(GL_LINES)
    for i in range(4):
        glVertex3fv(vertices[i])
        glVertex3fv(vertices[i + 4])
    glEnd()

    # Przywracanie domyślnej szerokości linii
    glLineWidth(1.0)

def draw_sphere(radius=2, position=(0, 0, 0), segments=30, rings=30):
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)  # Ustawienie trybu rysowania wypełnionego

    glColor3f(0.5, 0.3, 0.8)

    for i in range(rings + 1):
        latitude1 = pi * (-0.5 + i / rings)
        sin1 = sin(latitude1)
        cos1 = cos(latitude1)
        latitude2 = pi * (-0.5 + (i + 1) / rings)
        sin2 = sin(latitude2)
        cos2 = cos(latitude2)

        glBegin(GL_QUAD_STRIP)

        for j in range(segments + 1):
            longitude = 2 * pi * (j / segments)
            sin_long = sin(longitude)
            cos_long = cos(longitude)

            x1 = cos_long * cos1
            y1 = sin1
            z1 = sin_long * cos1

            x2 = cos_long * cos2
            y2 = sin2
            z2 = sin_long * cos2

            glVertex3f(x1 * radius + position[0], y1 * radius + position[1], z1 * radius + position[2])
            glVertex3f(x2 * radius + position[0], y2 * radius + position[1], z2 * radius + position[2])

        glEnd()

# Główna pętla programu
while True:
    glClearColor(0.8, 0.8, 0.8, 0.0) 
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Model Zadanie 2b
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # light_position = [camera_x, camera_y, camera_z, 1.0]
    light_position = [15.0, 15.0, 30.0, 1.0] # Pozycja swiatla i rodzaj - 1.0 Punktowe zrodlo swiatla, 0.0 Nieskonczone
    light_diffuse = [1.0, 1.0, 1.0, 1.0] # Kolor swiatla RGB
    light_specular = [1.0, 1.0, 1.0, 1.0] # Kolor odbitego swiatla RBG

    material_diffuse = [0.2, 0.5, 0.5, 1.0] # Kolor materialu
    material_specular = [1.0, 1.0, 1.0, 1.0] # Kolor odbitego swiatla przez material
    material_shininess = 20.0 # Polysk materialu

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

    # Rysowanie
    draw_board()
    draw_cube(0, 1, 0, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_cube(0,1,0, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_cube(0,1,10, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_cube(0,1,20, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_sphere(position=(8,1,10))
    draw_cube(16,1,0, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_cube(16,1,10, color=(0.2, 0.5, 0.5), line_width=2.0)
    draw_cube(16,1,20, color=(0.2, 0.5, 0.5), line_width=2.0)

    #### Osobne materialy
    # Pierwsza sfera (material_diffuse1, material_specular1)
    material_diffuse1 = [0.7, 0.7, 0.2, 1.0]
    material_specular1 = [.5, 0.5, 0.5, 1.0]
    material_shininess1 = 5.0

    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse1)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular1)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess1)
    draw_sphere(radius=2, position=(8, 1, 10))

    # Druga sfera (material_diffuse2, material_specular2)
    material_diffuse2 = [0.3, 0.8, 0.8, 1.0]
    material_specular2 = [0.5, 0.5, 0.5, 1.0]
    material_shininess2 = 50.0

    glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse2)
    glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular2)
    glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess2)
    draw_sphere(radius=2, position=(8, 5, 10))

    if keys[K_a]:
        translation_matrix = np.dot(translation_matrix,
                                    np.array([[1, 0, 0,
                                   -speed * cos(np.radians(camera_yaw))],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, speed * sin(np.radians(camera_yaw))],
                                   [0, 0, 0, 1]]))
    if keys[K_d]:
        translation_matrix = np.dot(translation_matrix,
                                    np.array([[1, 0, 0,
                                   speed * cos(np.radians(camera_yaw))],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, -speed * sin(np.radians(camera_yaw))],
                                   [0, 0, 0, 1]]))
    if keys[K_w]:
        translation_matrix = np.dot(translation_matrix,
                                    np.array([[1, 0, 0,
                                   speed * sin(np.radians(camera_yaw))],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, speed * cos(np.radians(camera_yaw))],
                                   [0, 0, 0, 1]]))
    if keys[K_s]:
        translation_matrix = np.dot(translation_matrix,
                                    np.array([[1, 0, 0,
                                   -speed * sin(np.radians(camera_yaw))],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, -speed * cos(np.radians(camera_yaw))],
                                   [0, 0, 0, 1]]))
    # Obracanie kamerą
    if keys[K_LEFT]:
        rotation_matrix = np.dot(rotation_matrix,
                         np.array([[cos(rotation_speed),
                         0, sin(rotation_speed), 0],
                         [0, 1, 0, 0],
                         [-sin(rotation_speed), 0, cos(rotation_speed), 0],
                         [0, 0, 0, 1]]))
    if keys[K_RIGHT]:
        rotation_matrix = np.dot(rotation_matrix,
                         np.array([[cos(-rotation_speed),
                         0, sin(-rotation_speed), 0],
                         [0, 1, 0, 0],
                         [-sin(-rotation_speed), 0, cos(-rotation_speed), 0],
                         [0, 0, 0, 1]]))
    if keys[K_UP]:
        rotation_matrix = np.dot(rotation_matrix,
                         np.array([[1, 0, 0, 0],
                         [0, cos(rotation_speed), -sin(rotation_speed), 0],
                         [0, sin(rotation_speed), cos(rotation_speed), 0],
                         [0, 0, 0, 1]]))
    if keys[K_DOWN]:
        rotation_matrix = np.dot(rotation_matrix,
                         np.array([[1, 0, 0, 0],
                         [0, cos(-rotation_speed), -sin(-rotation_speed), 0],
                         [0, sin(-rotation_speed), cos(-rotation_speed), 0],
                         [0, 0, 0, 1]]))

    # Translacja kamery góra-dół
    if keys[K_SPACE]:
        translation_matrix = np.dot(translation_matrix,
                            np.array([[1, 0, 0, 0],
                           [0, 1, 0, translation_speed],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]]))
    if keys[K_LSHIFT]:
        translation_matrix = np.dot(translation_matrix,
                            np.array([[1, 0, 0, 0],
                           [0, 1, 0, -translation_speed],
                           [0, 0, 1, 0],
                           [0, 0, 0, 1]]))

    # Aktualizacja zmiennych kamery na podstawie macierzy translacji
    camera_x += translation_matrix[0, 3]
    camera_y += translation_matrix[1, 3]
    camera_z += translation_matrix[2, 3]

    # Resetowanie macierzy translacji do macierzy jednostkowej
    translation_matrix = np.identity(4)

    # Obsługa klawiszy q i e
    if keys[K_q]:
        rotation_matrix = np.dot(rotation_matrix, np.array([[cos(rotation_speed), -sin(rotation_speed), 0, 0],
                                                            [sin(rotation_speed), cos(rotation_speed), 0, 0],
                                                            [0, 0, 1, 0],
                                                            [0, 0, 0, 1]]))
    if keys[K_e]:
        rotation_matrix = np.dot(rotation_matrix, np.array([[cos(-rotation_speed), -sin(-rotation_speed), 0, 0],
                                                            [sin(-rotation_speed), cos(-rotation_speed), 0, 0],
                                                            [0, 0, 1, 0],
                                                            [0, 0, 0, 1]]))

    # Zastosowanie transformacji do macierzy Model-View
    glLoadIdentity()
    glMultMatrixf(rotation_matrix.flatten())
    glMultMatrixf(translation_matrix.flatten())

    # Zmiana ogniskowej aparatu (zoom)
    if keys[K_o]:
        zoom -= 0.1
    if keys[K_p]:
        zoom += 0.1

    # Ustawianie kamery
    set_perspective()
    glRotatef(camera_pitch, 1, 0, 0)
    glRotatef(camera_yaw, 0, 1, 0)
    glRotatef(camera_roll, 0, 0, 1)
    glTranslatef(-camera_x, -camera_y, -camera_z)

    pygame.display.flip()
    pygame.time.wait(10)
