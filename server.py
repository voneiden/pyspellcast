#!/usr/bin/python2
# -*- coding: utf-8 -*-

'''
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


    Also, this program features very messy code, don't hurt your head
    trying to decypher it.

    Copyright 2010-2011 Matti Eiden <snaipperi()gmail.com>
'''

from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
import hashlib, random, re, pickle, time, os, json


class Game:
    def __init__(self):
        self.players    = {}
        self.spectators = {}

        self.bStarted = False
        self.round = 0
        self.stage = 0
        
    def addPlayer(self,player):
        if self.bStarted: self.spectators[player.name] = player
        else:             self.players[player.name] = player
        player.bReady = True
        self.updatePlayers()
        
    def updatePlayers(self):
        players = []
        
        for player in self.players.values():
            players.append('%s:%s'%(player.name,json.dumps(player.history)))
            
        pbuf = ";".join(players)
        
        for player in self.players.values():
            player.write('updatePlayers %s'%pbuf)
            
            
        
    def startGame(self):
        pass
        #Move spectators as playesr!

class Player(LineReceiver):
    def connectionMade(self):
        print "connectionMade"
        self.handle   = self.receive
        self.game = self.factory.game
        self.hp    = 15
        self.stage = 0
        self.history = []
        
        for i in xrange(8): self.history.append([' ',' '])
        
        self.bReady = False
        print "end connection made"
        
    def lineReceived(self, data):
        #print("Line received!")
        data = data.decode('utf-8')
        self.handle(data)
    
    def connectionLost(self,reason):
        #if not self.state == -1: self.world.disconnectPlayer(self)
        pass
    def write(self,data,newline=True):
        print "writing->",data
        if newline: data = ("%s\r\n"%data).encode('utf-8')
        self.transport.write(data)
        
 
    def receive(self,data):
        tok = data.split(' ')
        print "recv",data
        if not self.bReady:
            if tok[0] == 'handshake' and len(tok) >= 4:
                print "Handshake"
                client = tok[1]
                version = tok[2]
                name    = " ".join(tok[3:])
                
                if client != 'pyspellcast': self.transport.loseConnection();return
                if version != '0.1': self.write("Wrong version");self.transport.loseConnection();return
                self.name = name
                self.game.addPlayer(self)
                

class PlayerFactory(Factory):
    def __init__(self,game):
        self.protocol = Player
        self.game    = game


   
        

if __name__ == '__main__':
    game = Game()
    reactor.listenTCP(49500, PlayerFactory(game))
    reactor.run()
