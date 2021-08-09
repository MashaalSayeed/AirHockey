import time
import socket
import selectors

import pygame

from sprites import Player, AIPlayer, Ball, BaseGame
from ui import UIManager
from socketclient import SocketClient
import constants as const

SOCKET_EVENT = pygame.USEREVENT + 1


class Client(SocketClient):
    def __init__(self, sel, host, port):
        self.host = host
        self.port = port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        super().__init__(sel, sock, (host, port))

    def connect(self):
        self.sock.connect_ex((self.host, self.port))
        print(f"Connected to {self.host}, port: {self.port}")

    def listen(self):
        # Must keep calling this until client closes
        events = self.selector.select(timeout=None)
        try:
            for key, mask in events:
                sock = key.data
                sock.process_event(mask)
        except Exception as e:
            print("Exception caught:", e)
            return False
        else:
            return True

    def handle_request(self, data):
        header, body = data['header'], data['body']
        event = pygame.event.Event(SOCKET_EVENT, {'header': header, 'body': body})
        pygame.event.post(event)


class AirHockey(BaseGame):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.set_mode((const.SCREENX, const.SCREENY))
        self.ui = UIManager(self)
        self.client = None

        self.state = 'MENU'
        self.game_over = False
        pygame.display.set_caption('Air Hockey Python')
    
    def score_goal(self):
        super().score_goal()
        if self.winner:
            self.state = 'PAUSED'
            self.ui.pause_message = 'You Lose!' if type(self.winner) == Player else 'You Win'
    
    def reset_board(self):
        [sprite.reset() for sprite in self.all_sprites]
        self.goal = False

    def pause(self):
        if self.state == 'PLAYING':
            self.state = 'PAUSED' 
        elif self.state == 'PAUSED' and not self.win:
            self.state = 'PLAYING'

    def restart(self):
        if self.state == 'PAUSED':
            self.reset_board()
            self.scores = [0, 0]
            self.winner = None
            self.state = 'PLAYING'
            self.ui.pause_message = 'PAUSED'
        
    def quit(self):
        if self.state == 'MENU':
            self.game_over = True

    def connect_client(self):
        if self.client:
            return

        self.client = Client(sel, 'localhost', 22222)
        self.client.connect()
        self.client.send('JOIN_GAME')
        self.state = 'WAITING'
    
    def disconnect_client(self):
        if self.client:
            self.client.close()
            self.client = None
            self.state = 'MENU'

    def handle_online_event(self, event):
        if event.header == 'GAME_UPDATE':
            self.state = 'PLAYING'
            self.ball.rect.center = event.body['ball']
            self.player1.rect.center = event.body['opponent']
        elif event.header == 'GOAL':
            self.goal = True
            self.scores = event.body['scores']
        elif event.header == 'PLAYER_POS':
            self.player2.rect.center = event.body['rect']
            self.goal = False
        elif event.header == 'GAME_OVER':
            self.state = 'PAUSED'
            self.ui.pause_message = 'You win!' if event.body['winner'] else 'You lose!'

    def run(self):
        self.ui.prepare()
        self.player1 = AIPlayer(self, 0, const.SCREENX//2, const.SCREENY//4 + 50, const.AI_DIFFICULTY)
        self.player2 = Player(self, 1, const.SCREENX//2, 3 * const.SCREENY//4 + 25)
        self.ball = Ball(self, *self.board_rect.center)

        self.players = pygame.sprite.Group(self.player1, self.player2)
        self.all_sprites = pygame.sprite.Group(self.ball, self.players)

        try:
            while not self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_over = True
                    elif event.type == pygame.MOUSEBUTTONUP:
                        self.ui.handle_mouse_up()
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.pause()
                        elif event.key == pygame.K_r:
                            self.restart()
                    elif event.type == SOCKET_EVENT:
                        self.handle_online_event(event)

                self.ui.draw(self.screen)
                if self.client:
                    connected = self.client.listen()
                    if not connected:
                        self.disconnect_client()

                if self.state == 'PLAYING' and self.client:
                    self.player2.update()
                    self.client.send('PLAYER_MOVE', {
                        'rect': self.player2.rect.center, 
                        'velocity': list(self.player2.velocity)
                    })
                elif self.state == 'PLAYING':
                    self.all_sprites.update()

                    if self.goal and time.time() - self.time_of_goal >= const.GOAL_TEXT_DELAY:
                        self.reset_board()

                pygame.display.flip()
                # Seconds passed since last tick
                self.tick = self.clock.tick(const.FPS)
        except KeyboardInterrupt:
            pass
        self.disconnect_client()
        sel.close()


if __name__ == '__main__':
    pygame.init()
    sel = selectors.DefaultSelector()
    AirHockey().run()