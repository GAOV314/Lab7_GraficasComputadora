"""
En este módulo se realizaran todas las operaciones matemáticas que deban hacerse en todo el programa.
"""

import math

def dot_product(v1, v2):
    """Producto punto entre dos vectores"""
    return sum(v1[i] * v2[i] for i in range(3))

def vector_subtract(v1, v2):
    """Resta de vectores"""
    return [v1[i] - v2[i] for i in range(3)]

def vector_add(v1, v2):
    """Suma de vectores"""
    return [v1[i] + v2[i] for i in range(3)]

def vector_multiply(vector, scalar):
    """Multiplica un vector por un escalar"""
    return [vector[i] * scalar for i in range(3)]

def vector_magnitude(vector):
    """Calcula la magnitud de un vector"""
    return math.sqrt(sum(vector[i] * vector[i] for i in range(3)))

def vector_normalize(vector):
    """Normaliza un vector"""
    magnitude = vector_magnitude(vector)
    if magnitude == 0:
        return [0, 0, 0]
    return [vector[i] / magnitude for i in range(3)]

def cross_product(v1, v2):
    """Producto cruz entre dos vectores"""
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def reflect_vector(incident, normal):
    """Calcula el vector de reflexión"""
    dot = dot_product(incident, normal)
    return [incident[i] - 2 * dot * normal[i] for i in range(3)]

def refract_vector(incident, normal, eta):
    """Calcula el vector de refracción usando la ley de Snell"""
    cos_i = -dot_product(normal, incident)
    sin_t2 = eta * eta * (1.0 - cos_i * cos_i)
    
    if sin_t2 > 1.0:  # Reflexión total interna
        return None
    
    cos_t = math.sqrt(1.0 - sin_t2)
    return [eta * incident[i] + (eta * cos_i - cos_t) * normal[i] for i in range(3)]

def lerp(a, b, t):
    """Interpolación lineal entre dos valores"""
    return a + t * (b - a)

def clamp(value, min_val=0.0, max_val=1.0):
    """Limita un valor entre un mínimo y máximo"""
    return max(min_val, min(max_val, value))

def point_in_triangle(p, a, b, c):
    """Verifica si un punto está dentro de un triángulo usando coordenadas baricéntricas"""
    v0 = vector_subtract(c, a)
    v1 = vector_subtract(b, a)
    v2 = vector_subtract(p, a)
    
    dot00 = dot_product(v0, v0)
    dot01 = dot_product(v0, v1)
    dot02 = dot_product(v0, v2)
    dot11 = dot_product(v1, v1)
    dot12 = dot_product(v1, v2)
    
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    
    return (u >= 0) and (v >= 0) and (u + v <= 1)

def distance_squared(p1, p2):
    """Calcula la distancia al cuadrado entre dos puntos"""
    return sum((p1[i] - p2[i]) ** 2 for i in range(3))