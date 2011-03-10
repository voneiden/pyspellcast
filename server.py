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
        
        self.spells = {}
        self.loadSpells()
        
    def loadSpells(self):
        f = open('spells.txt','r')
        for line in f.readlines():
            if line[:2] == '//': print "comment ignore"
            else: 
                tok = line.split()
                syntax = tok[0]
                name = " ".join(tok[1:])
                print syntax,name,
                rebuf = []
                for chr in syntax:
                    if chr.isupper(): rebuf.append(chr)
                    else: rebuf.append("[%s%s]"%(chr.lower(),chr.upper()))
                regex = re.compile("".join(rebuf)+'$')
                print "".join(rebuf)
                self.spells[regex] = name
                
    def addPlayer(self,player):
        if self.bStarted: self.spectators[player.name] = player
        else:             self.players[player.name] = player
        player.bReady = True
        self.updatePlayers()
        self.updateHealth()
        
        for player in self.players.values():
            player.setStage(1)
    def updatePlayers(self):
        # Todo send unknowns
        players = []
        
        for player in self.players.values():
            players.append('%s:%s'%(player.name,json.dumps(player.history[-8:])))
            
        pbuf = ";".join(players)
        
        for player in self.players.values():
            player.write('updatePlayers %s'%pbuf)
            
    def updateHealth(self):
        pbuf = []
        for player in self.players.values():
            if player.stage == 0: ready = ''
            else: ready = '*'
            pbuf.append("%s%s%s%i"%(player.name,ready," "*(30-len(player.name+ready)),player.hp))
            
        for player in self.players.values():
            player.write("updateHealth %s"%(";".join(pbuf)))
            
        
    def startGame(self):
        self.round = 1
        self.stage = 1
        
        for player in self.players.values():
            player.write("msg You prepare yourself for the battle. The referee casts a formal dispel-magic and anti-spell on you")
            for other in self.players.values():
                if other == player: continue
                other.write("msg %s strides confidently on the arena, ready for the battle.")
            player.history = []
            for i in xrange(8):
                player.history.append([' ',' '])
            player.setStage(1)
            
            player.write("msg --- Round 1 ---")
        self.updatePlayers()
        self.updateHealth()
        
    def tick(self):
        # This function moves the game forward.. tick by tick
        # Stage 1 means that all players should sent their moves,
        # If there is a confusion spell or amnesia, the server modifies these moves accordingly
        # After all players have sent their moves, the moves are revealed.
        # If a player succeeded at casting multiple spells, 
        # they are required to choose which they wish to cast
        # If a player succeeded at casting spells, they are required to target those spells
        # Finally, if there are any monsters on the battlefield, request their masters to designate a target
        
        print "Tick tack"
        ''' Stage one, we need all players to send their moves before continuing! '''
        if self.stage == 1:
            bNotSent = False
            for player in self.players.values():
                if player.stage == 1: bNotSent = True;break
            if bNotSent:
                print "Waiting for other players.."
                self.updateHealth()
                return
            else:
                print "All players have sent their moves."
                self.stage = 2
                
                ''' Now we need to check if players have succeeded at casting anything.. '''
                for player in self.players.values():
                    lstr = []
                    rstr = []
                    for move in xrange(8):
                        move += 1
                        lstr.append( player.history[-move][0])
                        rstr.append( player.history[-move][1])
                    print "Player moves"
                    lstr.reverse()
                    rstr.reverse()
                    
                    lstr = "".join(lstr)
                    rstr = "".join(rstr)
                    print lstr
                    print rstr
                    
                    print "Checking left hand.."
                    l_choices = []
                    r_choices = []
                    for spell in self.spells.keys():
                        if re.search(spell,lstr): l_choices.append(self.spells[spell])
                        if re.search(spell,rstr): r_choices.append(self.spells[spell])
                        
                    print "You may cast the following spells"
                    print l_choices
                    print r_choices
                    
                    if len(l_choices) > 1: 
                        player.questions['What do you want to cast with your left hand?'] = l_choices[:]
                        self.setState(2)
                    if len(r_choices) > 1:
                        player.questions['What do you want to cast with your right hand?'] = r_choices[:]
                        self.setState(2)
                        
                        
                    self.sendQuestions(player)
        
        #TODO: think about it.. :F
        if self.stage == 2:
            bNotSent = False
            for player in self.players.values():
                if player.stage != 0: bNotSent = True;break
            if bNotSent:
                print "Waiting for players to answer questions.."
                self.updateHealth()
                return
            else:
                print "All players have answered the questions"
        
        self.newRound()
    
    def newRound(self):
        self.stage = 1
        
        for player in self.players.values():
            player.history.append([' ',' '])
            player.setStage(1)
        self.updatePlayers()
    def sendQuestions(self,player):
        if len(player.questions) > 0:
            qbuf = []
            for question,choices in player.questions.items():
                qbuf.append("%s:%s"%(question,json.dumps(choices)))
            player.write("questions %s"%";".join(qbuf))
            
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
        
        self.questions = {}
        
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
        data = data.strip()
        
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
                self.write("msg Welcome to pyspellcast server!")
                
        else:
            if tok[0] == 'moves':
                if self.stage != 1: print "Client sent moves even though stage not one!";return
                data = json.loads(" ".join(tok[1:]))
                print "Got moves",data
                if data[0] == data[1]: data = [data[0].upper(),data[1].upper()]
                self.history[-1] = data
                self.setStage(0)
                self.game.tick()
                    
            elif tok[0] == 'msg' and len(tok) > 1:
                if tok[1].lower() == '/start':
                    if self.game.round == 0: self.game.startGame()
                else:
                    for player in self.game.players.values():
                        player.write("msg %s: %s"%(self.name," ".join(tok[1:])))
                
    def setStage(self,stage):
        self.write("stage %i"%stage)
        self.stage = stage
        
class PlayerFactory(Factory):
    def __init__(self,game):
        self.protocol = Player
        self.game    = game


   
        

if __name__ == '__main__':
    game = Game()
    reactor.listenTCP(49500, PlayerFactory(game))
    reactor.run()
