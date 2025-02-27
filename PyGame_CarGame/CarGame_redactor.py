import random

import pygame
import math
from pygame.math import Vector2


def sprite_center_rotate(sprite: pygame.sprite.Sprite, angle: int, at_center=True):
    rect = sprite.image.get_rect()

    rotated_image = pygame.transform.rotate(sprite.image, -angle)
    new_rect = rotated_image.get_rect()

    if at_center:
        offset_x = rect.centerx - new_rect.centerx
        offset_y = rect.centery - new_rect.centery
    else:
        offset_x = rect.x - new_rect.x
        offset_y = rect.y - new_rect.y

    sprite.float_x += offset_x
    sprite.float_y += offset_y

    sprite.image = rotated_image
    sprite.rect = new_rect


class Redactor:
    def __init__(self):
        self.float_x = 0
        self.float_y = 0
        self.drawing = False
        self.resizing = True
        self.obj = None

    def update(self, event=None):
        if event is None:

            camera_change_x = 0
            camera_change_y = 0
            keymap = pygame.key.get_pressed()
            if keymap[pygame.K_w]:
                camera_change_y -= 10
            if keymap[pygame.K_s]:
                camera_change_y += 10
            if keymap[pygame.K_a]:
                camera_change_x -= 10
            if keymap[pygame.K_d]:
                camera_change_x += 10
            self.float_x += camera_change_x
            self.float_y += camera_change_y

            print(self.float_x, self.float_y)

            for obj in all_sprites:
                obj.rect.x = min(obj.float_x, obj.render_float_x) - self.float_x
                obj.rect.y = min(obj.float_y, obj.render_float_y) - self.float_y
            all_sprites.draw(screen)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            pygame.mouse.get_rel()
            self.obj = MapObject(all_sprites, *mouse_pos, (100, 100, 0))

        elif event.type == pygame.MOUSEBUTTONUP:
            self.obj = None

        elif event.type == pygame.MOUSEMOTION:
            if self.obj is None:
                return

            rel = pygame.mouse.get_rel()
            print(rel)

            if self.resizing:
                self.obj.resize(*rel)
            else:
                rot_point = self.obj.rect.bottomleft
                mouse_pos = event.pos
                prev_mouse_pos = mouse_pos[0] - rel[0], mouse_pos[1] - rel[1]
                prev_v = pygame.Vector2(rot_point[0] - prev_mouse_pos[0],
                                        rot_point[1] - prev_mouse_pos[1])
                new_v = pygame.Vector2(rot_point[0] - mouse_pos[0],
                                       rot_point[1] - mouse_pos[1])
                prev_v.normalize_ip()
                new_v.normalize_ip()
                prev_v_angle = (math.degrees(math.atan2(prev_v.y, prev_v.x)) + 270) % 360
                new_v_angle = (math.degrees(math.atan2(new_v.y, new_v.x)) + 270) % 360
                angle_diff = prev_v_angle - new_v_angle
                if abs(angle_diff) > 180:
                    if angle_diff < 0:
                        angle_diff = 360 - abs(angle_diff)
                    else:
                        angle_diff = -(360 - abs(angle_diff))

                self.obj.rotate(angle_diff)


class MapObject(pygame.sprite.Sprite):

    def __init__(self, group, x, y, color):
        super().__init__(group)
        self.image = pygame.Surface((0, 0))
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.float_x = x
        self.float_y = y
        self.render_float_x = x
        self.render_float_y = y
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.angle = 0

    def resize(self, w, h):
        self.rect.w += w
        self.rect.h += h
        if self.rect.w < 0:
            self.render_float_x = self.float_x + self.rect.w
        if self.rect.h < 0:
            self.render_float_y = self.float_y + self.rect.h

        self.image = pygame.Surface((abs(self.rect.w), abs(self.rect.h)))
        self.image.fill(self.color)
        # sprite_center_rotate(self, self.angle, False)


        # if figure == 'r':
        #     w, h, r, g, b, width, angle = 0, 0, 0, 0, 0, 0, 0
        #     self.float_x, self.float_y = x - w/2, y - h/2
        #     self.image = pygame.Surface((w, h))
        #     self.image.set_colorkey((0, 0, 0))
        #     pygame.draw.rect(self.image, (r, g, b), (0, 0, w, h), width)
        #     sprite_center_rotate(self, angle)
        #
        # if collide:
        #     self.mask = pygame.mask.from_surface(self.image)

    def rotate(self, angle):
        self.angle += angle
        sprite_center_rotate(self, self.angle, False)


if __name__ == '__main__':
    pygame.init()
    size = width, height = 2560, 1440
    screen = pygame.display.set_mode(size, flags=pygame.SCALED | pygame.FULLSCREEN)
    screen.fill((0, 0, 0))
    fps = 60
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    redactor = Redactor()
    font = pygame.font.Font(pygame.font.get_default_font(), 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            redactor.update(event)
            # all_sprites.update(event)

        screen.fill((0, 0, 0))
        redactor.update()

        pygame.display.flip()
        clock.tick(fps)