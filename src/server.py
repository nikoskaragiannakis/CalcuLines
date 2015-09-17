from PodSixNet.Channel import Channel
from PodSixNet.Server import Server
from time import sleep
import sys


class ServerChannel(Channel):
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)

    def Close(self):
        self._server.DeletePlayer(self)

    # Callbacks #########################################

    def Network_myaction(self, data):
        print "myaction:", data
        self._server.SetBoard(data, update=True)

    def Network_hello(self, data):
        print 'message=', data['message']
        if data['board'] != '':
            self._server.SetBoard(data)

    def Network_mousedown(self, data):
        print 'action:', data['action']

    # ###################################################


class CalcuLinesServer(Server):
    channelClass = ServerChannel

    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.players = {}
        print 'CalcuLines Server launched!'
        self.game = None
        self.board = None

    def Connected(self, channel, addr):
        print 'new connection:', channel
        self.players[channel] = True
        if self.game is None:
            self.game = Game(channel)
            self.game.redplayer.Send({"action": "hello",
                                      "message": "Hello red player!",
                                      "board": ""})
        else:
            self.game.blueplayer = channel
            self.game.blueplayer.Send({"action": "hello",
                                       "message": "Hello blue player!",
                                       "board": self.board})
            self.game.redplayer.Send({"action": "startgame",
                                      "player": "red",
                                      "whoplays": "red"})
            self.game.blueplayer.Send({"action": "startgame",
                                       "player": "blue",
                                       "whoplays": "red"})

    def DeletePlayer(self, player):
        print 'player with id', str(player.address), 'has left the game.'
        player.Send({"action": "bye", "message": "Bye client!"})
        del self.players[player]

    def SetBoard(self, data, update=False):
        self.board = data['board']
        if update:
            print(data['whoplays'], data['score_info'])
            self.game.redplayer.Send({"action": "update",
                                      "board": data['board'],
                                      "whoplays": data['whoplays'],
                                      "score_info": data['score_info'],
                                      "no_cells": data['no_cells']})
            self.game.blueplayer.Send({"action": "update",
                                       "board": data['board'],
                                      "whoplays": data['whoplays'],
                                      "score_info": data['score_info'],
                                      "no_cells": data['no_cells']})

    def Launch(self):
        while True:
            self.Pump()
            sleep(0.0001)


class Game:
    def __init__(self, redplayer):
        # 'red' or 'blue'
        self.turn = 'red'
        self.redplayer = redplayer
        self.blueplayer = None

# Get command line argument of server, port
if len(sys.argv) != 2:
    print "Usage:", sys.argv[0], "host:port"
    print "e.g.", sys.argv[0], "localhost:12345"
else:
    host, port = sys.argv[1].split(":")
    server = CalcuLinesServer(localaddr=(host, int(port)))
    server.Launch()
