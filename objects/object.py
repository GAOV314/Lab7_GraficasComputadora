"""
En esta clase se describe las propiedades de un objeto y sus comportamiento.
Clase padre de cualquier objeto renderizable.
"""

class Material:
    def __init__(self, diffuse=(1,1,1), specular=(1,1,1), ambient=(0.1,0.1,0.1), 
                 shininess=32, reflectivity=0.0, transparency=0.0, refractive_index=1.0):
        self.diffuse = diffuse
        self.specular = specular
        self.ambient = ambient
        self.shininess = shininess
        self.reflectivity = reflectivity
        self.transparency = transparency
        self.refractive_index = refractive_index

class Light:
    def __init__(self, position, color=(1,1,1), intensity=1.0):
        self.position = position
        self.color = color
        self.intensity = intensity

class Object:
    def __init__(self, material):
        self.material = material
    
    def ray_intersect(self, ray_origin, ray_direction):
        """Debe ser implementado por cada objeto específico"""
        raise NotImplementedError
    
    def get_normal(self, point):
        """Debe ser implementado por cada objeto específico"""
        raise NotImplementedError