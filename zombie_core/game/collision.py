import math


def circle_rect_collide(circle_pos, circle_radius, rect):
    """Checks collision between a circle (bullet/projectile) and a
    rect (zombie/barricade)."""
    closest_x = max(rect.left, min(circle_pos.x, rect.right))
    closest_y = max(rect.top, min(circle_pos.y, rect.bottom))
    distance = math.dist((circle_pos.x, circle_pos.y), (closest_x, closest_y))
    return distance <= circle_radius
