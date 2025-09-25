"""
En este modulo se llevara acabo el control de todos los módulos del funcionamiento de
este programa, incluyendo la ejecución final del grafico.
"""
import pygame
import os
from gl import *

# Configuración de alta calidad
width = 800
height = 600
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.SCALED)
clock = pygame.time.Clock()
rend = Renderer(screen)

# Crear la escena de la habitación
rend.create_room_scene()

# Configurar cámara
rend.set_camera((0, 0, 2))

# Intentar cargar environment maps
environment_files = [
    "environment.hdr",
    "skybox.hdr", 
    "hdri.hdr",
    "environment.jpg",
    "skybox.jpg",
    "environment.png",
    "skybox.png"
]

environment_loaded = False
for env_file in environment_files:
    if os.path.exists(env_file):
        print(f"Intentando cargar: {env_file}")
        if rend.load_environment_map(env_file):
            environment_loaded = True
            break

if not environment_loaded:
    print("No se encontró ningún environment map - usando fondo por defecto")

print("\n=== RAY TRACER DE ALTA CALIDAD - HABITACIÓN 3D ===")
print("Escenario: Habitación con planos, cubos, disco y triángulo")
print("OPTIMIZACIONES INTELIGENTES:")
print(f"- Resolución nativa: {rend.render_width}x{rend.render_height}")
print("- Algoritmo de intersección optimizado")
print("- Caching de cálculos costosos")
print("- Antialiasing básico (4x)")
print("- Renderizado progresivo mejorado")
print("\nControles:")
print("- ESC: Salir")
print("- ENTER: Guardar imagen")
print("- R: Re-renderizar")
print("- ESPACIO: Información de archivos")
print("\nRenderizando en alta resolución...")

running = True
start_time = pygame.time.get_ticks()

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                running = False
            elif e.key == pygame.K_RETURN:
                filename = "room_scene_hq.bmp"
                rend.save_bmp(filename)
                print(f"Imagen guardada como {filename}")
            elif e.key == pygame.K_r:
                rend.reset_render()
                start_time = pygame.time.get_ticks()
                print("Re-renderizando...")
            elif e.key == pygame.K_SPACE:
                print("\n=== Archivos en directorio actual ===")
                files = os.listdir(".")
                image_files = [f for f in files if f.lower().endswith(('.hdr', '.jpg', '.jpeg', '.png', '.bmp'))]
                if image_files:
                    print("Archivos de imagen encontrados:")
                    for f in image_files:
                        size = os.path.getsize(f)
                        print(f"  - {f} ({size} bytes)")
                else:
                    print("No se encontraron archivos de imagen.")
                print("=======================================\n")

    rend.glClear()
    rend.glRender()

    # Mostrar progreso y tiempo
    if rend.raytracing_completed:
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        env_status = "Con Environment Map" if rend.environment_map else "Sin Environment Map"
        title = f"Habitación 3D {env_status} | Completado en {elapsed_time:.1f}s | ESC: Salir | ENTER: Guardar"
    else:
        progress = (rend.current_line / rend.render_height) * 100
        elapsed_time = (pygame.time.get_ticks() - start_time) / 1000.0
        title = f"Renderizando HQ... {progress:.1f}% | Tiempo: {elapsed_time:.1f}s | ESC: Salir"
    
    pygame.display.set_caption(title)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()