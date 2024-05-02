from random import randint
from kivy.app import App
from kivy.uix.image import Image
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.vector import Vector
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.uix.button import Button


class Player(Image):
    score = NumericProperty(0)
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)

    def move(self):
        self.x += self.velocity_x
        self.y += self.velocity_y


class Enemy(Image):
    pass


class Bullet(Image):
    velocity = NumericProperty(10)

    def move(self):
        self.y += self.velocity
        if self.top < 0:
            return True


class SpaceGame(Widget):
    player = ObjectProperty(None)
    player_speed = 5

    def __init__(self, **kwargs):
        super(SpaceGame, self).__init__(**kwargs)
        self.size = (1100, 745)
        with self.canvas:
            self.background = Rectangle(source='background_image.png', size=self.size)
        self.enemies = []
        self.bullets = []
        self.player = Player(source='player_image.png')
        self.player.pos = self.center
        self.add_widget(self.player)  
        self._keyboard = Window.request_keyboard(None, self)
        self._keyboard.bind(on_key_down=self.on_key_down)
        self._keyboard.bind(on_key_up=self.on_key_up)
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.score_label = Label(text="Score: 0", font_size=20, pos=(0, self.height - 100))
        self.add_widget(self.score_label)
        self.restart_button = Button(text="Restart", size_hint=(None, None), size=(100, 50), pos=(10, 10))
        self.restart_button.bind(on_release=self.restart_game)

    def update(self, dt):
        self.player.move()
        self.keep_player_in_bounds()  
        self.spawn_enemies()
        self.move_enemies()
        self.move_bullets()
        self.check_collisions()
        self.update_score_label()

    def update_score_label(self):
        self.score_label.text = f"Score: {self.player.score}"

    def on_key_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'left':
            self.player.velocity_x = -self.player_speed
        elif keycode[1] == 'right':
            self.player.velocity_x = self.player_speed
        elif keycode[1] == 'up':
            self.player.velocity_y = self.player_speed
        elif keycode[1] == 'down':
            self.player.velocity_y = -self.player_speed
        elif keycode[1] == 'spacebar':
            self.fire_bullet()

    def on_key_up(self, keyboard, keycode):
        if keycode[1] in ('left', 'right'):
            self.player.velocity_x = 0
        elif keycode[1] in ('up', 'down'):
            self.player.velocity_y = 0

    def keep_player_in_bounds(self):
        if self.player.x < 0:
            self.player.x = 0
        elif self.player.right > self.width:
            self.player.right = self.width
        if self.player.y < 0:
            self.player.y = 0
        elif self.player.top > self.height:
            self.player.top = self.height

    def fire_bullet(self):
        bullet = Bullet(source='bullet_image.png')
        bullet.velocity = 10
        bullet.center_x = self.player.center_x
        bullet.top = self.player.top
        self.add_widget(bullet)
        self.bullets.append(bullet)

    def move_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.y > self.height:
                self.remove_widget(bullet)
                self.bullets.remove(bullet)

    def move_enemies(self):
        for enemy in self.enemies:
            enemy.y -= 3
            if enemy.top <= 0:
                self.remove_widget(enemy)
                self.enemies.remove(enemy)

    def spawn_enemies(self):
        if randint(1, 60) == 1:
            enemy = Enemy(source='enemy_image.png')
            enemy.x = randint(0, self.width - enemy.width)
            enemy.y = self.height
            self.add_widget(enemy)
            self.enemies.append(enemy)

    def check_collisions(self):
        for enemy in self.enemies:
            if self.player.collide_widget(enemy):
                self.game_over()
        for bullet in self.bullets:
            for enemy in self.enemies:
                if bullet.collide_widget(enemy):
                    self.remove_widget(bullet)
                    self.bullets.remove(bullet)
                    self.remove_widget(enemy)
                    self.enemies.remove(enemy)
                    self.player.score += 1
                    self.update_score_label()

    def game_over(self):
        self.clear_widgets()
        game_over_label = Label(text="Game Over!", font_size=50, center=self.center)
        final_score_label = Label(text=f"Final Score: {self.player.score}", font_size=30,
                                center_x=self.center_x, y=self.center_y - 100)
        self.add_widget(game_over_label)
        self.add_widget(final_score_label)
        self.restart_button = Button(text="Restart", size_hint=(None, None), size=(100, 50),
                                    pos=(self.center_x - 50, self.center_y - 150))
        self.restart_button.bind(on_release=self.restart_game)
        self.add_widget(self.restart_button)
        self.remove_widget(self.player)


    def restart_game(self, instance):
        self.clear_widgets()
        self.enemies = [] 
        for enemy in self.enemies:  
            self.remove_widget(enemy)
        self.bullets = []  
        self.player = Player(source='player_image.png')
        self.player.pos = self.center
        self.add_widget(self.player)
        self.player.score = 0  
        self.add_widget(self.score_label)  
        self.update_score_label()  

class SpaceApp(App):
    def build(self):
        return SpaceGame()

if __name__ == '__main__':
    SpaceApp().run()
