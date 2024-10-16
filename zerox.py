import pygame
import math
import random

pygame.init()
pygame.mixer.init()
    
class Game():

    delta_time = 0
    running = True
    EXPLOSION_SOUND = pygame.mixer.Sound("sounds/explosion sound.wav")
    EXPLOSION_IMAGES = None
    METEOR_IMAGES = None
    PLAYER_IMAGE = None
    SPACE_STATION_IMAGES = None
    POWERUP_IMAGES = None
    SHIELD_IMAGE = None
    joysticks = []
    
    def __init__(self):
        pygame.mouse.set_visible(False)
        pygame.mixer.set_num_channels(16)
        pygame.mixer.music.load("music/constellation.ogg")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(loops=-1)
        window_icon = pygame.image.load("images/window icon.png")
        window_icon = pygame.transform.smoothscale(window_icon,(32,32))
        pygame.display.set_icon(window_icon)
        Game.setup_images()
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((800,600))
        self.all_sprites = pygame.sprite.LayeredUpdates()
        space_stations = pygame.sprite.Group()
        meteors = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        pygame.display.set_caption("Zerox")
        self.player = Player(pygame.Vector2(800 / 2,530),self.all_sprites,space_stations,meteors,powerups)
        self.all_sprites.add(self.player,layer=0)
        self.space_background = pygame.image.load("images/space background.png")
        background_width = self.space_background.get_width()
        background_height = self.space_background.get_height()
        self.space_background = pygame.transform.smoothscale_by(self.space_background,(800/background_width,600/background_height))
        self.meteor_spawner = MeteorSpawner(self.all_sprites,meteors)
        self.space_station_spawner = SpaceStationSpawner(self.all_sprites,space_stations)
        self.powerup_spawner = PowerupSpawner(self.all_sprites,powerups,self.player)
            
    def poll_events(self):
        Game.delta_time = self.clock.tick(self.fps) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                Game.running = False
            if event.type == pygame.JOYDEVICEADDED:
                joystick = pygame.joystick.Joystick(event.device_index)
                Game.joysticks.append(joystick)

    def update(self):
        self.meteor_spawner.update()
        self.space_station_spawner.update()
        self.powerup_spawner.update()
        self.all_sprites.update()

    def draw(self):
        self.window.blit(self.space_background,(0,0))
        self.all_sprites.draw(self.window)
        Game.draw_text(self.window,pygame.Vector2(800 / 2,20),"Score:"+str(self.player.score),20)
        Game.draw_health_bar(self.window,pygame.Vector2(50,25),self.player.start_health,self.player.health)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.poll_events()
            self.update()
            self.draw()

    @staticmethod
    def draw_text(window,pos,text,size):
        font = pygame.font.Font("fonts/future.ttf",size)
        text_image = font.render(text,True,pygame.Color(255,255,255))
        text_rect = text_image.get_rect()
        text_rect.midtop = (pos.x,pos.y)
        window.blit(text_image,text_rect)

    @staticmethod
    def draw_health_bar(window,pos,start_health,health):
        if health < 0:
            health = 0
        BAR_LENGTH = 120
        BAR_HEIGHT = 10
        fill = (health / start_health) * BAR_LENGTH
        red_bar = pygame.Rect(pos.x,pos.y,BAR_LENGTH,BAR_HEIGHT)
        green_bar = pygame.Rect(pos.x,pos.y,fill,BAR_HEIGHT)
        outline = pygame.Rect(pos.x,pos.y,BAR_LENGTH,BAR_HEIGHT)
        pygame.draw.rect(window,pygame.Color(237,76,76),red_bar,border_radius=3)
        pygame.draw.rect(window,pygame.Color(14,247,134),green_bar,border_radius=3)
        
    @staticmethod
    def setup_images():
        explosion_paths = ["images/explosion 1.png","images/explosion 2.png",
                        "images/explosion 3.png","images/explosion 4.png",
                        "images/explosion 5.png","images/explosion 6.png",
                        "images/explosion 7.png","images/explosion 8.png","images/explosion 9.png"]
        meteor_paths = ["images/meteor big 1.png",
                    "images/meteor big 2.png","images/meteor big 3.png","images/meteor big 4.png",
                    "images/meteor medium 1.png","images/meteor medium 2.png"]
        space_station_paths = ["images/space station 1.png","images/space station 2.png"]
        Game.EXPLOSION_IMAGES = Game.load_images(explosion_paths)
        Game.EXPLOSION_IMAGES = Game.scale_images(Game.EXPLOSION_IMAGES,2)
        Game.METEOR_IMAGES = Game.load_images(meteor_paths)
        Game.METEOR_IMAGES = Game.scale_images(Game.METEOR_IMAGES,1.5)
        Game.SPACE_STATION_IMAGES = Game.load_images(space_station_paths)
        Game.SPACE_STATION_IMAGES = Game.scale_images(Game.SPACE_STATION_IMAGES,0.65)
        space_station_image3 = pygame.image.load("images/space station 3.png")
        space_station_image3 = pygame.transform.smoothscale_by(space_station_image3,0.65)
        Game.SPACE_STATION_IMAGES.append(space_station_image3)
        powerup_paths = ["images/shield powerup.png","images/fire powerup.png","images/speed powerup.png"]
        Game.POWERUP_IMAGES = Game.load_images(powerup_paths)
        Game.POWERUP_IMAGES = Game.scale_images(Game.POWERUP_IMAGES,1.2)
        Game.SHIELD_IMAGE = pygame.image.load("images/shield.png")
        Game.SHIELD_IMAGE = pygame.transform.smoothscale_by(Game.SHIELD_IMAGE,1.1)
            
    @staticmethod
    def load_images(image_paths):
        loaded_images = []
        for image_path in image_paths:
            loaded_image = pygame.image.load(image_path)
            loaded_images.append(loaded_image)
        return loaded_images

    @staticmethod
    def scale_images(images,scale_factor):
        scaled_images = []
        for image in images:
            scaled_image = pygame.transform.smoothscale_by(image,scale_factor)
            scaled_images.append(scaled_image)
        return scaled_images

