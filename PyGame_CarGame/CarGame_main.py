import math
import sys, os
import time

import pygame
from pygame.math import Vector2

# загрузка изображений
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# поворот спрайта по центру
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


# класс камера для слежения за машинкой
class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = self.dx + obj.float_x
        obj.rect.y = self.dy + obj.float_y

    def update(self, target):
        self.dx = width // 2 - target.float_x - target.rect.w / 2
        self.dy = height // 2 - target.float_y - target.rect.h / 2


# состояния игры
RUN = 1
LOSE = 2
WIN = 3


# класс игра, содержит все объекты и управляет ими
class CarGame:
    def __init__(self):
        self.load_images()
        self.map_objects = []
        self.collide_objects = []
        self.finish = None
        self.level = 1
        self.max_level = 2
        self.load_level()

    # загрузка текущего уровня
    def load_level(self):
        self.load_map()
        self.car = Car(all_sprites)
        self.car.float_x = 0
        self.car.float_y = 0
        self.time_start = time.time()
        self.time_amount = 60
        self.state = RUN

    # загрузка изображений
    def load_images(self):
        Car.image = load_image("car.png")

    # обновление кадра
    def update(self):
        self.car.update()

        camera.update(game.car)
        for sprite in all_sprites:
            camera.apply(sprite)

        if self.state == RUN:
            if self.car.rect.colliderect(self.finish.rect):
                game.win()
            else:
                left_time = self.time_amount - (time.time() - self.time_start)
                if left_time <= 0:
                    game.lose()

        all_sprites.draw(screen)

        if self.state == RUN:
            time_text = f'{round(left_time // 60)}:{round(left_time % 60)}'
            time_rend = font.render(time_text, 1, (255, 0, 0))
            time_rect = time_rend.get_rect(center=(width / 2, 50))
            screen.blit(time_rend, time_rect)

        speed = round(self.car.get_speed(), 2)
        speedometer = font.render(str(speed) + ' m/s', 1, (255, 0, 0))
        screen.blit(speedometer, (10, 10))
        pygame.draw.rect(screen, (255, 0, 0), (width / 2, height / 2, 1, 1))

        if self.state == LOSE or self.state == WIN:
            if self.state == LOSE:
                text = "ВРЕМЯ ВЫШЛО"
            else:
                text = "ВЫ ПОБЕДИЛИ!"
            label = font.render(text, 1, (255, 0, 0))
            label_rect = label.get_rect(center=(width / 2, 100))
            screen.blit(label, label_rect)

            if self.state == WIN and self.level > self.max_level:
                text = "ИГРА ЗАКОНЧЕНА!"
            elif self.state == WIN:
                text = "НАЖМИТЕ ENTER ДЛЯ ПЕРЕХОДА НА СЛЕДУЮЩИЙ УРОВЕНЬ"
            else:
                text = "НАЖМИТЕ ENTER ЧТОБЫ НАЧАТЬ СНАЧАЛА"

            label = font.render(text, 1, (255, 0, 0))
            label_rect = label.get_rect(center=(width / 2, 200))
            screen.blit(label, label_rect)

    # загрузка текущей карты
    def load_map(self):
        self.collide_objects.clear()
        self.map_objects.clear()

        map_name = 'map' + str(self.level) + '.txt'
        fullname = os.path.join('data', map_name)
        map_file = open(fullname, encoding="utf8")
        for s in map_file.readlines()[1:]:
            s = s.strip()
            args = s.split(';')
            if len(args) <= 1:
                continue
            obj = MapObject(all_sprites, *args)
            if args[0] == 'f':
                self.finish = MapObject(all_sprites, *args)
            if args[1] == '1':
                self.collide_objects.append(obj)
            else:
                self.map_objects.append(obj)

    # переход в выигрышное состояние
    def win(self):
        self.state = WIN
        self.level += 1

    # переход в проигрышное состояние
    def lose(self):
        self.state = LOSE
        self.level = 1


# класс - объект на карте
class MapObject(pygame.sprite.Sprite):
    background: pygame.Surface

    def __init__(self, group, *args):
        super().__init__(group)
        collide, x, y, w, h, r, g, b, angle = map(int, args[1:])
        self.float_x, self.float_y = x, y
        self.image = pygame.Surface((w, h))
        self.image.set_colorkey((0, 0, 0))
        self.image.fill((r, g, b))
        sprite_center_rotate(self, angle)

        if collide:
            self.mask = pygame.mask.from_surface(self.image)


