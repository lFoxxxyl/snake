import os
import json
import random
import curses

def add_win(height, width, y ,x):
	window = curses.newwin(height, width, y ,x)
	window.box()
	return window

class Snake:
	def __init__(self, stdscr):
		self.stdscr = stdscr
		self.height = 30
		self.width = 90
		self.snake = [
			[self.height//2, self.width//2],
			[self.height//2, self.width//2-1]
		]
		self.food = [self.height//3, self.width//3]
		self.direction = curses.KEY_LEFT
		self.score = 0
		self.record_table = {}
		self.read_record_table()
		
		#interface
		title = add_win(3, self.width//3, 0, 0)
		title.addstr(1,1,"SNAKE") 
		title.refresh()

		username = add_win(3, self.width//3, 0, self.width//3)
		username.addstr(1,1, f"USERNAME: {os.getenv('USER')}")
		username.refresh()

		self.score_win = add_win(3, self.width//3, 0, self.width//3*2)
		self.score_win.addstr(1,1, "SCORE: 0")
		self.score_win.refresh()

		self.field = add_win(self.height, self.width, 3, 0)
		curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
		self.field.refresh()

		self.record_win = add_win(13, self.width, self.height + 3, 0)
		self.record_win.addstr(1,1, "HIGH SCORES (TOP 10):")
		top_ten = sorted(self.record_table.items(), 
			key=lambda item: item[1], reverse=True)[:10]
		
		for idx, (name, score) in enumerate(top_ten):
			self.record_win.addstr(idx + 2, 1, f"{name:<25} {score:<10}")   
		self.record_win.refresh()
	
	def start(self):
		curses.curs_set(0)
		self.field.nodelay(1)
		self.field.timeout(100)
		self.field.keypad(True)
		self.field.addch(self.food[0], self.food[1], "*", curses.color_pair(1))	
		self.draw_snake()
		valid_keys =  [
			curses.KEY_RIGHT, 
			curses.KEY_LEFT, 
			curses.KEY_DOWN,
			curses.KEY_UP
		]

		#game cycle
		while True:
			next_key = self.field.getch()
			if next_key in valid_keys:
				self.direction = next_key
			
			self.move_snake()

			if self.snake[0] == self.food:
				self.eat_food()
			else:
				self.remove_tail()
			if (
				self.snake[0][0] in [0, self.height-1] or 
				self.snake[0][1] in [0, self.width-1] or
				self.snake[0] in self.snake[1:]
			):
				self.end_game()
				self.write_record_table()
				break

			self.draw_snake()	
	
	def eat_food(self):
		self.food = None
		while self.food is None:
			new_food = [
				random.randint(1, self.height - 2), 
				random.randint(1, self.width - 2)
			]
			self.food = new_food if new_food not in self.snake else None
		self.field.addch(self.food[0], self.food[1], "*", curses.color_pair(1))
		self.score += 1
		self.score_win.addstr(1,1, f"SCORE: {self.score}")
		self.score_win.refresh()

	def move_snake(self):
		new_head = [self.snake[0][0], self.snake[0][1]]
		if self.direction == curses.KEY_RIGHT:
			new_head[1] += 1
		if self.direction == curses.KEY_LEFT:
			new_head[1] -= 1
		if self.direction == curses.KEY_DOWN:
			new_head[0] += 1
		if self.direction == curses.KEY_UP:
			new_head[0] -= 1
		self.snake.insert(0, new_head)

	def draw_snake(self):
		for item in self.snake:
			self.field.addch(item[0], item[1], "#", curses.color_pair(2)) 
		self.field.refresh()

	def remove_tail(self):
		tail = self.snake.pop()
		self.field.addch(tail[0], tail[1], " ")
	
	def end_game(self):
		self.field.clear()
		self.field.box()
		self.field.addstr(self.height // 2, self.width // 2 - 5, "GAME OVER")
		self.field.refresh()
		curses.napms(2000)

	def read_record_table(self):
		self.record_table = {}
		if not os.path.isfile("record_table.json"):
			with open("record_table.json", "w") as file:
				json.dump(self.record_table, file)
		else:
			with open("record_table.json") as file:
				self.record_table = json.load(file)
	
	def write_record_table(self):
		if (
			os.getenv('USER') not in self.record_table or 
			self.record_table[os.getenv('USER')] < self.score
		):
			
			self.record_table[os.getenv('USER')] = self.score
			with open("record_table.json", "w") as file:
				json.dump(self.record_table, file) 

def main(stdscr):	
	snake = Snake(stdscr)
	snake.start()

curses.wrapper(main)
