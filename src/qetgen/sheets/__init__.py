"""Capas de aplicación: proyectos concretos construidos con el motor.

Aquí vive el **contenido de ingeniería** de un caso concreto (por ejemplo el
sistema FV de 588 módulos), separado del núcleo genérico. El núcleo no sabe
nada de fotovoltaico; esta capa sí.
"""

from . import fv588

__all__ = ["fv588"]
