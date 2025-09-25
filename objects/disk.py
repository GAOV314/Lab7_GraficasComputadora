"""
En esta clase se definiran las operaciones asiganadas para un disco y sus atributos
herendando de la clase "objetos".
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object import Object
from mathe import *

class Disk(Object):
    def __init__(self, center, normal, radius, material):
        super().__init__(material)
        self.center = center
        self.normal = vector_normalize(normal)
        self.radius = radius
    
    def ray_intersect(self, ray_origin, ray_direction):
        """Calcula la intersección de un rayo con el disco"""
        denom = dot_product(self.normal, ray_direction)
        
        if abs(denom) < 1e-6:  # Rayo paralelo al disco
            return None
        
        t = dot_product(vector_subtract(self.center, ray_origin), self.normal) / denom
        
        if t <= 0.001:  # Evitar auto-intersección
            return None
        
        # Calcular punto de intersección
        intersection_point = [ray_origin[i] + t * ray_direction[i] for i in range(3)]
        
        # Verificar si está dentro del radio del disco
        distance_squared_val = distance_squared(intersection_point, self.center)
        
        if distance_squared_val <= self.radius * self.radius:
            return t
        
        return None
    
    def get_normal(self, point):
        """Retorna la normal del disco"""
        return self.normal