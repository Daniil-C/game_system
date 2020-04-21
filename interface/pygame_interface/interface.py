import sys, pygame

pygame.init()
 
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
black = 0, 0, 0

info = pygame.display.Info()
size = width, height = info.current_w, info.current_h
print(size)

SERVER_IP = ""
SERVER_PORT = ""
SETTINGS = False
MODE = 0

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

def settings_menu(com, backend):
	"""settings menu"""
	BG_settings = 0
	BG_settingsrect = 0
	ip_text = ""
	port_text = ""
	def save_fun(*arg):
		"""Save ip and port"""
		nonlocal BG_settings, BG_settingsrect, ip_text, port_text
		if checker(ip_text, port_text):	# backend.set_conection_params(ip_text, int(port_text))
			global SETTINGS
			SERVER_IP = ip_text
			SERVER_PORT = int(port_text)
			SETTINGS = True
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
					elif len(ip_text) < 20:
						ip_text += event.unicode
				elif port_active:
					if event.key == pygame.K_RETURN:
						ip_active = False
						port_active = False
						# == press save
						save_fun()
					elif event.key == pygame.K_BACKSPACE:
						port_text = port_text[:-1]
					elif len(port_text) < 22:
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

def rule_menu(com, backend):
	BG_rule = pygame.transform.scale(pygame.image.load("rule_menu.png"), size)
	BG_rulerect = BG_rule.get_rect()

	back = pygame.transform.scale(pygame.image.load("back.png"), (int(height * 21 / 216), int(height * 21 / 216)))
	backrect = back.get_rect()
	backrect[0] = 0
	backrect[1] = int(height * 185 / 216)

	while True:
		for event in pygame.event.get():
			"""MOUSE EVENTS"""
			if event.type == pygame.MOUSEBUTTONDOWN:
				if backrect.collidepoint(event.pos):
					return None
		screen.blit(BG_rule, BG_rulerect)
		screen.blit(back, backrect)
		pygame.display.flip()

def play_menu_2(com, backend):
	BG = pygame.transform.scale(pygame.image.load("BG_main.png"), size)
	BGrect = BG.get_rect()

	back = pygame.transform.scale(pygame.image.load("back.png"), (int(height * 21 / 216), int(height * 21 / 216)))
	backrect = back.get_rect()
	backrect[0] = 0
	backrect[1] = int(height * 185 / 216)

	font = pygame.font.SysFont("Chilanka", int(height / 30))
	name_active = False
	name_text = ""
	namerect = pygame.Rect(int(width / 3), int(height * 53 / 216), int(width / 3), int(height * 3 / 60))
	inactive_color = 0xFF, 0xFF, 0xFF
	active_color = 0xAD, 0xE5, 0xF3
	name_color = inactive_color

	def save_fun(*arg):
		"""Save ip and port"""
		nonlocal BG, BG, name_text
		if name_text.isalnum:	
			#backend.set_name(name_text)
			BG_settings = pygame.transform.scale(pygame.image.load("BG_settings_saved.png"), size)
			BG_settingsrect = BG_settings.get_rect()
			name_text = ""
		else:
			BG_settings = pygame.transform.scale(pygame.image.load("BG_settings_not_saved.png"), size)
			BG_settingsrect = BG_settings.get_rect()

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
				if namerect.collidepoint(event.pos):
					name_active = not name_active
				else:
					name_active = False
					if saverect.collidepoint(event.pos):
						save_fun()
			"""KEYBOARD EVENTS"""
			if event.type == pygame.KEYDOWN:
				if name_active:
					if event.key == pygame.K_RETURN:
						name_active = False
					elif event.key == pygame.K_BACKSPACE:
						name_text = name_text[:-1]
					elif len(name_text) < 20:
						name_text += event.unicode
			"""OTHER EVENTS"""
			if event.type == pygame.QUIT:
				sys.exit()
			name_color = active_color if name_active else inactive_color

		shift = int(height / 120)
		screen.blit(BG, BGrect)
		screen.blit(back, backrect)
		screen.blit(save, saverect)
		name_box = font.render(name_text, True, name_color)
		screen.blit(name_box, (namerect[0] + shift, namerect[1] + shift))
		pygame.draw.rect(screen, name_color, namerect, 2)
		pygame.display.flip()


