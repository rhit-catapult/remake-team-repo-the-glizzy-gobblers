import pygame

# 1. Initialize Pygame and Font Setup
pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Pygame Text Input Example")
font = pygame.font.Font(None, 36)

# 2. Text Box Configuration
input_rect = pygame.Rect(100, 200, 440, 45)
color_active = pygame.Color("dodgerblue2")
color_inactive = pygame.Color("lightskyblue3")
box_color = color_inactive

# 3. State Variables
user_text = ""
active = False
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Toggle focus when clicking the text box
        if event.type == pygame.MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = True
                box_color = color_active
            else:
                active = False
                box_color = color_inactive

        # Capture key presses when the text box is active
        if active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    # Remove the last character
                    user_text = user_text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Process the final text entry
                    print(f"Submitted Text: {user_text}")
                    user_text = ""

            elif event.type == pygame.TEXTINPUT:
                # Append standard unicode characters
                user_text += event.text

    # 4. Rendering Phase
    screen.fill((30, 30, 30))

    # Render text surface (Text, Antialiasing, Color)
    text_surface = font.render(user_text, True, (255, 255, 255))
    
    # Auto-resize the input box outline if text exceeds default size
    input_rect.w = max(440, text_surface.get_width() + 10)

    # Draw the text and the surrounding boundary box
    screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 7))
    pygame.draw.rect(screen, box_color, input_rect, 3)

    pygame.display.flip()

pygame.quit()