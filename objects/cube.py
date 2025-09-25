"""
En esta clase se definiran las operaciones asiganadas para un cubo y sus atributos
herendando de la clase "objetos".
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from object import Object
from mathe import *

class Cube(Object):
    def __init__(self, min_point, max_point, material):
        super().__init__(material)
        self.min_point = min_point
        self.max_point = max_point
    
    def ray_intersect(self, ray_origin, ray_direction):
        """Calcula la intersección de un rayo con el cubo usando el algoritmo slab"""
        t_min = float('-inf')
        t_max = float('inf')
        
        for i in range(3):
            if abs(ray_direction[i]) < 1e-6:
                # Rayo paralelo a la cara
                if ray_origin[i] < self.min_point[i] or ray_origin[i] > self.max_point[i]:
                    return None
            else:
                t1 = (self.min_point[i] - ray_origin[i]) / ray_direction[i]
                t2 = (self.max_point[i] - ray_origin[i]) / ray_direction[i]
                
                if t1 > t2:
                    t1, t2 = t2, t1
                
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                
                if t_min > t_max:
                    return None
        
        if t_min > 0.001:
            return t_min
        elif t_max > 0.001:
            return t_max
        
        return None
    
    def get_normal(self, point):
        """Calcula la normal del cubo en el punto dado"""
        # Encontrar qué cara está más cerca del punto
        epsilon = 0.001
        
        if abs(point[0] - self.min_point[0]) < epsilon:
            return [-1, 0, 0]
        elif abs(point[0] - self.max_point[0]) < epsilon:
            return [1, 0, 0]
        elif abs(point[1] - self.min_point[1]) < epsilon:
            return [0, -1, 0]
        elif abs(point[1] - self.max_point[1]) < epsilon:
            return [0, 1, 0]
        elif abs(point[2] - self.min_point[2]) < epsilon:
            return [0, 0, -1]
        elif abs(point[2] - self.max_point[2]) < epsilon:
            return [0, 0, 1]
        
        # Si no está exactamente en una cara, calcular la normal más cercana
        center = [(self.min_point[i] + self.max_point[i]) / 2 for i in range(3)]
        diff = vector_subtract(point, center)
        
        # Encontrar el componente con mayor valor absoluto
        max_component = 0
        max_value = abs(diff[0])
        for i in range(1, 3):
            if abs(diff[i]) > max_value:
                max_value = abs(diff[i])
                max_component = i
        
        normal = [0, 0, 0]
        normal[max_component] = 1 if diff[max_component] > 0 else -1
        
        return normal