def play_menu(com, backend):
	while not SETTINGS:
		settings_menu(com, backend)
		return None
	#backend.start_game()
	num = 1 #backend.get_num()
	if num == 1:
		BG = pygame.transform.scale(pygame.image.load("BG_main.png"), size)
		BGrect = BG.get_rect()

		back = pygame.transform.scale(pygame.image.load("back.png"), (int(height * 21 / 216), int(height * 21 / 216)))
		backrect = back.get_rect()
		backrect[0] = 0
		backrect[1] = int(height * 185 / 216)

		mode1 = pygame.transform.scale(pygame.image.load("classic.png"), (int(width / 6), int(width / 6)))
		mode1rect = mode1.get_rect()
		mode1rect[0] = int(width / 8)
		mode1rect[1] = int(height * 29 / 216)

		mode2 = pygame.transform.scale(pygame.image.load("ariadna.png"), (int(width / 6), int(width / 6)))
		mode2rect = mode2.get_rect()
		mode2rect[0] = int(width * 5 / 12)
		mode2rect[1] = int(height * 29 / 216)

		mode3 = pygame.transform.scale(pygame.image.load("himera.png"), (int(width / 6), int(width / 6)))
		mode3rect = mode3.get_rect()
		mode3rect[0] = int(width * 17 / 24)
		mode3rect[1] = int(height * 29 / 216)

		mode4 = pygame.transform.scale(pygame.image.load("Odiseya.png"), (int(width / 6), int(width / 6)))
		mode4rect = mode4.get_rect()
		mode4rect[0] = int(width / 8)
		mode4rect[1] = int(height * 122 / 216)

		mode5 = pygame.transform.scale(pygame.image.load("pandora.png"), (int(width / 6), int(width / 6)))
		mode5rect = mode5.get_rect()
		mode5rect[0] = int(width * 5 / 12)
		mode5rect[1] = int(height * 122 / 216)

		mode6 = pygame.transform.scale(pygame.image.load("persefona.png"), (int(width / 6), int(width / 6)))
		mode6rect = mode6.get_rect()
		mode6rect[0] = int(width * 17 / 24)
		mode6rect[1] = int(height * 122 / 216)

		global MODE

		while True:
			for event in pygame.event.get():
				"""MOUSE EVENTS"""
				if event.type == pygame.MOUSEBUTTONDOWN:
					if backrect.collidepoint(event.pos):
						return None
					if mode1rect.collidepoint(event.pos):
						#global MODE
						MODE = 1
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None
					if mode2rect.collidepoint(event.pos):
						#global MODE
						MODE = 2
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None
					if mode3rect.collidepoint(event.pos):
						#global MODE
						MODE = 3
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None
					if mode4rect.collidepoint(event.pos):
						#global MODE
						MODE = 4
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None
					if mode5rect.collidepoint(event.pos):
						#global MODE
						MODE = 5
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None
					if mode6rect.collidepoint(event.pos):
						#global MODE
						MODE = 6
						#backend.mode(MODE)
						play_menu_2(com, backend)
						return None

			screen.blit(BG, BGrect)
			screen.blit(back, backrect)
			screen.blit(mode1, mode1rect)
			screen.blit(mode2, mode2rect)
			screen.blit(mode3, mode3rect)
			screen.blit(mode4, mode4rect)
			screen.blit(mode5, mode5rect)
			screen.blit(mode6, mode6rect)
			pygame.display.flip()
	elif num > 0:
		play_menu_2(com, backend)
		return None
	else:
		clock = pygame.time.Clock()
		BG = pygame.transform.scale(pygame.image.load("BG_main.png"), size)
		BGrect = BG.get_rect()

		back = pygame.transform.scale(pygame.image.load("back.png"), (int(height * 21 / 216), int(height * 21 / 216)))
		backrect = back.get_rect()
		backrect[0] = 0
		backrect[1] = int(height * 185 / 216)
#		while not backend.end.upd():
		for i in range(15):
			for event in pygame.event.get():
				"""MOUSE EVENTS"""
				if event.type == pygame.MOUSEBUTTONDOWN:
					if backrect.collidepoint(event.pos):
						return None
			time_passed = clock.tick (1)

			screen.blit(BG, BGrect)
			screen.blit(back, backrect)
			pygame.display.flip()

def main_menu(com, backend):
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
				settings_menu(com, backend)
			elif event.type == pygame.MOUSEBUTTONDOWN and rulerect.collidepoint(event.pos):
				rule_menu(com, backend)
			elif event.type == pygame.MOUSEBUTTONDOWN and playrect.collidepoint(event.pos):
				play_menu(com, backend)

		screen.blit(BG, BGrect)
		screen.blit(play, playrect)
		screen.blit(exit, exitrect)
		screen.blit(settings, settingsrect)
		screen.blit(rule, rulerect)
		pygame.display.flip()

def init_interface(com, backend):
	main_menu(com, backend)

init_interface(-1, -1)
