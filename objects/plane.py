"""
En esta clase se definiran las operaciones asiganadas para un plano y sus atributos
herendando de la clase "objetos".
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object import Object
from mathe import *

class Plane(Object):
    def __init__(self, point, normal, material):
        super().__init__(material)
        self.point = point
        self.normal = vector_normalize(normal)
    
    def ray_intersect(self, ray_origin, ray_direction):
        """Calcula la intersección de un rayo con el plano"""
        denom = dot_product(self.normal, ray_direction)
        
        if abs(denom) < 1e-6:  # Rayo paralelo al plano
            return None
        
        t = dot_product(vector_subtract(self.point, ray_origin), self.normal) / denom
        
        if t > 0.001:  # Evitar auto-intersección
            return t
        
        return None
    
    def get_normal(self, point):
        """Retorna la normal del plano"""
        return self.normal