# класс - машинка
class Car(pygame.sprite.Sprite):
    image: pygame.Surface

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Car.image
        self.rect = self.image.get_rect()
        self.float_x = 0 + self.rect.w / 2
        self.float_y = 0 + self.rect.h / 2

        self.update_rect()
        self.mass = 700 # масса машинки
        self.angle = 0 # угол машинки
        self.angle_change = 0 # изменение угла после 1 кадра
        self.thrust_force = 10000 # сила двигателя
        self.v = Vector2(0, 0) # вектор скорости в пикселях

    # установка размеров спрайта
    def update_rect(self):
        w = self.image.get_width()
        h = self.image.get_height()
        self.rect.w = w
        self.rect.h = h
        self.mask = pygame.mask.from_surface(self.image)

    # управление машинкой
    def update(self, *args):
        if not args:
            total_force = Vector2(0, 0)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                traction = self.thrust_force * Vector2(0, 1).rotate(self.angle)
                total_force += traction
            if keys[pygame.K_s]:
                traction = self.thrust_force * Vector2(0, 1).rotate(self.angle)
                total_force -= traction

            if not self.v and not total_force:
                return

            if keys[pygame.K_SPACE] and self.v:
                brake = 20000
                v_direct = self.v.normalize()
                brake_force = v_direct * brake
                if abs(self.v.x) + abs(self.v.y) < brake / self.mass / fps:
                    self.v = Vector2(0, 0)
                    return
                else:
                    total_force -= brake_force

            speed = self.get_speed()

            air_k = 0.4257
            air_force = self.v * speed ** 2 * air_k
            total_force -= air_force

            rr_k = 12.8
            rr_force = self.v * rr_k
            total_force -= rr_force

            # move_direct = (math.degrees(math.atan2(self.v.y, self.v.x)) + 270) % 360
            # angle_diff = self.angle - move_direct
            # if abs(angle_diff) > 180:
            #     if angle_diff < 0:
            #         angle_diff = 360 - abs(angle_diff)
            #     else:
            #         angle_diff = -(360 - abs(angle_diff))
            #
            # lateral_k = 100
            # angle_force = angle_diff * lateral_k

            self.apply_force(total_force)

            if keys[pygame.K_a]:
                self.angle_change -= 60 / fps
                self.rotate()
            if keys[pygame.K_d]:
                self.angle_change += 60 / fps
                self.rotate()

    def get_speed(self):
        speed = self.v.length()
        return speed

    def get_center(self):
        center_x = self.float_x + self.rect.w / 2
        center_y = self.float_y + self.rect.h / 2
        return center_x, center_y

    def apply_force(self, force):
        a = force / self.mass
        new_v = self.v + a / fps

        new_float_x = self.float_x - self.v.x * 20 / fps
        new_float_y = self.float_y - self.v.y * 20 / fps
        self.rect.x = new_float_x
        self.rect.y = new_float_y

        for obj in game.collide_objects:
            offset = new_float_x - obj.float_x, new_float_y - obj.float_y
            if obj.mask.overlap(self.mask, offset):
                self.v = Vector2(0, 0)
                self.rect.x = self.float_x
                self.rect.y = self.float_y
                return

        self.v = new_v
        self.float_x = new_float_x
        self.float_y = new_float_y

    def rotate(self):
        orig_center = self.image.get_rect().center
        new_angle = self.angle + self.angle_change
        self.angle_change = 0

        rotated_image = pygame.transform.rotate(Car.image, -new_angle)
        new_rect = rotated_image.get_rect()
        new_mask = pygame.mask.from_surface(rotated_image)
        new_center = new_rect.center
        offset_x = new_center[0] - orig_center[0]
        offset_y = new_center[1] - orig_center[1]
        new_float_x = self.float_x - offset_x
        new_float_y = self.float_y - offset_y

        for obj in game.collide_objects:
            offset = new_float_x - obj.float_x, new_float_y - obj.float_y
            if obj.mask.overlap(new_mask, offset):
                return

        self.rect = new_rect
        self.float_x = new_float_x
        self.float_y = new_float_y
        self.image = rotated_image
        self.mask = new_mask
        self.angle = new_angle % 360


# запуск игры
if __name__ == '__main__':
    # инициализация pygame
    pygame.init()
    size = width, height = 2560, 1440
    screen = pygame.display.set_mode(size, flags=pygame.SCALED | pygame.FULLSCREEN)
    screen.fill((0, 0, 0))
    fps = 60
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()

    # создание объектов
    game = CarGame()
    camera = Camera()
    font = pygame.font.Font(pygame.font.get_default_font(), 36)

    # основной цикл управления игрой
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game.state != RUN and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if game.level <= game.max_level:
                    game.load_level()
                else:
                    running = False
            all_sprites.update(event)

        screen.fill((0, 0, 0))
        game.update()

        pygame.display.flip()
        clock.tick(fps)
