import sys, pygame

pygame.init()
 
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h
print(size)

SERVER_IP = ""
SERVER_PORT = ""

def checker(IP, PORT):
	"""Check data in settings fields"""
	ip_pars = IP.split(".")
	ip_flg = False
	port_flg = False
	if len(ip_pars) == 4:
		for i in ip_pars:
			if i.isnumeric():
				if int(i) <= 255 and int(i) >= 0:
					continue
				else:
					break
			else:
				break
		else:
			ip_flg = True
	if PORT.isnumeric():
		if int(PORT) >= 1024 and int(PORT) <= 65535:
			port_flg = True
	return ip_flg and port_flg

def settings_menu():
	"""settings menu"""
	BG_settings = 0
	BG_settingsrect = 0
	ip_text = ""
	port_text = ""
	def save_fun(*arg):
		"""Save ip and port"""
		nonlocal BG_settings, BG_settingsrect, ip_text, port_text
		if checker(ip_text, port_text):
			SERVER_IP = ip_text
			SERVER_PORT = port_text
			BG_settings = pygame.transform.scale(pygame.image.load("BG_settings_saved.png"), size)
			BG_settingsrect = BG_settings.get_rect()
			ip_text = ""
			port_text = ""
		else:
			BG_settings = pygame.transform.scale(pygame.image.load("BG_settings_not_saved.png"), size)
			BG_settingsrect = BG_settings.get_rect()

	font = pygame.font.SysFont("Chilanka", int(height / 30))
	ip_active = False
	port_active = False
	iprect = pygame.Rect(int(width / 3), int(height * 53 / 216), int(width / 3), int(height * 3 / 60))
	portrect = pygame.Rect(int(width / 3), int(height * 137 / 216), int(width / 3), int(height * 3 / 60))
	inactive_color = 0xFF, 0xFF, 0xFF
	active_color = 0xAD, 0xE5, 0xF3
	ip_color = inactive_color
	port_color = inactive_color

	BG_settings = pygame.transform.scale(pygame.image.load("BG_settings.png"), size)
	BG_settingsrect = BG_settings.get_rect()

	back = pygame.transform.scale(pygame.image.load("back.png"), (int(height * 21 / 216), int(height * 21 / 216)))
	backrect = back.get_rect()
	backrect[0] = 0
	backrect[1] = int(height * 185 / 216)

	save = pygame.transform.scale(pygame.image.load("save.png"), (int(width * 7 / 128), int(height * 12 / 216)))
	saverect = save.get_rect()
	saverect[0] = int(width * 227 / 480)
	saverect[1] = int(height * 7 / 9)
	
	while True:		
		for event in pygame.event.get():			
			"""MOUSE EVENTS"""
			if event.type == pygame.MOUSEBUTTONDOWN:
				if backrect.collidepoint(event.pos):
					return None
				if iprect.collidepoint(event.pos):
					port_active = False
					ip_active = not ip_active
				elif portrect.collidepoint(event.pos):
					ip_active = False
					port_active = not port_active
				else:
					ip_active = False
					port_active = False
					if saverect.collidepoint(event.pos):
						save_fun()
			"""KEYBOARD EVENTS"""
			if event.type == pygame.KEYDOWN:
				if ip_active:
					if event.key == pygame.K_RETURN:
						ip_active = False
						port_active = True
					elif event.key == pygame.K_BACKSPACE:
						ip_text = ip_text[:-1]
					else:
						ip_text += event.unicode
				elif port_active:
					if event.key == pygame.K_RETURN:
						# TODO save data!!
						ip_active = False
						port_active = False
						# == press save
						save_fun()
					elif event.key == pygame.K_BACKSPACE:
						port_text = port_text[:-1]
					else:
						port_text += event.unicode
			"""OTHER EVENTS"""
			if event.type == pygame.QUIT:
				sys.exit()
			ip_color = active_color if ip_active else inactive_color
			port_color = active_color if port_active else inactive_color

		shift = int(height / 120)
		screen.blit(BG_settings, BG_settingsrect)
		screen.blit(back, backrect)
		screen.blit(save, saverect)
		ip_box = font.render(ip_text, True, ip_color)
		port_box = font.render(port_text, True, port_color)
		screen.blit(ip_box, (iprect[0] + shift, iprect[1] + shift))
		screen.blit(port_box, (portrect[0] + shift, portrect[1] + shift))
		pygame.draw.rect(screen, ip_color, iprect, 2)
		pygame.draw.rect(screen, port_color, portrect, 2)
		pygame.display.flip()

def main_menu():
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
			if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN and exitrect.collidepoint(event.pos):
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN and settingsrect.collidepoint(event.pos):
				settings_menu()

		screen.blit(BG, BGrect)
		screen.blit(play, playrect)
		screen.blit(exit, exitrect)
		screen.blit(settings, settingsrect)
		screen.blit(rule, rulerect)
		pygame.display.flip()

main_menu()