class Animation(pygame.sprite.Sprite):
    def __init__(self,pos,millis_per_frame,frames,loop):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.frames = frames
        self.secs_per_frame = millis_per_frame / 1000
        self.cycle_time = self.secs_per_frame * len(self.frames)
        self.loop = loop
        self.frame = 0
        self.anim_clock = pygame.time.Clock()
        self.anim_timer = 0
        self.image = self.frames[self.frame]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)

    def update(self):
        self.anim_timer += self.anim_clock.tick() / 1000
        if self.anim_timer >= self.secs_per_frame:
            self.frame+=1
            if self.loop:
                if self.frame > len(self.frames)-1:
                    self.frame = 0
            else:
                if self.frame > len(self.frames)-1:
                    self.frame = len(self.frames)-1
                    self.kill()
            self.image = self.frames[self.frame]
            self.rect = self.image.get_rect()
            self.rect.center = (self.pos.x,self.pos.y)
            self.anim_timer = 0

    def draw(self,window):
        window.blit(self.image,self.rect)
    
class PlayerLaser(pygame.sprite.Sprite):
    def __init__(self,pos,player,direction,all_sprites,meteors,space_stations):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.all_sprites = all_sprites
        self.meteors = meteors
        self.space_stations = space_stations
        self.pos = pos
        self.direction = direction
        self.image = pygame.image.load("images/player laser.png")
        self.image = pygame.transform.smoothscale_by(self.image,0.65)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        self.speed = 900
        self.mask = pygame.mask.from_surface(self.image)
        self.kill_clock = pygame.time.Clock()
        self.kill_timer = 0
        self.kill_time = Game.EXPLOSION_SOUND.get_length()
        self.can_kill = False

    def check_collisions(self):
        if pygame.sprite.spritecollide(self,self.meteors,False):
            collided = pygame.sprite.spritecollide(self,self.meteors,False,collided=pygame.sprite.collide_mask)
            if collided:
                for meteor in collided:
                    if meteor.rect.bottom > 50:
                        meteor.kill()
                        self.player.score += (100 - meteor.score_adjust)
                        Game.EXPLOSION_SOUND.play()
                        self.image.set_alpha(0)
                        self.pos.x = -180
                        self.rect.center = (self.pos.x,self.pos.y)
                        self.can_kill = True
        collided = pygame.sprite.spritecollide(self,self.space_stations,False)
        if collided:
            for space_station in collided:
                space_station.kill()
                self.player.score += space_station.score_adjust
                explosion_animation = Animation(space_station.pos,55,Game.EXPLOSION_IMAGES,False)
                self.all_sprites.add(explosion_animation,layer=5)
                Game.EXPLOSION_SOUND.play()
                self.image.set_alpha(0)
                self.pos.x = -180
                self.rect.center = (self.pos.x,self.pos.y)
                self.can_kill = True
        if self.can_kill:
            self.kill_timer += self.kill_clock.tick() / 1000
            if self.kill_timer > self.kill_time:
                self.kill()

    def update(self):
        movement = self.direction * self.speed * Game.delta_time
        self.pos += movement
        self.rect.center = (self.pos.x,self.pos.y)
        if self.pos.x > 850 or self.pos.x < -50:
            self.kill()
        if self.pos.y < -50 or self.pos.y > 650:
            self.kill()
        self.check_collisions()

    def draw(window):
        window.blit(self.image.self.rect)
        
