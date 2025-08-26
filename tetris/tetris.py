import subprocess
import sys
import random
import os
import pygame

paquetes = ["pygame"] 
for paquete in paquetes:
    try:
        __import__(paquete)
    except ImportError:
        print(f"Instalando {paquete}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", paquete])
        print(f"{paquete} instalado.")

ruta_musica = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musica de fondo.mp3")
pygame.init()
pygame.mixer.init()
ANCHO, ALTO = 400, 600
TAMANO_BLOQUE = 30
columnas, filas = ANCHO // TAMANO_BLOQUE, ALTO // TAMANO_BLOQUE
ventana = pygame.display.set_mode((ANCHO + 150, ALTO))  
pygame.display.set_caption("Tetris for Miguel")

pygame.mixer.music.load(ruta_musica)
pygame.mixer.music.play(-1)

NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
GRIS = (50, 50, 50)

PIEZAS = [
    [[1, 1, 1, 1]],  # Línea
    [[1, 1], [1, 1]],  # Cuadrado
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
]

class Pieza:
    def __init__(self, x, y, forma):
        self.x = x
        self.y = y
        self.forma = forma
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    def rotar(self):
        self.forma = [list(row) for row in zip(*self.forma[::-1])]

def crear_pieza():
    return Pieza(columnas // 2 - 2, 0, random.choice(PIEZAS))

def dibujar_tablero(tablero):
    ventana.fill(NEGRO)
    for y in range(filas):
        for x in range(columnas):
            if tablero[y][x] != 0:
                pygame.draw.rect(ventana, tablero[y][x], (x * TAMANO_BLOQUE, y * TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))

    for x in range(columnas):
        pygame.draw.line(ventana, GRIS, (x*TAMANO_BLOQUE, 0), (x*TAMANO_BLOQUE, ALTO))
    for y in range(filas):
        pygame.draw.line(ventana, GRIS, (0, y*TAMANO_BLOQUE), (ANCHO, y*TAMANO_BLOQUE))

def dibujar_pieza(pieza):
    for i, fila in enumerate(pieza.forma):
        for j, valor in enumerate(fila):
            if valor:
                pygame.draw.rect(ventana, pieza.color, ((pieza.x + j) * TAMANO_BLOQUE, (pieza.y + i) * TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))

def dibujar_siguiente_pieza(pieza):
    mostrar_texto("Siguiente:", ANCHO + 20, 50, size=28)
    for i, fila in enumerate(pieza.forma):
        for j, valor in enumerate(fila):
            if valor:
                pygame.draw.rect(ventana, pieza.color, (ANCHO + 50 + j*TAMANO_BLOQUE, 100 + i*TAMANO_BLOQUE, TAMANO_BLOQUE, TAMANO_BLOQUE))

def colision(pieza, tablero):
    for i, fila in enumerate(pieza.forma):
        for j, valor in enumerate(fila):
            if valor:
                x = pieza.x + j
                y = pieza.y + i
                if x < 0 or x >= columnas or y >= filas or tablero[y][x] != 0:
                    return True
    return False

def fusionar_pieza(tablero, pieza):
    for i, fila in enumerate(pieza.forma):
        for j, valor in enumerate(fila):
            if valor:
                tablero[pieza.y + i][pieza.x + j] = pieza.color

def eliminar_filas(tablero):
    global puntaje
    nuevas_filas = [fila for fila in tablero if any(c == 0 for c in fila)]
    filas_eliminadas = filas - len(nuevas_filas)
    for _ in range(filas_eliminadas):
        nuevas_filas.insert(0, [0] * columnas)
    puntaje += filas_eliminadas * 10
    return nuevas_filas

def mostrar_texto(texto, x, y, color=BLANCO, size=36, fondo=None):
    fuente = pygame.font.Font(None, size)
    superficie_texto = fuente.render(texto, True, color)
    ventana.blit(superficie_texto, (x, y))

def caer_instantaneo(pieza, tablero):
    while not colision(pieza, tablero):
        pieza.y += 1
    pieza.y -= 1

def game_over_screen():
    mostrar_texto("¡Perdiste!", ANCHO // 4, ALTO // 2 - 50, size=48, color=(255, 0, 0), fondo=NEGRO)
    mostrar_texto("¿Jugar de nuevo? (S/N)", ANCHO // 4 - 40, ALTO // 2 + 20, size=32, color=(255,255,0), fondo=NEGRO)
    pygame.display.update()

    esperando = True
    while esperando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_s:
                    return True
                elif evento.key == pygame.K_n:
                    return False

def main():
    global puntaje
    reloj = pygame.time.Clock()
    tablero = [[0] * columnas for _ in range(filas)]
    pieza_actual = crear_pieza()
    pieza_siguiente = crear_pieza()
    puntaje = 0
    nivel = 1
    corriendo = True
    velocidad_caida = 500
    tiempo_ultimo_movimiento = pygame.time.get_ticks()
    pausa = False

    while corriendo:
        if not pausa:
            dibujar_tablero(tablero)
            dibujar_pieza(pieza_actual)
            dibujar_siguiente_pieza(pieza_siguiente)
            mostrar_texto(f"Puntaje: {puntaje}", ANCHO + 20, 200, size=24)
            mostrar_texto(f"Nivel: {nivel}", ANCHO + 20, 230, size=24)
        else:
            mostrar_texto("PAUSA", ANCHO // 3, ALTO // 2, size=60, color=(200, 0, 0))

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            elif evento.type == pygame.KEYDOWN:
                if not pausa:
                    if evento.key == pygame.K_LEFT:
                        pieza_actual.x -= 1
                        if colision(pieza_actual, tablero):
                            pieza_actual.x += 1
                    elif evento.key == pygame.K_RIGHT:
                        pieza_actual.x += 1
                        if colision(pieza_actual, tablero):
                            pieza_actual.x -= 1
                    elif evento.key == pygame.K_UP:
                        pieza_actual.rotar()
                        if colision(pieza_actual, tablero):

                            pieza_actual.rotar()
                            pieza_actual.rotar()
                            pieza_actual.rotar()
                    elif evento.key == pygame.K_DOWN:
                        pieza_actual.y += 1
                        if colision(pieza_actual, tablero):
                            pieza_actual.y -= 1
                    elif evento.key == pygame.K_SPACE: 
                        caer_instantaneo(pieza_actual, tablero)
                if evento.key == pygame.K_p: 
                    pausa = not pausa

        if not pausa:
            tiempo_actual = pygame.time.get_ticks()
            if tiempo_actual - tiempo_ultimo_movimiento > velocidad_caida:
                pieza_actual.y += 1
                if colision(pieza_actual, tablero):
                    pieza_actual.y -= 1
                    fusionar_pieza(tablero, pieza_actual)
                    tablero = eliminar_filas(tablero)

                    if puntaje >= nivel * 50:
                        nivel += 1
                        velocidad_caida -= 200

                    pieza_actual = pieza_siguiente
                    pieza_siguiente = crear_pieza()

                    if colision(pieza_actual, tablero):
                        if game_over_screen():  
                            main()
                        else:
                            corriendo = False

                tiempo_ultimo_movimiento = pygame.time.get_ticks()

        reloj.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
