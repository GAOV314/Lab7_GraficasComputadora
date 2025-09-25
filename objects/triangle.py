"""
En esta clase se definiran las operaciones asiganadas para un triangulo y sus atributos
herendando de la clase "objetos".
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object import Object
from mathe import *

class Triangle(Object):
    def __init__(self, v0, v1, v2, material):
        super().__init__(material)
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        
        # Calcular la normal del triángulo
        edge1 = vector_subtract(v1, v0)
        edge2 = vector_subtract(v2, v0)
        self.normal = vector_normalize(cross_product(edge1, edge2))
    
    def ray_intersect(self, ray_origin, ray_direction):
        """Calcula la intersección usando el algoritmo Möller-Trumbore"""
        edge1 = vector_subtract(self.v1, self.v0)
        edge2 = vector_subtract(self.v2, self.v0)
        
        h = cross_product(ray_direction, edge2)
        a = dot_product(edge1, h)
        
        if abs(a) < 1e-6:  # Rayo paralelo al triángulo
            return None
        
        f = 1.0 / a
        s = vector_subtract(ray_origin, self.v0)
        u = f * dot_product(s, h)
        
        if u < 0.0 or u > 1.0:
            return None
        
        q = cross_product(s, edge1)
        v = f * dot_product(ray_direction, q)
        
        if v < 0.0 or u + v > 1.0:
            return None
        
        t = f * dot_product(edge2, q)
        
        if t > 0.001:  # Evitar auto-intersección
            return t
        
        return None
    
    def get_normal(self, point):
        """Retorna la normal del triángulo"""
        return self.normal