import sys, pygame

pygame.init()

def scale(a, A, point):
	"""a - origin, A - real, point - dot in original"""
	return (point * A)/a

#size_orig = width_orig, height_orig = 1920, 1080
size_orig = width_orig, height_orig = 320, 240

#size = width, height = 
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#screen = pygame.display.set_mode(size_orig)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h

BG = pygame.transform.scale(pygame.image.load("BG.png"), size)
BGrect = BG.get_rect()

play = pygame.transform.scale(pygame.image.load("play.png"), (int(width / 3), int(height * 11 / 72)))
playrect = play.get_rect()
playrect[0] = int(width / 3)
playrect[1] = int(height * 64 / 216)

exit = pygame.transform.scale(pygame.image.load("exit.png"), (int(width / 3), int(height * 11 / 72)))
exitrect = exit.get_rect()
exitrect[0] = int(width / 3)
exitrect[1] = int(height * 115 / 216)

settings = pygame.transform.scale(pygame.image.load("settings.png"), (int(height * 21 / 216), int(height * 21 / 216)))
settingsrect = settings.get_rect()
settingsrect[0] = 0
settingsrect[1] = int(height * 185 / 216)

rule = pygame.transform.scale(pygame.image.load("rule.png"), (int(height * 21 / 216), int(height * 21 / 216)))
rulerect = rule.get_rect()
rulerect[0] = int(width * 121 / 128)
rulerect[1] = int(height * 185 / 216)

while 1:
	for event in pygame.event.get():
		if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
			sys.exit()

	screen.blit(BG, BGrect)
	screen.blit(play, playrect)
	screen.blit(exit, exitrect)
	screen.blit(settings, settingsrect)
	screen.blit(rule, rulerect)
	pygame.display.flip()