class Player(pygame.sprite.Sprite):
    def __init__(self,pos,all_sprites,space_stations,meteors,powerups):
        pygame.sprite.Sprite.__init__(self)
        self.all_sprites = all_sprites
        self.space_stations = space_stations
        self.meteors = meteors
        self.powerups = powerups
        self.pos = pos
        self.angle = 0
        self.score = 0
        self.start_health = 500
        self.health = 500
        self.rotated_image = pygame.image.load("images/player spaceship.png")
        self.rotated_image = pygame.transform.rotate(self.rotated_image,180)
        self.rotated_image = pygame.transform.smoothscale_by(self.rotated_image,0.9)
        self.image = pygame.transform.rotate(self.rotated_image,self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 300
        self.backup_speed = 200
        self.rotation_speed = 200
        self.cos = math.cos(math.radians(self.angle+90))
        self.sin = math.sin(math.radians(self.angle+90))
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        self.fire_clock = pygame.time.Clock()
        self.fire_timer = 0
        self.kill_timer = 0
        self.powerup_time = 10
        self.fire_powerup_timer = 0
        self.speed_powerup_timer = 0
        self.shield_powerup_timer = 0
        self.fire_time = 0.3
        self.firing = False
        self.hit = False
        self.killed = False
        self.fire_activated = False
        self.speed_activated = False
        self.shield_activated = False
        self.laser_sound = pygame.mixer.Sound("sounds/player laser sound.ogg")
        self.powerup_sound = pygame.mixer.Sound("sounds/powerup sound.ogg")
        self.shield_up_sound = pygame.mixer.Sound("sounds/shield up sound.ogg")
        self.shield_down_sound = pygame.mixer.Sound("sounds/shield down sound.ogg")
        self.flash_delay = 50
        self.lasers = pygame.sprite.Group()
        self.shield = None
        
    def rotate(self):
        self.cos = math.cos(math.radians(self.angle+90))
        self.sin = math.sin(math.radians(self.angle+90))
        self.image = pygame.transform.rotate(self.rotated_image,self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)

    def check_bounds(self):
        image_width = self.image.get_width()
        image_height = self.image.get_height()
        if self.rect.left >= 800:
            self.pos.x = -image_width / 2
        elif self.rect.right <= 0:
            self.pos.x = 800 + (image_width / 2)
        if self.rect.top >= 600:
            self.pos.y = -image_height / 2
        elif self.rect.bottom <= 0:
            self.pos.y = 600 + (image_height / 2)

    def move_forward(self):
        x_movement = self.cos * self.speed * Game.delta_time
        y_movement = -self.sin * self.speed * Game.delta_time
        movement = pygame.Vector2(x_movement,y_movement)
        self.check_bounds()
        self.pos += movement
        if self.shield != None:
            self.shield.pos.x = self.pos.x
            self.shield.pos.y = self.pos.y
        self.rect.center = (self.pos.x,self.pos.y)
        
    def move_backward(self):
        x_movement = self.cos * self.backup_speed  * Game.delta_time
        y_movement = -self.sin * self.backup_speed * Game.delta_time
        movement = pygame.Vector2(x_movement, y_movement) * -1
        self.check_bounds()
        self.pos += movement
        if self.shield != None:
            self.shield.pos.x = self.pos.x
            self.shield.pos.y = self.pos.y
        self.rect.center = (self.pos.x,self.pos.y)

    def check_powerups(self):
        if self.shield_activated:
            self.shield_powerup_timer += Game.delta_time
            if self.shield_powerup_timer >= self.powerup_time:
                self.shield.kill()
                self.shield_powerup_timer = 0
                self.shield_down_sound.play()
                self.shield_activated = False
        if self.fire_activated:
            self.fire_powerup_timer += Game.delta_time
            if self.fire_powerup_timer >= self.powerup_time:
                self.fire_time = 0.3
                self.fire_powerup_timer = 0
                self.fire_activated = False
        if self.speed_activated:
            self.speed_powerup_timer += Game.delta_time
            if self.speed_powerup_timer >= self.powerup_time:
                self.speed = 300
                self.speed_powerup_timer = 0
                self.speed_activated = False

    def spawn_laser(self):
        self.firing = True
        if self.fire_timer >= self.fire_time:
            self.laser_sound.play()
            direction = pygame.Vector2(self.cos,-self.sin)
            player_laser = PlayerLaser(pygame.Vector2(self.pos.x+self.cos*self.image.get_width()/1.6,self.pos.y - self.sin*self.image.get_height()/1.6),self,
                                           direction,self.all_sprites,self.meteors,self.space_stations)
            player_laser.image = pygame.transform.rotate(player_laser.image,self.angle)
            player_laser.rect = player_laser.image.get_rect()
            player_laser.rect.center = (self.pos.x+self.cos*self.image.get_width()/1.6,self.pos.y - self.sin*self.image.get_height()/1.6)
            self.all_sprites.add(player_laser,layer=5)
            self.lasers.add(player_laser)
            self.fire_timer = 0

    def fire(self,keys):
        if keys[pygame.K_SPACE]:
            self.spawn_laser()
        if self.firing:
            self.fire_timer += self.fire_clock.tick() / 1000

    def detect_collisions(self):
        if pygame.sprite.spritecollide(self,self.powerups,False):
            collided = pygame.sprite.spritecollide(self,self.powerups,False,pygame.sprite.collide_mask)
            for powerup in collided:
                if isinstance(powerup,ShieldPowerup):
                    self.shield_up_sound.play()
                    if not self.shield_activated:
                        self.shield = Shield(pygame.Vector2(self.pos.x,self.pos.y),self.angle)
                        self.shield_activated = True
                        self.all_sprites.add(self.shield,layer=5)
                if isinstance(powerup,FirePowerup):
                    self.powerup_sound.play()
                    self.fire_activated = True
                    self.fire_time = 0.2
                if isinstance(powerup,SpeedPowerup):
                    self.powerup_sound.play()
                    self.speed_activated = True
                    self.speed = 400
                powerup.kill()
        collided = pygame.sprite.spritecollide(self,self.space_stations,False)
        MINIMUM_HEALTH = 4
        if collided:
            for space_station in collided:
                if not self.shield_activated:
                    self.hit = True
                    self.health -= 30
                    if self.health <= MINIMUM_HEALTH:
                        self.killed = True
                Game.EXPLOSION_SOUND.play()
                pos = space_station.pos
                space_station.kill()
                explosion_animation = Animation(pos,55,Game.EXPLOSION_IMAGES,False)
                self.all_sprites.add(explosion_animation,layer=5)
        if pygame.sprite.spritecollide(self,self.meteors,False):
            collided = pygame.sprite.spritecollide(self,self.meteors,False,pygame.sprite.collide_mask)
            for meteor in collided:
                if not self.shield_activated:
                    self.health -= meteor.score_adjust
                    if self.health <= MINIMUM_HEALTH:
                        self.killed = True
                    self.hit = True
                Game.EXPLOSION_SOUND.play()
                meteor.kill()

    def flash(self):
        if self.hit:
            if self.flash_delay % 2 != 0:
                self.image.set_alpha(50)
            else:
                self.image.set_alpha(255)
            self.flash_delay -= 1
            if self.flash_delay <= 1:
                self.flash_delay = 50
                self.hit = False

    def handle_keyboard_movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.angle += self.rotation_speed * Game.delta_time
            if self.shield != None:
                self.shield.angle += self.rotation_speed * Game.delta_time
            self.rotate()
        elif keys[pygame.K_d]:
            self.angle -= self.rotation_speed * Game.delta_time
            if self.shield != None:
                self.shield.angle -= self.rotation_speed * Game.delta_time
            self.rotate()
        elif keys[pygame.K_w]:
            self.move_forward()
        elif keys[pygame.K_s]:
            self.move_backward()
        self.fire(keys)

    def handle_controller_movement(self):
        for joystick in Game.joysticks:
            horizontal = joystick.get_axis(0)
            vertical = joystick.get_axis(1)
            if vertical < -0.5:
                self.move_forward()
            elif vertical > 0.5:
                self.move_backward()
            elif horizontal < -0.4:
                self.angle += self.rotation_speed * Game.delta_time
                if self.shield != None:
                    self.shield.angle += self.rotation_speed * Game.delta_time
                self.rotate()
            elif horizontal > 0.4:
                self.angle -= self.rotation_speed * Game.delta_time
                if self.shield != None:
                    self.shield.angle -= self.rotation_speed * Game.delta_time
                self.rotate()
            right_trigger = joystick.get_axis(5)
            if right_trigger > 0.5:
                self.spawn_laser()
            if self.firing:
                self.fire_timer += self.fire_clock.tick() / 1000
        
    def update(self):
        self.detect_collisions()
        self.check_powerups()
        self.handle_keyboard_movement()
        self.handle_controller_movement()
        self.flash()
        if self.killed:
            self.kill_timer += Game.delta_time
            if self.kill_timer >= Game.EXPLOSION_SOUND.get_length():
                Game.running = False
            
    def draw(self,window):
        window.blit(self.image,self.rect)

class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rotation_speed = 300
        self.angle = 0
        self.rotated_image = random.choice(Game.METEOR_IMAGES)
        x_pos = random.randrange(800-self.rotated_image.get_width())
        y_pos = random.randrange(-100,-40)
        self.pos = pygame.Vector2(x_pos,y_pos)
        self.direction_x = random.randrange(-3,3)
        self.direction_y = random.randrange(1,8)
        self.speed = 200                 
        self.rect = self.rotated_image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        self.score_adjust = int(self.rect.width * 0.85 / 2)
        self.rotate_direction = 0
        if random.random() < 0.5:
            self.rotate_direction = -1
        else:
            self.rotate_direction = 1
        self.mask = pygame.mask.from_surface(self.rotated_image)

    def rotate(self):
        self.image = pygame.transform.rotate(self.rotated_image,self.angle)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        
    def update(self):
        movement = pygame.Vector2(self.direction_x,self.direction_y).normalize() * self.speed * Game.delta_time
        self.pos += movement
        self.rect.center = (self.pos.x,self.pos.y)
        if self.rotate_direction == 1:
            self.angle += self.rotation_speed * Game.delta_time
            self.rotate()
        elif self.rotate_direction == -1:
            self.angle -= self.rotation_speed * Game.delta_time
            self.rotate()
        if self.rect.top > 650 or self.rect.left < -200 or self.rect.right > 1000:
            self.kill()

    def draw(self,window):
        window.blit(self.image,self.rect)

class Spawner():
    def __init__(self,all_sprites):
        self.spawn_time = 1
        self.spawn_clock = pygame.time.Clock()
        self.spawn_timer = 0
        self.all_sprites = all_sprites

    def update(self):
        pass

class MeteorSpawner(Spawner):
    def __init__(self,all_sprites,meteors):
        super().__init__(all_sprites)
        self.meteors = meteors
        
    def update(self):
        self.spawn_timer += self.spawn_clock.tick() / 1000
        if self.spawn_timer >= self.spawn_time:
            spawned_meteor = Meteor()
            self.all_sprites.add(spawned_meteor,layer=5)
            self.meteors.add(spawned_meteor)
            self.spawn_timer = 0

class SpaceStationSpawner(Spawner):
    def __init__(self,all_sprites,space_stations):
        super().__init__(all_sprites)
        self.space_stations = space_stations
        self.spawn_time = 5
        self.spawn_index = 0
        self.spawn_sound = pygame.mixer.Sound("sounds/spawn sound.mp3")

    def update(self):
        self.spawn_timer += self.spawn_clock.tick() / 1000
        if self.spawn_timer >= self.spawn_time:
            self.spawn_sound.play()
            random_x = random.randrange(90,700)
            random_y = random.randrange(90,500)
            spawned_space_station = SpaceStation(pygame.Vector2(random_x,random_y),self.spawn_index)
            self.all_sprites.add(spawned_space_station,layer=1)
            self.space_stations.add(spawned_space_station)
            self.spawn_timer = 0
            self.spawn_index += 1
            if self.spawn_index > len(Game.SPACE_STATION_IMAGES)-1:
                self.spawn_index = 0

class PowerupSpawner(Spawner):
    def __init__(self,all_sprites,powerups,player):
        super().__init__(all_sprites)
        self.player = player
        self.powerups = powerups
        self.spawn_times = (6,9)
        self.spawn_time = random.choice(self.spawn_times)
        self.powerup_tags = ("Shield","Fire","Speed")
        self.tag_index = 0
        self.powerup_tag = self.powerup_tags[self.tag_index]

    def update(self):
        self.spawn_timer += self.spawn_clock.tick() / 1000
        if self.spawn_timer >= self.spawn_time:
            random_x = random.randrange(20,780)
            y = -50
            if self.powerup_tag == "Shield":
                shield_powerup = ShieldPowerup(pygame.Vector2(random_x,y),self.player)
                self.all_sprites.add(shield_powerup,layer=5)
                self.powerups.add(shield_powerup)
            if self.powerup_tag == "Fire":
                fire_powerup = FirePowerup(pygame.Vector2(random_x,y),self.player)
                self.all_sprites.add(fire_powerup,layer=5)
                self.powerups.add(fire_powerup)
            if self.powerup_tag == "Speed":
                speed_powerup = SpeedPowerup(pygame.Vector2(random_x,y),self.player)
                self.all_sprites.add(speed_powerup,layer=5)
                self.powerups.add(speed_powerup)
            self.spawn_timer = 0
            self.tag_index += 1
            if self.tag_index > len(self.powerup_tags)-1:
                self.tag_index = 0
            self.powerup_tag = self.powerup_tags[self.tag_index]
            self.spawn_time = random.choice(self.spawn_times)
            
class Powerup(pygame.sprite.Sprite):
    def __init__(self,pos,player):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.player = player
        self.speed = 70

    def update(self):
        movement = pygame.Vector2(0,1) * self.speed * Game.delta_time
        self.pos += movement
        self.rect.center = (self.pos.x,self.pos.y)
        if self.rect.top > 600:
            self.kill()

class ShieldPowerup(Powerup):
    def __init__(self,pos,player):
        super().__init__(pos,player)
        self.image = Game.POWERUP_IMAGES[0]
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

class FirePowerup(Powerup):
    def __init__(self,pos,player):
        super().__init__(pos,player)
        self.image = Game.POWERUP_IMAGES[1]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        self.mask = pygame.mask.from_surface(self.image)

class SpeedPowerup(Powerup):
    def __init__(self,pos,player):
        super().__init__(pos,player)
        self.image = Game.POWERUP_IMAGES[2]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
        self.mask = pygame.mask.from_surface(self.image)
          
class SpaceStation(pygame.sprite.Sprite):
    def __init__(self,pos,image_index):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.image = Game.SPACE_STATION_IMAGES[image_index]
        self.rect = self.image.get_rect()
        self.score_adjust = 20
        
    def update(self):
        amplitude = 4
        random_x = random.uniform(-1,1)
        random_y = random.uniform(-1,1)
        offset = pygame.Vector2(random_x,random_y).normalize() * amplitude
        freq = 50
        offset = offset * freq * Game.delta_time
        new_pos = pygame.Vector2(self.pos.x + offset.x,self.pos.y + offset.y)
        self.rect.center = (new_pos.x,new_pos.y)

    def draw(self,window):
        window.blit(self.image,self.rect)

class Shield(pygame.sprite.Sprite):
    def __init__(self,pos,angle):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.angle = angle
        self.original_image = Game.SHIELD_IMAGE.copy()
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)

    def update(self):
        self.image = pygame.transform.rotate(self.original_image,self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos.x,self.pos.y)
    
if __name__ == "__main__":  
    game = Game()
    game.run()
    pygame.quit()
