import pygame

class Fighter():
    #Constructor
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_frames, attack_sound, hit_sound):
        #Player hitbox
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.custom_offset = [87, 76]
        self.hit_offset = [85, 81.5]
        self.death_offset = [85, 83]
        self.flip = flip

        #Player animation
        self.animation_list = self.load_images(sprite_sheet, animation_frames)
        self.action = 0 #0:idle #1:run #2:jump #3:attack1 #4:attack2 #5:hit #6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index] #Assign first frame of fighter's current action animation 
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0

        #Player status and actions
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.last_attack_time = 0
        self.attack_sound = attack_sound
        self.hit = False
        self.hit_sound = hit_sound
        self.health = 100
        self.alive = True
    
    def load_images(self, sprite_sheet, animation_frames):
        #Extract images from spreadsheet
        animation_list = []
        #y = 0
        for y, animation in enumerate(animation_frames): #Track each frame
            temp_img_list = []
            #Create temp list of frames from each row of spreadsheet to add to main list
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            #y += 1
            animation_list.append(temp_img_list)
        #print(animation_list)
        return animation_list

    #Method to move fighters
    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        FLOOR = 50
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        #Get keypress
        key = pygame.key.get_pressed() #Register key pressed into key variable

        #Can only perform other actions if not currently attacking
        if self.attacking == False and self.alive == True and round_over == False:
            #Check player 1 controls
            if self.player == 1:
                #Movement keys
                #Move left
                if key[pygame.K_a]: 
                    dx = -SPEED
                    self.running = True
                #Move right
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True
                #Jump
                if key[pygame.K_w] and self.jump == False: #If not currently jumping
                    self.vel_y = -30
                    self.jump = True
                #Attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #Determine which attack type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            #Check player 2 controls
            if self.player == 2:
                #Movement keys
                #Move left
                if key[pygame.K_LEFT]: 
                    dx = -SPEED
                    self.running = True
                #Move right
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True
                #Jump
                if key[pygame.K_UP] and self.jump == False: #If not currently jumping
                    self.vel_y = -30
                    self.jump = True
                #Attack
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    #Determine which attack type was used
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

        #Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        #Ensure players stays on screen
        if self.rect.left + dx < 0: #If player is going off left side of screen (x position is negative)
            dx = 0 - self.rect.left

        if self.rect.right + dx > screen_width: #If player is going off right side of screen
            dx = screen_width - self.rect.right

        if self.rect.bottom + dy > screen_height - FLOOR: 
            self.vel_y = 0
            self.jump = False #Reset player status to not jumping
            dy = screen_height - FLOOR - self.rect.bottom
        
        #Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True
        
        #Apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #Update player position
        self.rect.x += dx
        self.rect.y += dy

    #Handle animation updates
    def update(self):
        #Check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6) #6:death
        elif self.hit == True:
            self.update_action(5) #5:hit
        elif self.attacking == True: 
            if self.attack_type == 1:
                self.update_action(3) #3:attack1
            elif self.attack_type == 2:
                self.update_action(4) #4:attack2
        elif self.jump == True:
            self.update_action(2) #2:jump
        elif self.running == True:
            self.update_action(1) #1:run
        else:
            self.update_action(0) #0:idle     

        animation_cooldown = 45

        #Update image
        self.image = self.animation_list[self.action][self.frame_index]

        #Check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        #Check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]): #If next animation index is out of range

            #If player is dead, end animation
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

                #Check if an attack was performed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20

                #Check if damage was taken
                if self.action == 5:
                    self.hit = False
                    #If the player was in the middle of an attack, stop attack animation
                    self.attacking = False
                    self.attack_cooldown = 20

    #Method to attack
    def attack(self, target):
        #Add a delay before allowing another attack
        ATTACK_DELAY = 300

        if self.attack_cooldown == 0 and pygame.time.get_ticks() - self.last_attack_time > ATTACK_DELAY:
            self.attacking = True
            self.attack_sound.play()
            
            #Create attack hitbox facing target, from center of player
            attack_width = 3 * self.rect.width
            attack_height = self.rect.height
            if self.flip:
                attacking_rect = pygame.Rect(self.rect.left - attack_width, self.rect.y, attack_width, attack_height)
            else:
                attacking_rect = pygame.Rect(self.rect.right, self.rect.y, attack_width, attack_height)
            
            #Check for collision with target
            if attacking_rect.colliderect(target.rect):
                target.health -= 25
                target.hit = True
                self.hit_sound.play()

            #Set the attack cooldown
            self.attack_cooldown = 20
            self.last_attack_time = pygame.time.get_ticks()
            #pygame.draw.rect(surface, (0, 255, 0), attacking_rect)



    def update_action(self, new_action):
        #Check if the new action is different to previous one
        if new_action != self.action:
            self.action = new_action

            #Update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    #Method to draw fighters    
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        #pygame.draw.rect(surface, (255, 0, 0), self.rect)

        # Check the current action and apply the appropriate offset
        if self.action == 5:  # Hit animation
            surface.blit(img, (self.rect.x - (self.hit_offset[0] * self.image_scale), self.rect.y - (self.hit_offset[1] * self.image_scale)))
        elif self.action == 6:  # Death animation
            surface.blit(img, (self.rect.x - (self.death_offset[0] * self.image_scale), self.rect.y - (self.death_offset[1] * self.image_scale)))
        elif self.action not in [0, 1, 2]:  # Custom offset for animations other than idle, run, and jump
            surface.blit(img, (self.rect.x - (self.custom_offset[0] * self.image_scale), self.rect.y - (self.custom_offset[1] * self.image_scale)))
        else:
            # Apply regular offset for idle, run, and jump actions
            surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))





