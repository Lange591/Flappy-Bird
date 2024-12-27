print("starting")
from tkinter import *
from math import *
from random import randrange
import threading
from PIL import ImageTk, Image

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1000
GAP_WIDTH = 150
BOTTOM_GAP_PADDING = 50
TOP_GAP_PADDING = 20
PIPE_WIDTH = 80
BIRD_HEIGHT = 58
BIRD_WIDTH = 79

playing = True
window_open = True

class Sprite:
	def __init__(self, file, canvas, x=0, y=0):
		self.x = x
		self.y = y
		self.image = PhotoImage(file=file)
		self.cnv = canvas
		self.draw()

	def draw(self):
		self.image_id = self.cnv.create_image(self.x, self.y, image=self.image, anchor=NW)

	def destroy(self):
		self.cnv.delete(self.image_id)

class Bird(Sprite):
	SPEED = 11
	
	def __init__(self, game, x=0, y=0):
		super().__init__('bird.png', game.canvas, x, y)
		self.angle = 0
		self.game = game
		self.moving = True
		self.cnv.bind_all('<space>', self.resetAngle)

	def move(self):
		if self.y < 0:
			self.y = 0
			self.angle = 0
		elif self.y > SCREEN_HEIGHT - BIRD_HEIGHT:
			self.game.gameover()
		else:
			self.y -= sin(radians(self.angle)) * Bird.SPEED
		self.angle = max(self.angle-4.5, -89)

		pilImage = Image.open('bird.png')
		self.image = ImageTk.PhotoImage(pilImage.rotate(self.angle/2))
		self.cnv.delete(self.image_id)
		self.draw()
		
		if playing:
			self.cnv.after(30, self.move)
	
	def resetAngle(self, event):
		self.angle = 65

class PipeSet:
	def __init__(self, game, x=1000):
		self.topy = randrange(0-SCREEN_HEIGHT+TOP_GAP_PADDING, 0-GAP_WIDTH-BOTTOM_GAP_PADDING)
		self.down_pipe = Sprite('pipedown.png', game.canvas, x, self.topy)
		self.up_pipe = Sprite('pipeup.png', game.canvas, x, self.topy + SCREEN_HEIGHT + GAP_WIDTH)
		self.farx = x+PIPE_WIDTH
		self.cnv = game.canvas
		self.game = game
		self.move()

	def move(self):
		self.down_pipe.x -= 11
		self.up_pipe.x -= 11
		self.farx -= 11
		
		self.cnv.coords(self.down_pipe.image_id, self.down_pipe.x, self.down_pipe.y)
		self.cnv.coords(self.up_pipe.image_id, self.up_pipe.x, self.up_pipe.y)
		
		if self.farx < 0:
			self.game.score += 1
			self.destroy()
		elif playing:
			self.cnv.after(30, self.move)
			self.game.check(self)

	def destroy(self):
		self.down_pipe.destroy()
		self.up_pipe.destroy()
		del self.game.pipes[0]

class Game:
	def __init__(self):
		self.root = Tk()
		self.root.title('Flappy Airplane')
		self.root.protocol("WM_DELETE_WINDOW", self.window_closed)

		self.canvas = Canvas(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg='lightblue')
		self.canvas.create_text(350,30,fill="white",font="Times 30 italic bold", text="Press space to jump")
		self.canvas.pack()

		self.score = 0
		self.bird = Bird(self, 100, SCREEN_HEIGHT/2)
		self.pipes = []

	def start(self):
		self.bird.move()
		self.createpipes()
		self.root.mainloop()
	
	def createpipes(self):
		if playing:
			print("creating new pipe")
			self.pipes.append(PipeSet(self))
			self.canvas.after(2500, self.createpipes)

	def gameover(self):
		global playing
		playing = False
		timer = threading.Timer(3, self.resume)
		timer.start()

	def resume(self):
		if window_open:
			global playing
			playing = True
			self.bird.destroy()
			for sets in self.pipes:
				sets.destroy()
			self.score = 0
			self.bird = Bird(self, 100, SCREEN_HEIGHT/2)
			self.pipes = []
			self.bird.move()
			self.createpipes()

	def check(self, pipeset):
		if self.bird.x > pipeset.farx-PIPE_WIDTH-BIRD_WIDTH and self.bird.x < pipeset.farx:
			if self.bird.y < pipeset.topy+600 or self.bird.y+BIRD_HEIGHT > pipeset.topy+600+GAP_WIDTH:
				self.gameover()

	def window_closed(self):
		global window_open
		window_open = False
		self.root.destroy()

game = Game()
game.start()