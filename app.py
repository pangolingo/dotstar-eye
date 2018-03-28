import os
import keyboard
import argparse
import apa102

# --headless will run without window
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--headless", help="run in headless mode", action="store_true")

args = parser.parse_args()

if args.headless:
    os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame


run_loop = True

# Initialize the library and the strip
strip = apa102.APA102(num_led=64, global_brightness=1, mosi = 10, sclk = 11,
                                          order='rgb')


class EyeLid(pygame.sprite.Sprite):
    def __init__(self):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("images/eye_lid.png")
        self.rect = self.image.get_rect()
        self.open()
        self.blinking_opening = False
        self.blinking_closing = False
        self.blink_speed = 5
        self.blink()
    
    def update(self):
        if self.blinking_closing:
            self.rect.y += self.blink_speed
            if self.rect.y >= 0:
                self.blinking_closing = False
                self.blinking_opening = True
        elif self.blinking_opening:
            self.rect.y -= self.blink_speed
            if self.rect.y < -self.image.get_size()[1]:
                self.blinking_closing = False
                self.blinking_opening = False

    def open(self):
        self.rect.y = -(self.image.get_size()[1])
    
    def close(self):
        self.rect.y = 0

    def blink(self):
        self.blinking_closing = True


def draw_to_dotstar(dotstar, image):
    pixel_num = 0
    for row in image:
        for pixel in row:
            dotstar.set_pixel(int(pixel_num), int(pixel[0]), int(pixel[1]), int(pixel[2]))
            pixel_num += 1

    dotstar.show()

def main():

    def move(dir):
        global run_loop
        if dir == 'up':         eye_ball_pos[1] = eye_ball_pos[1] - 1
        elif dir == "down":     eye_ball_pos[1] = eye_ball_pos[1] + 1
        elif dir == "left":     eye_ball_pos[0] = eye_ball_pos[0] - 1
        elif dir == "right":    eye_ball_pos[0] = eye_ball_pos[0] + 1
        else:                   raise ValueError('move type not supported')

        if eye_ball_pos[0] < -1:
            eye_ball_pos[0] = -1
        if eye_ball_pos[0] + eye_ball.get_size()[0] > 9:
            eye_ball_pos[0] = 9 - eye_ball.get_size()[0]
        if eye_ball_pos[1] < -1:
            eye_ball_pos[1] = -1
        if eye_ball_pos[1] + eye_ball.get_size()[1] > 9:
            eye_ball_pos[1] = 9 - eye_ball.get_size()[1]

    def blink():
        return None

    # Turn off all pixels (sometimes a few light up when the strip gets power)
    strip.clear_strip()

    """ Set up the game and run the main game loop """
    pygame.init()      # Prepare the pygame module for use
    pygame.display.init()


    try:

        screen_size = 8   # Desired physical surface size, in pixels.
        preview_size = 64

        # Create surface of (width, height), and its window.
        viewable_surface = pygame.display.set_mode((preview_size, preview_size), 0, 32 if args.headless else 0)
        main_surface = pygame.surface.Surface((screen_size, screen_size))

        clock = pygame.time.Clock()


        eye_white = pygame.image.load("images/eye_white.png")
        eye_ball = pygame.image.load("images/eye_ball.png")
        eye_alpha_overlay = pygame.image.load("images/eye_alpha_overlay.png")
        eye_mask = pygame.image.load("images/eye_mask.png")
        # eye_lid = pygame.image.load("images/eye_lid.png")


        eye_ball_pos = [0, 0]
        # eye_lid_pos = [0, 0 - eye_lid.get_size()[1] / 2] # start offscreen

        
        all_sprites = pygame.sprite.Group()
        eyelid = EyeLid()
        all_sprites.add(eyelid)
        

        def headless_key_pressed(event, scan_code=None, time=None):
            global run_loop
            if event.name == 'esc':         run_loop = False
            elif event.name == 'up':        move("up")
            elif event.name == 'down':      move("down")
            elif event.name == 'left':      move("left")
            elif event.name == 'right':     move("right")
            elif event.name == 'space':     blink()
        
        if args.headless:
            keyboard.on_press(headless_key_pressed)

        while run_loop:
            if pygame.event.get(pygame.QUIT): break
            pygame.event.pump()

            if not args.headless:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]: break
                if keys[pygame.K_UP]:       move("up")
                if keys[pygame.K_DOWN]:     move("down")
                if keys[pygame.K_LEFT]:     move("left")
                if keys[pygame.K_RIGHT]:    move("right")
                if keys[pygame.K_SPACE]:      eyelid.blink()

            
                

            

            main_surface.fill((0, 0, 0))
            viewable_surface.fill((0, 0, 0))

            main_surface.blit(eye_white, (0, 0))
            main_surface.blit(eye_ball, eye_ball_pos)
            main_surface.blit(eye_alpha_overlay, (0, 0))

            all_sprites.update()
            all_sprites.draw(main_surface)

            main_surface.blit(eye_mask, (0, 0))
            # main_surface.blit(eye_lid, (0, 0))



            # Overpaint a smaller rectangle on the main surface
            # main_surface.fill((255, 0, 0), (0, 0, 2, 2))
            # main_surface.fill((0, 255, 0), (6, 0, 2, 2))

            

            viewable_surface.blit(pygame.transform.scale(main_surface, (64, 64)), (0, 0))

            # numpy arr
            # print(pygame.surfarray.array3d(main_surface))
            # print(pygame.surfarray.array3d(eye_ball)[0])
            # print(pygame.surfarray.array3d(main_surface)[0][5])
            if args.headless:
                draw_to_dotstar(strip, pygame.surfarray.array3d(main_surface))


            # Now the surface is ready, tell pygame to display it!
            pygame.display.flip()

            clock.tick(10)

    finally:
        pygame.quit()     # Once we leave the loop, close the window.
        # strip cleanup
        strip.clear_strip()
        strip.cleanup()

main()