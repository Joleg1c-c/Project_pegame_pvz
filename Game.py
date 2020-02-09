import pygame
import sys
import os
import random
import time

# берёт значения FPS из текставого файла
take_snach = open("text/settings.txt", encoding='utf8').read().split()
FPS = int(take_snach[2])


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Monster(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(Monster_group, all_sprites)
        self.pos = (pos_x, pos_y)
        self.const = (pos_x, pos_y)
        # проигрыш
        self.game_over = 0
        # эффекс заморозки
        self.cold = 0
        # скорость передвижения
        self.kof_speed = 0.125
        # кол-во здоровья
        self.xp = 100
        # урон от зомби
        self.power = 10
        # начальный заряд перезарядки удара
        self.accum = 0
        # скорость удара
        self.accum_speed = 5
        # анимация движения
        self.now = 0
        self.now_hit = 0
        self.image_list_move = image[0]
        self.image_list_hit = image[1]
        self.image = pygame.transform.scale(load_image(self.image_list_move[self.now % 4], -1),
                                            (hero_width, hero_height))
        self.stand_x = tile_left + tile_width * pos_x + 10
        self.stand_y = tile_top + tile_height * pos_y + 10

        self.rect = self.image.get_rect().move(self.stand_x,
                                               self.stand_y)

    # переобразовывает значения
    def pererab(self, spisok):
        self.kof_speed = spisok[0]
        self.accum_speed = spisok[1]
        self.xp = spisok[2]
        self.power = spisok[3]

    # проверка на проигрыш
    def game_over(self):
        return self.game_over

    def damage(self, xp):
        self.xp -= xp
        pygame.mixer.music.load('data/splat.mp3')
        pygame.mixer.music.play()
        if self.xp <= 0:
            self.kill()

    # замедляет монстра
    def freezing(self):
        self.cold = 100

    def check(self):
        return (self.stand_x, self.const[1])

    def hit(self):
        return self.power

    # накопление энергии для удара
    def accumulation(self):
        self.now_hit += 1
        if self.now_hit % 8 == 0:
            self.image = pygame.transform.scale(load_image(self.image_list_hit[(self.now_hit // 8) % 4], -1),
                                                (hero_width, hero_height))
        self.accum += self.accum_speed
        if self.accum >= 100:
            self.accum = 0
            return True
        else:
            return False

    def move(self, x, y):
        self.pos = (x, y)
        f = 1
        if self.cold > 0:
            f = 0.5
        self.now += 1
        if self.now % 8 == 0:
            self.image = pygame.transform.scale(load_image(self.image_list_move[(self.now // 8) % 4], -1),
                                                (hero_width, hero_height))
        self.stand_x += speed * self.kof_speed * self.pos[0] * f
        self.rect = self.image.get_rect().move(self.stand_x, self.stand_y)
        if self.stand_x < 0:
            self.game_over = 1


class Defender(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image, tile_top):
        super().__init__(Defender_group, all_sprites)
        self.pos = (pos_x, pos_y)
        self.pos_cons = (pos_x, pos_y)
        # id пуль
        self.id = "bullet_standart"
        # скорострельность
        self.accum_speed = 0.8
        # начальный заряд перезарядки патронов
        self.accum = 0
        # кол-во здоровья
        self.xp = 100
        self.image = pygame.transform.scale(load_image(image, -1), (hero_width, hero_height))
        self.stand_x = tile_left + tile_width * pos_x + 10
        self.stand_y = tile_top + tile_height * pos_y + 10

        self.rect = self.image.get_rect().move(self.stand_x,
                                               self.stand_y)

    def check(self):
        return (self.stand_x, self.pos_cons[1], self.pos)

    def pererab(self, develop):
        self.accum_speed = develop[0]
        self.xp = develop[1]
        self.id = develop[2]

    # возвращает тип защитника
    def tipe(self):
        return self.id

    def damage(self, xp):
        self.xp -= xp
        if self.xp <= 0:
            pygame.mixer.music.load('data/gulp.mp3')
            pygame.mixer.music.play()
            self.kill()

    # накопление энергии для выстрела
    def accumulation(self):
        self.accum += self.accum_speed
        if self.accum >= 100:
            shot((self.pos[0], self.pos[1]), self.id)
            self.accum = 0


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image):
        super().__init__(Bullet_group, all_sprites)
        self.pos = (pos_x, pos_y)
        self.pos_cons = (pos_x, pos_y)
        # тип пули
        self.tipe_bullet = image[:-4]
        # скорость пули
        self.speed_move = 3
        # урон
        self.damage = 10
        self.image = pygame.transform.scale(load_image(image, -1), bullen_rise[image])
        self.stand_x = tile_left + tile_width * pos_x + 10
        self.stand_y = tile_top + tile_height * pos_y + 10

        self.rect = self.image.get_rect().move(self.stand_x,
                                               self.stand_y)

    def check(self):
        return (self.stand_x, self.pos_cons[1], self.stand_y)

    def pererab(self, mov):
        self.speed_move = mov

    # возвращает тип пули
    def tipe(self):
        return self.tipe_bullet

    def hit(self):
        return self.damage

    def move(self, x, y):
        self.pos = (x, y)
        self.stand_x += speed * self.speed_move * self.pos[0]

        self.rect = self.image.get_rect().move(self.stand_x, self.stand_y)

        # проверка на смерть или касания монстра  or hurt((self.stand_x, self.stand_y, self.poser[0], self.poser[1]))
        if self.stand_x > width + 50:
            self.kill()


class Choice_board:
    # создание поля для выбора защитника
    def __init__(self, width, height, showcase):
        self.width = width + 2
        self.height = height
        self.height = 1
        self.board = [[0] * self.width for _ in range(height)]
        # счёт пыльцы
        self.col_vo_pollen = 2
        # список с растениями, из которых можно выбрать, что поставить
        self.showcase = showcase
        # проверка на то, находится ли там кто-то
        self.state = []
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # подсвечивает выбранное поле и убирает подсветку у других полей
    def red(self, coor):
        pygame.mixer.music.load('data/buzzer.mp3')
        pygame.mixer.music.play()
        self.board = [[0] * self.width for _ in range(self.height)]
        if coor != None:
            for i in range(self.width):
                if i * self.cell_size + self.left + self.cell_size > coor > i * self.cell_size + self.left:
                    self.board[0][i] = 2
                    break

    # подсвечивает выбранное поле и убирает подсветку у других полей
    def sero(self, coor):
        self.board = [[0] * self.width for _ in range(self.height)]
        if coor != None:
            for i in range(self.width):
                if i * self.cell_size + self.left + self.cell_size > coor > i * self.cell_size + self.left:
                    self.board[0][i] = 1
                    break

    def take_pollen(self):
        self.col_vo_pollen += 1
        pygame.mixer.music.load('data/chime.mp3')
        pygame.mixer.music.play()

    def buy_za_pollen(self, hoy):
        self.col_vo_pollen -= hoy

    def hou_pollen(self):
        return self.col_vo_pollen

    # обработка клика
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell != None:
            return self.on_click(cell)
        else:
            return None

    def get_cell(self, cell_coords):
        s = []
        for i in range(1, self.width):
            if i * self.cell_size + self.left + self.cell_size > cell_coords[0] > i * self.cell_size + self.left:
                s.append(i)
                break
        if self.top + self.cell_size > cell_coords[1] > self.top:
            s.append(1)
        if len(s) < 2:
            return None
        else:
            return s

    def on_click(self, cell_coords):
        if cell_coords[0] < len(self.showcase):
            self.board[0][cell_coords[0]] = 1
            return self.showcase[cell_coords[0]]

        elif cell_coords[0] == self.width - 1:
            return "potions"

    def posichion(self):
        return [self.left, self.top, self.cell_size]

    def render(self):
        pol_size = self.cell_size // 2
        pygame.draw.circle(screen, (255, 255, 255), (self.left + pol_size, self.top + pol_size), pol_size, 1)

        # показатель пыльцы
        font = pygame.font.Font(None, 30)
        text = font.render(str(self.col_vo_pollen), 1, (100, 255, 100))
        if self.col_vo_pollen < 10:
            screen.blit(text, (self.left + self.cell_size // 3 + 4, self.top + self.cell_size // 3 - 1))
        else:
            screen.blit(text, (self.left + self.cell_size // 3 - 3, self.top + self.cell_size // 3 - 1))

        # создаем само поле для выбора защитников
        choicen = {0: (255, 255, 255), 1: (255, 215, 0), 2: (255, 0, 0)}
        for i in range(1, self.width):
            pygame.draw.rect(screen, choicen[self.board[0][i]],
                             [i * self.cell_size + self.left, self.top, self.cell_size,
                              self.cell_size], 1)

            if i < len(self.showcase):
                screen.blit(
                    pygame.transform.scale(load_image(spisok_defenders_image[self.showcase[i]], -1), (self.cell_size,
                                                                                                      self.cell_size)),
                    (i * self.cell_size + self.left, self.top))

            # cоздания элексира, который убирает защитников
            elif i == self.width - 1:
                screen.blit(
                    pygame.transform.scale(load_image("potions.png", -1), (self.cell_size, self.cell_size)),
                    (i * self.cell_size + self.left, self.top))


class Game_board:
    # создание игрового поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # проверка на то, находится ли там кто-то
        self.state = []
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # обработка клика
    def get_click(self, mouse_pos, id):
        if id == None:
            return False
        cell = self.get_cell(mouse_pos)
        if cell != None:
            if self.on_click(cell, id):
                return True
        return False

    def on_click(self, cell_coords, id):
        # если выбран potions, то проверяется, попал ли он по растению
        if id == "potions":
            if cell_coords in self.state:
                for i in defenders:
                    if list(i.check()[2]) == cell_coords:
                        pygame.mixer.music.load('data/shovel.mp3')
                        pygame.mixer.music.play()
                        i.kill()

        elif cell_coords not in self.state:
            self.state.append(cell_coords)
            defender_spavn(cell_coords, id)
            return True
        else:
            return False

    # удаление занятого места, где нет цветка
    def delate(self, cor):
        self.state.pop(self.state.index([cor[0], cor[1]]))

    def get_cell(self, cell_coords):
        s = []
        for i in range(self.width):
            if i * self.cell_size + self.left + self.cell_size > cell_coords[0] > i * self.cell_size + self.left:
                s.append(i)
                break
        for j in range(self.height):
            if j * self.cell_size + self.top + self.cell_size > cell_coords[1] > j * self.cell_size + self.top:
                s.append(j)
                break
        if len(s) < 2:
            return None
        else:
            return s

    def posichion(self):
        return [self.left, self.top, self.cell_size]

    def render(self):
        # карта
        # screen.blit(pygame.transform.scale(load_image("map.png"), (width, height)), (0, 0))
        for i in range(self.width):
            for j in range(self.height):
                pygame.draw.rect(screen, (255, 255, 255),
                                 [i * self.cell_size + self.left, j * self.cell_size + self.top, self.cell_size,
                                  self.cell_size], 1)


class Game_menu:
    # создание игрового поля
    def __init__(self, height):
        self.height = height
        # проверка на то, находится ли там кто-то
        self.state = []
        # типы штук в меню
        self.menu = ["Играть", "Помощь", "Выход"]
        # подсвечины ли они
        self.tipe = [0, 0, 0]
        # размеры
        self.size_menu = {"Играть": (170, 70), "Помощь": (200, 70), "Выход": (170, 70)}
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # что именно выбрали
    def what(self, number):
        if number != None:
            return self.menu[number]

    # подсвечивает выбранную
    def light(self, number):
        if number != None:
            self.tipe[number] = 1
        else:
            self.tipe = [0, 0, 0]

    # обработка клика
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell != None:
            return self.on_click(cell)

    def on_click(self, cell_coords):
        return cell_coords[-1]

    def get_cell(self, cell_coords):
        s = []

        for j in range(self.height):
            if self.left + self.size_menu[self.menu[j]][0] > cell_coords[0] > self.left:
                s.append(1)
            if j * self.cell_size + self.top + self.size_menu[self.menu[j]][1] > cell_coords[
                1] > j * self.cell_size + self.top:
                s.append(j)
            if len(s) > 1:
                break
            else:
                s = []

        if len(s) < 2:
            return None
        else:
            return s

    def render(self):
        for j in range(self.height):
            # кнопки
            font = pygame.font.Font(None, 70)
            if self.tipe[j]:
                text = font.render(self.menu[j], 1, (255, 255, 255))
            else:
                text = font.render(self.menu[j], 1, (110, 110, 110))
            screen.blit(text, (self.left, self.top + j * self.cell_size))


class Difficult:
    # создание игрового поля
    def __init__(self, height):
        self.height = height
        # проверка на то, находится ли там кто-то
        self.state = []
        # типы штук в меню
        self.menu = ["Нормально", "Сложно"]
        # подсвечины ли они
        self.tipe = [0, 0]
        # размеры
        self.size_menu = {"Нормально": (390, 70), "Сложно": (280, 70)}
        # значения по умолчанию
        self.left = 10
        self.top = 10
        self.cell_size = 30

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    # что именно выбрали
    def what(self, number):
        if number != None:
            return self.menu[number]

    # подсвечивает выбранную
    def light(self, number):
        if number != None:
            self.tipe[number] = 1
        else:
            self.tipe = [0, 0]

    # обработка клика
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell != None:
            return self.on_click(cell)

    def on_click(self, cell_coords):
        return cell_coords[-1]

    def get_cell(self, cell_coords):
        s = []

        for j in range(self.height):
            if self.left + self.size_menu[self.menu[j]][0] > cell_coords[0] > self.left:
                s.append(1)
            if j * self.cell_size + self.top + self.size_menu[self.menu[j]][1] > cell_coords[
                1] > j * self.cell_size + self.top:
                s.append(j)
            if len(s) > 1:
                break
            else:
                s = []

        if len(s) < 2:
            return None
        else:
            return s

    def render(self):
        for j in range(self.height):
            # кнопки
            font = pygame.font.Font(None, 100)
            if self.tipe[j]:
                text = font.render(self.menu[j], 1, (255, 255, 255))
            else:
                text = font.render(self.menu[j], 1, (110, 110, 110))
            screen.blit(text, (self.left, self.top + j * self.cell_size))


class Help:
    # создание игрового поля
    def __init__(self):
        self.height = height
        self.width = width
        # размеры
        self.size_klava = (150, 70)
        # подсветка
        self.tipe_lifgt = 0
        # значения по умолчанию
        self.left = 10
        self.top = 10

    # настройка внешнего вида
    def set_view(self, left, top):
        self.left = left
        self.top = top

    # подсвечивает выбранную
    def light(self, number):
        if number != None:
            self.tipe_lifgt = 1
        else:
            self.tipe_lifgt = 0

    # обработка клика
    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell != None:
            return True

    def get_cell(self, cell_coords):
        s = []

        if self.left + self.size_klava[0] > cell_coords[0] > self.left:
            s.append(1)
        if height - self.top - 10 + self.size_klava[1] > cell_coords[1] > height - self.top + 10:
            s.append(1)

        if len(s) < 2:
            return None
        else:
            return s

    def render(self):
        # карта
        screen.blit(load_image("проверка1.bmp"), (self.left, self.top))

        # обьяснение
        font = pygame.font.Font(None, 70)
        text = font.render("Общее обьяснение", 1, (255, 255, 255))
        screen.blit(text, (self.left + 5, 0))

        # кнопка назад
        font = pygame.font.Font(None, 70)
        if self.tipe_lifgt == 1:
            text = font.render("назад", 1, (255, 255, 255))
        else:
            text = font.render("назад", 1, (110, 110, 110))
        screen.blit(text, (self.left, height - self.top))


# проверяет щелчёк мыши, попал ли он по кому-то(в виде класса)
def click(pos_mouse, kto):
    right_point = kto.check()[0] + hero_width * 7 // 10
    down_point = kto.check()[2] + hero_width * 7 // 10
    if kto.check()[0] < pos_mouse[0] < right_point and kto.check()[2] < pos_mouse[1] < down_point:
        return True
    return False


# есть ли кто-то(в виде класса) кого-то(в виде списка с классами) на одной линии
def common_line(kto, kogo):
    f = None
    for i in kogo:
        if i.check()[1] == kto.check()[1]:
            f = i
    return f


# задела ли кто-то(в виде класса) кого-то(в виде списка с классами)
def hurt(kto, kogo, tipe_kto, tipe_kogo):
    id = {"def": hero_width, "mon": hero_width,
          "but": hero_width // 2}
    f = None
    for i in kogo:
        if i.check()[1] != kto.check()[1]:
            continue
        if i.check()[0] < kto.check()[0] + id[tipe_kto] < i.check()[0] + id[tipe_kogo] or i.check()[0] < kto.check()[
            0] < i.check()[0] + id[tipe_kogo]:
            f = i
    return f


# смерть (проверка классов, есть ли они в списке)
def death(spisok, id=None):
    f = 1
    while f == 1:
        f = 0
        for i in range(len(spisok)):
            if spisok[i] not in all_sprites:
                if id != None:
                    board.delate(spisok[i].check()[2])
                spisok.pop(i)
                f = 1
                break


def move(hero, mov):
    if mov == "up":
        hero.move(0, -1)

    if mov == "down":
        hero.move(0, 1)

    if mov == "left":
        hero.move(-1, 0)

    if mov == "right":
        hero.move(1, 0)


# спавн защитника
def defender_spavn(cell_coords, tipe):
    spisok_defender_tipe = {"defender_standart": (const["normal_defender_accum_speed"], const["normal_xp"],
                                                  bullen_tipe[tipe]),

                            "defender_pollen_given": (const["low_defender_accum_speed"], const["normal_xp"],
                                                      bullen_tipe[tipe]),

                            "defender_slower": (const["normal_defender_accum_speed"], const["normal_xp"],
                                                bullen_tipe[tipe]),

                            "defender_stend": (0, const["very_high_xp"], bullen_tipe[tipe])}

    defe = Defender(cell_coords[0], cell_coords[1], spisok_defenders_image[tipe], tile_top)
    defe.pererab(spisok_defender_tipe[tipe])
    defenders.append(defe)


# спавн монстра
def monster_spavn():
    spisok_monsters_tipe = {"monster_standart": (const["normal_move_speed"], const["normal_monster_accum_speed"],
                                                 const["normal_xp"], const["normal_power"]),

                            "monster_speed": (const["fast_move_speed"], const["low_monster_accum_speed"],
                                              const["normal_xp"], const["low_power"]),

                            "monster_easy_tank": (const["normal_move_speed"], const["normal_monster_accum_speed"],
                                                  const["medium_xp"], const["normal_power"])}
    tipe = random.choice(monsters_tipe)
    image = spisok_monsters_image[tipe]

    monster = Monster(random.randint(10, 12) + random.randint(1, 9) * 0.1, random.randint(0, 4), image)
    monsters.append(monster)
    monster.pererab(spisok_monsters_tipe[tipe])


# спавн пули
def shot(position, image_id):
    id = {"bullet_standart": 3, "pollen": 0, "ice": 3}
    bullet = Bullet(position[0] - random.randint(0, 2) * 0.1 + random.randint(0, 4) * 0.1, position[1],
                    spisok_bullen_image[image_id])
    bullet.pererab(id[image_id])
    bullets.append(bullet)


pygame.init()
size = width, height = 500, 400
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
pygame.display.set_caption("The Insurrection")
sound1 = pygame.mixer.Sound('data/Utopia Close.wav')

# группы спрайтов
all_sprites = pygame.sprite.Group()
Bullet_group = pygame.sprite.Group()
Defender_group = pygame.sprite.Group()
Monster_group = pygame.sprite.Group()
end_game = pygame.sprite.Group()

# поле 5 на 7
board = Game_board(8, 5)
board.set_view(10, 100, 50)

# поле для выбора защитника
defender_tipe = ["defender_standart", "defender_pollen_given", "defender_stend", "defender_slower"]
s = ["его вы никогда не увидете ;)"]
s.extend(defender_tipe)
choice_board = Choice_board(5, 1, s)
choice_board.set_view(10, 10, 50)

# иницилизация констандных переменных (размер)
tile_width = tile_height = board.posichion()[2]
tile_left = board.posichion()[0]
tile_top = board.posichion()[1]
tile_top_choice = choice_board.posichion()[1]
speed = 1
hero_width = hero_height = 30

# настройка видов дефендеров, монстров и пуль
# защитники
spisok_defenders_image = {"defender_standart": "defender_standart.png",
                          "defender_pollen_given": "defender_pollen_given.png",
                          "defender_stend": "defender_stend.png",
                          "defender_slower": "defender_slower.png"}

# монстры
monsters_tipe = ["monster_standart", "monster_standart", "monster_standart", "monster_speed", "monster_standart",
                 "monster_speed", "monster_easy_tank"]

spisok_monsters_image = {
    "monster_standart": [['11.jpg', '12.jpg', '13.jpg', '14.jpg'], ['21.jpg', '22.jpg', '23.jpg', '24.jpg']],
    "monster_speed": [['31.jpg', '32.jpg', '33.jpg', '34.jpg'], ['41.jpg', '42.jpg', '43.jpg', '44.jpg']],
    "monster_easy_tank": [['51.jpg', '52.jpg', '53.jpg', '54.jpg'], ['61.jpg', '62.jpg', '63.jpg', '64.jpg']]}

# пули
spisok_bullen_image = {"bullet_standart": "bullet_standart.png", "pollen": "pollen.png",
                       "ice": "ice.png"}

bullen_tipe = {"defender_standart": "bullet_standart", "defender_pollen_given": "pollen",
               "defender_stend": "а ты попробуй увидеть меня))", "defender_slower": "ice"}

bullen_rise = {"bullet_standart.png": (hero_width // 2, hero_height // 2),
               "pollen.png": (hero_width * 7 // 10, hero_height * 7 // 10),
               "ice.png": (hero_width // 2, hero_height // 2)}

# константные переменные
const = {"normal_move_speed": 0.125, "fast_move_speed": 0.25,  # скорость движения монстра
         "normal_xp": 100, "medium_xp": 300, "high_xp": 600, "very_high_xp": 1500,  # здоровье спрайтов
         "low_monster_accum_speed": 5, "normal_monster_accum_speed": 10,  # скорость удара монстра
         "low_power": 7, "normal_power": 10,  # урон монстра
         "low_defender_accum_speed": 0.25, "normal_defender_accum_speed": 0.5  # скорострельность защитника
         }

# меню
board_menu = Game_menu(3)
board_menu.set_view(10, 50, 70)

help = Help()
help.set_view(10, 70)

start_glav_menu, start_help = True, False
running_menu = True
running = False
choice_diff = False
helper = False
while running_menu:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_menu = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # обрабатывает клики
            if start_glav_menu:
                kto_menu = board_menu.get_click(event.pos)

                if board_menu.what(kto_menu) == "Выход":
                    sound1.play()
                    running_menu = False

                elif board_menu.what(kto_menu) == "Играть":
                    sound1.play()
                    running_menu = False
                    choice_diff = True
                    running = True

                elif board_menu.what(kto_menu) == "Помощь":
                    sound1.play()
                    help.light(None)
                    start_glav_menu = False
                    start_help = True

            if start_help:
                kto_help = help.get_click(event.pos)
                if kto_help:
                    sound1.play()
                    board_menu.light(None)
                    start_glav_menu = True
                    start_help = False

        if event.type == pygame.MOUSEMOTION:
            # подсвечивает при касании
            if start_glav_menu:
                board_menu.light(None)
                kto_menu = board_menu.get_click(event.pos)
                if kto_menu != None:
                    board_menu.light(kto_menu)

            if start_help:
                help.light(None)
                kto_help = help.get_click(event.pos)
                if kto_help != None:
                    help.light(kto_help)

    screen.fill((0, 0, 0))

    if start_glav_menu:
        board_menu.render()

    if start_help:
        help.render()

    pygame.display.flip()
    clock.tick(FPS)

# выбор сложности
Diff = Difficult(2)
Diff.set_view(10, 100, 100)
diffic = "Нормально"
while choice_diff:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            choice_diff = False
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            kto_menu = Diff.get_click(event.pos)

            if Diff.what(kto_menu) == "Нормально":
                sound1.play()
                diffic = "Нормально"
                choice_diff = False

            elif Diff.what(kto_menu) == "Сложно":
                sound1.play()
                diffic = "Сложно"
                choice_diff = False

        if event.type == pygame.MOUSEMOTION:
            Diff.light(None)
            kto_menu = Diff.get_click(event.pos)
            if kto_menu != None:
                Diff.light(kto_menu)

    screen.fill((0, 0, 0))
    Diff.render()
    pygame.display.flip()
    clock.tick(FPS)

# проверка на то, запускается ли эта игра впервые
# запускает сюжет
if int(take_snach[5]) == 0 and running:
    perezapic = open('text/settings.txt', 'w', encoding='utf8')
    perezapic.write("FPS = {}\nSTART = {}".format(take_snach[2], 1))
    perezapic.close()
    Fail = True
    x = height
    # заставка
    while Fail:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                Fail = False
                helper = True
        if x < -664:
            Fail = False
            helper = True

        screen.blit(load_image("s1200 (2) — копия.jpg"), (0, x))
        x -= 0.3

        pygame.display.flip()
        clock.tick(FPS)

# если игра запускается впервые, то запускается подсказка
while helper:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            helper = False
    screen.blit(load_image("проверка1.bmp"), (0, height / 2 - 247 // 2))

    # подсказка
    font = pygame.font.Font(None, 60)
    text = font.render("Подсказка как играть", 1, (255, 255, 255))
    screen.blit(text, (5, 10))

    font = pygame.font.Font(None, 40)
    text = font.render("нажмите любую клавишу", 1, (255, 255, 255))
    screen.blit(text, (10, 350))

    pygame.display.flip()
    clock.tick(FPS)

# стоимость защитников
shop_defender = {None: 10000, "defender_standart": 4, "defender_pollen_given": 2, "defender_stend": 2, "potions": 0,
                 "defender_slower": 6}

# список с классоми защитников, пули, монстрами
defenders = []
bullets = []
monsters = []

# настройки спавна зомби
cd_zom_sp = 100
zom_sp = 0.125
kol_waves = 3

over, win = False, False
defen = None
defen_pro = None
stop = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if stop:
                mouse_position = event.pos
                defen_pro = choice_board.get_click(mouse_position)

            if choice_board.hou_pollen() >= shop_defender[defen_pro] and defen != defen_pro:
                choice_board.sero(event.pos[0])
                defen = defen_pro
                pygame.mixer.music.load('data/tap.mp3')
                pygame.mixer.music.play()

            elif defen == defen_pro and defen != None:
                choice_board.sero(None)
                defen = None

            elif defen_pro != None:
                choice_board.red(event.pos[0])
                defen = None

            if board.get_click(event.pos, defen):
                choice_board.buy_za_pollen(shop_defender[defen])
                choice_board.sero(None)
                pygame.mixer.music.load('data/plant.mp3')
                pygame.mixer.music.play()
                defen = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                stop = True
            if event.key == pygame.K_DOWN:
                stop = False
                pygame.mixer.music.load('data/pause.mp3')
                pygame.mixer.music.play()
            if event.key == pygame.K_q:
                monsters[-1].kill()

    if stop:
        # спавн
        if cd_zom_sp <= 0:
            if kol_waves > 0:
                pygame.mixer.music.load('data/awooga.mp3')
                pygame.mixer.music.play()
                sp = {"Нормально": 5, "Сложно": 10}
                f = 7
                for i in range(sp[diffic]):
                    monster_spavn()
                kol_waves -= 1
                cd_zom_sp = 300
        if kol_waves == 0 and monsters == []:
            win = True
            break
        cd_zom_sp -= zom_sp

        # ход монстров
        for i in monsters:
            if i not in all_sprites:
                monsters.remove(i)

            defender_popalsja = hurt(i, defenders, "mon", "def")
            if defender_popalsja != None:
                # готовность ударить зомби
                gotovnpst = i.accumulation()
                if gotovnpst:
                    defenders[defenders.index(defender_popalsja)].damage(i.hit())

            else:
                move(i, "left")
                if i.game_over:
                    over = True
                    break
        if over:
            break

        # ход защитников
        for i in defenders:
            # проверка на смерть защитников
            if i not in all_sprites:
                board.delate(i.check()[2])
                defenders.remove(i)

            if i.tipe() == "pollen":
                i.accumulation()

            elif i.tipe() == "bullet_standart" or i.tipe() == "ice":
                somebody = common_line(i, monsters)
                if somebody != None:
                    i.accumulation()

        # пуля ход и попадание
        for i in bullets:
            # проверка на смерть пули
            if i not in all_sprites:
                Bullet_group.remove(i)
                bullets.remove(i)

            if i.tipe() == "defender_stend":
                continue

            elif i.tipe() == "pollen":
                if click(mouse_position, i):
                    choice_board.take_pollen()
                    i.kill()

            elif i.tipe() == "ice":
                move(i, "right")
                monst_popalsja = hurt(i, monsters, "but", "mon")
                if monst_popalsja != None:
                    monsters[monsters.index(monst_popalsja)].damage(i.hit())
                    monsters[monsters.index(monst_popalsja)].freezing()
                    i.kill()

            elif i.tipe() == "bullet_standart":
                move(i, "right")
                monst_popalsja = hurt(i, monsters, "but", "mon")
                if monst_popalsja != None:
                    monsters[monsters.index(monst_popalsja)].damage(i.hit())
                    i.kill()

    mouse_position = (-1, -1)
    choice_board.render()
    board.render()
    all_sprites.draw(screen)
    if stop == False:
        screen.blit(pygame.transform.scale(load_image("pause.png", -1), (250, 250)), (90, 70))

    pygame.display.flip()
    clock.tick(FPS)

if over or win:
    sprite = pygame.sprite.Sprite()
    if over:
        sprite.image = pygame.transform.scale(load_image("game.jpg"), (500, 400))
        pygame.mixer.music.load('data/scream.mp3')
        pygame.mixer.music.play()
    else:
        sprite.image = pygame.transform.scale(load_image("win.jpg", -1), (500, 400))
        pygame.mixer.music.load('data/finalfanfare.mp3')
        pygame.mixer.music.play()
    sprite.rect = sprite.image.get_rect()
    end_game.add(sprite)
    sprite.rect.x = -500
    sprite.rect.y = 0

    MYEVENTTYPE = 30
    pygame.time.set_timer(MYEVENTTYPE, 10)

    cx = 2
    running_over = True
    while running_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_over = False
            if event.type == MYEVENTTYPE:
                sprite.rect.x += cx
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                running_over = False

        if sprite.rect.x >= 0:
            cx = 0
        choice_board.render()
        board.render()
        all_sprites.draw(screen)
        end_game.draw(screen)
        pygame.display.flip()
