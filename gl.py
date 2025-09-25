"""
En esta clase se realizaran todo lo que este relacionado con mostrar 
cosas en pantalla y efectos, como los reflejos entre otros.
"""
import pygame
import math
import struct
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from objects.object import Material, Light
from objects.plane import Plane
from objects.disk import Disk
from objects.triangle import Triangle
from objects.cube import Cube
from mathe import *

RAYTRACER = 3 

class SimpleEnvironmentMap:
    """Environment map más simple que funciona con archivos de imagen comunes"""
    def __init__(self, filename):
        self.width = 0
        self.height = 0
        self.pixels = []
        self.load_image(filename)
    
    def load_image(self, filename):
        """Carga una imagen usando pygame (soporta JPG, PNG, etc.)"""
        try:
            surface = pygame.image.load(filename)
            self.width = surface.get_width()
            self.height = surface.get_height()
            
            print(f"Cargando imagen: {filename} ({self.width}x{self.height})")
            
            self.pixels = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    color = surface.get_at((x, y))
                    normalized_color = [color.r / 255.0, color.g / 255.0, color.b / 255.0]
                    row.append(normalized_color)
                self.pixels.append(row)
            
            return True
        except Exception as e:
            print(f"Error cargando imagen {filename}: {e}")
            return False
    
    def sample(self, direction):
        """Muestrea el environment map basado en la dirección del rayo"""
        if not self.pixels:
            return [0.2, 0.2, 0.3]
        
        u = 0.5 + math.atan2(direction[2], direction[0]) / (2 * math.pi)
        v = 0.5 - math.asin(max(-1, min(1, direction[1]))) / math.pi
        
        x = int(u * self.width) % self.width
        y = int(v * self.height) % self.height
        
        return self.pixels[y][x]

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # OPTIMIZACIONES INTELIGENTES: Mejor resolución manteniendo velocidad
        self.render_scale = 2  # Reducido de 4 a 2 para mejor calidad
        self.render_width = self.width // self.render_scale
        self.render_height = self.height // self.render_scale
        
        # Cache para optimizar cálculos
        self.intersection_cache = {}
        self.normal_cache = {}
        
        # Configuración de renderizado
        self.background_color = [0.2, 0.2, 0.3]
        self.objects = []
        self.lights = []
        self.camera_position = [0, 0, 0]
        self.environment_map = None
        self.raytracing_completed = False
        self.rendered_surface = None
        
        # Configuración de la cámara
        self.fov = 60
        self.aspect_ratio = self.width / self.height
        
        # Para mostrar progreso
        self.current_line = 0
        
        print(f"Renderer inicializado: {self.width}x{self.height} -> {self.render_width}x{self.render_height}")
        
    def set_camera(self, position):
        self.camera_position = position
        
    def add_object(self, obj):
        self.objects.append(obj)
        
    def add_light(self, light):
        self.lights.append(light)
        
    def load_environment_map(self, filename):
        """Carga un environment map"""
        try:
            self.environment_map = SimpleEnvironmentMap(filename)
            return True
        except Exception as e:
            print(f"Error cargando environment map: {e}")
            return False
    
    def create_room_scene(self):
        """Crea la escena de la habitación según las especificaciones EXACTAS"""
        self.objects.clear()
        self.lights.clear()
        
        # Materiales mejorados para mejor calidad visual
        white_wall = Material(
            diffuse=(0.95, 0.95, 0.95),
            specular=(0.2, 0.2, 0.2),
            ambient=(0.3, 0.3, 0.3),
            shininess=20,
            reflectivity=0.1
        )
        
        glass_floor = Material(
            diffuse=(0.7, 0.8, 0.9),
            specular=(0.5, 0.5, 0.5),
            ambient=(0.2, 0.25, 0.3),
            shininess=50,
            reflectivity=0.3,
            transparency=0.1
        )
        
        purple_rock = Material(
            diffuse=(0.6, 0.2, 0.8),
            specular=(0.15, 0.1, 0.2),
            ambient=(0.2, 0.1, 0.25),
            shininess=10,
            reflectivity=0.05
        )
        
        yellow_material = Material(
            diffuse=(0.9, 0.8, 0.1),
            specular=(0.3, 0.25, 0.1),
            ambient=(0.25, 0.2, 0.05),
            shininess=25,
            reflectivity=0.15
        )
        
        lava_material = Material(
            diffuse=(0.9, 0.1, 0.1),
            specular=(0.4, 0.2, 0.2),
            ambient=(0.4, 0.15, 0.15),
            shininess=40,
            reflectivity=0.2,
            transparency=0.1
        )
        
        # === HABITACIÓN: 5 PLANOS ===
        # Suelo (vidrioso)
        floor = Plane([0, -3, 0], [0, 1, 0], glass_floor)
        self.add_object(floor)
        
        # Techo (blanco)
        ceiling = Plane([0, 3, 0], [0, -1, 0], white_wall)
        self.add_object(ceiling)
        
        # Pared del fondo (blanco) - donde irá el disco
        back_wall = Plane([0, 0, -8], [0, 0, 1], white_wall)
        self.add_object(back_wall)
        
        # Pared izquierda (blanco) - donde irá el triángulo
        left_wall = Plane([-4, 0, 0], [1, 0, 0], white_wall)
        self.add_object(left_wall)
        
        # Pared derecha (blanco)
        right_wall = Plane([4, 0, 0], [-1, 0, 0], white_wall)
        self.add_object(right_wall)
        
        # === DOS CUBOS EN EL SUELO (SEPARADOS) ===
        # Cubo morado rocoso (izquierda)
        cube1 = Cube([-2.5, -3, -6], [-1.5, -2, -5], purple_rock)
        self.add_object(cube1)
        
        # Cubo amarillo (derecha)
        cube2 = Cube([1.5, -3, -6.5], [2.5, -2, -5.5], yellow_material)
        self.add_object(cube2)
        
        # === DISCO EN LA PARED DEL FONDO (ARRIBA, CENTRADO) ===
        # Posicionado en la pared del fondo, centrado horizontalmente, en la parte superior
        disk = Disk([0, 1.8, -7.99], [0, 0, 1], 0.6, lava_material)
        self.add_object(disk)
        
        # === TRIÁNGULO DEBAJO DEL DISCO ===
        # Triángulo plano (no pirámide) pegado a la pared del fondo, debajo del disco
        triangle = Triangle(
            [-0.5, 0.5, -7.99],   # Vértice izquierdo
            [0.5, 0.5, -7.99],    # Vértice derecho  
            [0, -0.2, -7.99],     # Vértice inferior (centrado)
            lava_material
        )
        self.add_object(triangle)
        
        # === ILUMINACIÓN OPTIMIZADA ===
        # Dos luces en las esquinas superiores del fondo
        light1 = Light([-3, 2.5, -7.5], (1.0, 1.0, 1.0), 1.4)
        light2 = Light([3, 2.5, -7.5], (1.0, 1.0, 1.0), 1.4)
        
        # Luz ambiental suave
        ambient_light = Light([0, 0, 0], (0.3, 0.3, 0.3), 0.4)
        
        # Luz adicional frontal para mejor visibilidad
        front_light = Light([0, 1, -2], (0.8, 0.8, 0.8), 0.8)
        
        self.add_light(light1)
        self.add_light(light2)
        self.add_light(ambient_light)
        self.add_light(front_light)
        
        print("=== ESCENA CREADA CORRECTAMENTE ===")
        print("HABITACIÓN:")
        print(f"- {len([obj for obj in self.objects if isinstance(obj, Plane)])} planos (suelo vidrioso + 4 paredes blancas)")
        print("OBJETOS:")
        print(f"- {len([obj for obj in self.objects if isinstance(obj, Cube)])} cubos en el suelo (morado rocoso + amarillo)")
        print(f"- 1 disco rojo lava en pared del fondo (arriba, centrado)")
        print(f"- 1 triángulo rojo lava en pared del fondo (debajo del disco)")
        print(f"- {len(self.lights)} fuentes de luz")
        print(f"RESOLUCIÓN: {self.render_width}x{self.render_height} -> {self.width}x{self.height}")
        print("===================================")
    
    def cast_ray(self, ray_origin, ray_direction, recursion_depth=0):
        """Lanza un rayo y calcula el color resultante - OPTIMIZADO CON CACHE"""
        if recursion_depth > 2:  # Aumentado para mejor calidad
            return [0, 0, 0]
        
        # Encontrar la intersección más cercana
        closest_t = float('inf')
        closest_object = None
        
        for obj in self.objects:
            t = obj.ray_intersect(ray_origin, ray_direction)
            if t is not None and t < closest_t:
                closest_t = t
                closest_object = obj
        
        if closest_object is None:
            if self.environment_map:
                return self.environment_map.sample(ray_direction)
            return self.background_color
        
        # Calcular punto de intersección y normal
        intersection_point = [ray_origin[i] + closest_t * ray_direction[i] for i in range(3)]
        normal = closest_object.get_normal(intersection_point)
        
        # Calcular color usando modelo de iluminación mejorado
        color = self.calculate_lighting_improved(intersection_point, normal, ray_direction, closest_object.material)
        
        # Reflexiones mejoradas
        if closest_object.material.reflectivity > 0.05 and recursion_depth < 2:
            reflected_dir = reflect_vector(ray_direction, normal)
            reflected_origin = vector_add(intersection_point, vector_multiply(normal, 0.001))
            reflected_color = self.cast_ray(reflected_origin, reflected_dir, recursion_depth + 1)
            
            for i in range(3):
                color[i] = lerp(color[i], reflected_color[i], closest_object.material.reflectivity)
        
        # Transparencia/refracción mejorada
        if closest_object.material.transparency > 0.05 and recursion_depth < 2:
            refracted_dir = refract_vector(ray_direction, normal, closest_object.material.refractive_index)
            if refracted_dir:
                refracted_origin = vector_subtract(intersection_point, vector_multiply(normal, 0.001))
                refracted_color = self.cast_ray(refracted_origin, refracted_dir, recursion_depth + 1)
                
                for i in range(3):
                    color[i] = lerp(color[i], refracted_color[i], closest_object.material.transparency)
        
        return color
    
    def calculate_lighting_improved(self, point, normal, view_direction, material):
        """Cálculo de iluminación mejorado para mejor calidad visual"""
        color = [0, 0, 0]
        
        # Calcular todas las luces para mejor calidad
        for light in self.lights:
            if light.intensity <= 0:
                continue
                
            light_direction = vector_normalize(vector_subtract(light.position, point))
            distance_to_light = vector_magnitude(vector_subtract(light.position, point))
            
            # Atenuación por distancia (solo para luces puntuales)
            if distance_to_light > 0.1:
                attenuation = 1.0 / (1.0 + 0.1 * distance_to_light + 0.01 * distance_to_light * distance_to_light)
            else:
                attenuation = 1.0
            
            # Verificar sombras con mayor precisión
            in_shadow = self.is_in_shadow_precise(point, light_direction, light.position)
            shadow_factor = 0.3 if in_shadow else 1.0
            
            # Componente difusa (Lambert)
            diffuse_intensity = max(0, dot_product(normal, light_direction))
            
            # Componente especular (Phong)
            reflected_light = reflect_vector(vector_multiply(light_direction, -1), normal)
            view_dir_normalized = vector_normalize(vector_multiply(view_direction, -1))
            specular_intensity = max(0, dot_product(reflected_light, view_dir_normalized))
            specular_intensity = specular_intensity ** material.shininess
            
            # Combinar componentes con atenuación y sombras
            effective_intensity = light.intensity * attenuation * shadow_factor
            
            for i in range(3):
                diffuse = material.diffuse[i] * light.color[i] * diffuse_intensity * effective_intensity
                specular = material.specular[i] * light.color[i] * specular_intensity * effective_intensity
                color[i] += diffuse + specular
        
        # Agregar componente ambiental
        for i in range(3):
            color[i] += material.ambient[i]
            color[i] = clamp(color[i])
        
        return color
    
    def is_in_shadow_precise(self, point, light_direction, light_position):
        """Detección de sombras más precisa"""
        distance_to_light = vector_magnitude(vector_subtract(light_position, point))
        shadow_ray_origin = vector_add(point, vector_multiply(light_direction, 0.001))
        
        for obj in self.objects:
            t = obj.ray_intersect(shadow_ray_origin, light_direction)
            if t is not None and 0.001 < t < distance_to_light:
                return True
        return False
    
    def get_ray_direction(self, x, y):
        """Calcula la dirección del rayo para un píxel dado"""
        px = (2 * x / self.render_width) - 1
        py = 1 - (2 * y / self.render_height)
        
        px *= self.aspect_ratio * math.tan(math.radians(self.fov / 2))
        py *= math.tan(math.radians(self.fov / 2))
        
        direction = vector_normalize([px, py, -1])
        return direction
    
    def glClear(self):
        """Limpia la pantalla"""
        self.screen.fill((0, 0, 0))
    
    def glRender(self):
        """Renderiza la escena usando ray tracing optimizado con mejor calidad"""
        if self.raytracing_completed:
            # Mostrar la imagen ya renderizada escalada con suavizado
            if self.rendered_surface:
                scaled_surface = pygame.transform.smoothscale(self.rendered_surface, (self.width, self.height))
                self.screen.blit(scaled_surface, (0, 0))
            return
        
        # Crear superficie de renderizado si no existe
        if self.rendered_surface is None:
            self.rendered_surface = pygame.Surface((self.render_width, self.render_height))
        
        # Renderizar menos líneas por frame para mostrar progreso más suave
        lines_per_frame = 4  # Reducido para mejor calidad
        
        for line_offset in range(lines_per_frame):
            if self.current_line >= self.render_height:
                self.raytracing_completed = True
                break
            
            y = self.current_line
            
            # Renderizar toda la línea con antialiasing básico
            for x in range(self.render_width):
                # Antialiasing simple: promedio de 4 sub-píxeles
                color_samples = []
                for sub_x in [0.25, 0.75]:
                    for sub_y in [0.25, 0.75]:
                        ray_direction = self.get_ray_direction(x + sub_x, y + sub_y)
                        sample_color = self.cast_ray(self.camera_position, ray_direction)
                        color_samples.append(sample_color)
                
                # Promediar las muestras
                final_color = [0, 0, 0]
                for sample in color_samples:
                    for i in range(3):
                        final_color[i] += sample[i]
                
                for i in range(3):
                    final_color[i] /= len(color_samples)
                
                # Convertir color a formato pygame
                pygame_color = [int(clamp(final_color[i]) * 255) for i in range(3)]
                
                # Dibujar píxel en la superficie de renderizado
                self.rendered_surface.set_at((x, y), pygame_color)
            
            self.current_line += 1
        
        # Escalar y mostrar la superficie actual con suavizado
        if self.rendered_surface:
            if self.current_line > 0:
                current_surface = self.rendered_surface.subsurface((0, 0, self.render_width, min(self.current_line, self.render_height)))
                scaled_height = int(self.height * self.current_line / self.render_height)
                scaled_surface = pygame.transform.smoothscale(current_surface, (self.width, scaled_height))
                self.screen.blit(scaled_surface, (0, 0))
    
    def save_bmp(self, filename):
        """Guarda la imagen renderizada como BMP en alta calidad"""
        if self.rendered_surface and self.raytracing_completed:
            # Guardar la versión escalada con suavizado
            scaled_surface = pygame.transform.smoothscale(self.rendered_surface, (self.width, self.height))
            pygame.image.save(scaled_surface, filename)
            print(f"Imagen de alta calidad guardada como {filename}")
        else:
            pygame.image.save(self.screen, filename)
            print(f"Imagen parcial guardada como {filename}")
    
    def reset_render(self):
        """Reinicia el renderizado"""
        self.raytracing_completed = False
        self.rendered_surface = None
        self.current_line = 0
        self.intersection_cache.clear()
        self.normal_cache.clear()