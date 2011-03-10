#!/usr/bin/python
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


''' Official todo list 


-- Default player should always be first
-- Network
-- Question handling


'''


from Tkinter import *
from twisted.internet import tksupport, reactor
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import ReconnectingClientFactory
from ScrolledText import ScrolledText

import json, time, sys, os

class Window:
    def __init__(self):
        
        self.nickname = "Matti"
        
        
        ''' Create the base window '''
        self.root = Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root.title('pySpellcast')
        self.frame = Frame(self.root,background="white")
        self.frame.pack(fill=BOTH,expand=YES)    
        self.frame.grid_rowconfigure(0,weight=1)
        self.frame.grid_columnconfigure(0,weight=1)
        
        ''' Textframe holds the textbox and entry box '''
        self.textframe = Frame(self.frame)
        self.textframe.grid(row=0,column=0,rowspan=3,sticky=N+S+W+E)
        self.textframe.grid_rowconfigure(0,weight=1)
        self.textframe.grid_columnconfigure(0,weight=1)
        ''' Textbox for server output '''
        self.text = ScrolledText(self.textframe,width=40,height=20,
                                     wrap=WORD,
                                     state=DISABLED, background="white",foreground="black")
        self.text.grid(row=0,column=0,ipadx=10,sticky=N+S+W+E)
        
        
        ''' entrybox for input '''
        self.input = StringVar()
        self.entry = Entry(self.textframe,textvariable=self.input,background="white",foreground="black",
                             state=NORMAL, insertbackground="black")
        self.entry.grid(row=1,column=0,sticky=W+E)
        
        ''' Creating buttons '''
        
        self.sendbutton = Button(self.frame,text="Send")
        self.spellbutton = Button(self.frame,text="Spells")
        
        self.sendbutton.grid(row=1,column=1,sticky=W+E)
        self.spellbutton.grid(row=1,column=2,sticky=W+E)
        
        
        ''' listbox for characters and hitpoints '''
        self.list = Listbox(self.frame,height=10,width=40,font="courier")
        self.list.grid(row=2,column=1,columnspan=8,sticky=N+S+W+E)
        
       
        ''' Loading the icons '''
        self.wave   = PhotoImage(file="wave.gif")
        self.digit  = PhotoImage(file="digit.gif")
        self.snap   = PhotoImage(file="snap.gif")
        self.clap   = PhotoImage(file="clap.gif")
        self.palm   = PhotoImage(file="palm.gif")
        self.wiggle = PhotoImage(file="wiggle.gif")
        self.empty  = PhotoImage(file="empty.gif")
        
        
        ''' Setting up player dictionary, contains player name to player class '''
        self.players = {}
    
    
        #myplayer = Player("Matti",self)
        #pietu = Player("Pietu",self)
        #samu = Player("Richard",self)
        #self.sortPlayers()
        '''
        player = LabelFrame(self.frame, text="White Mage", background="white")
        player.grid(row=0,column=1,columnspan=2,padx=5,pady=0)

        for y in xrange(2):
            for i in xrange(8):
                licon = Label(player,image=self.icon)
                licon.grid(row=i,column=y,pady=2,padx=2)
            
        player = LabelFrame(self.frame, text="Black Mage", background="white")
        player.grid(row=0,column=3,columnspan=2,padx=5,pady=0)

        for y in xrange(2):
            for i in xrange(8):
                licon = Label(player,image=self.icon)
                licon.grid(row=i,column=y,pady=2,padx=2)
        '''   
        questions = LabelFrame(self.frame,text="Questions")
        questions.grid(row=4,column=0,columnspan=10,sticky=W+E)
        
        question = Label(questions,text="Test")
        question.pack(anchor=W,fill=BOTH,expand=1)
        

    def sortPlayers(self):
        for i,(name,player) in enumerate(self.players.items()):
            player.frame.grid_remove()
            player.frame.grid(row=0,column=1+i,padx=5)
        
    def testPlayers(self):
        self.players = {'White mage':0,'Black mage':0}
        
    def updatePlayers(self,players):
        for player,history in players:
            if player not in self.players.keys():
                self.players[player] = Player(player,self)

            self.players[player].updateHistory(history)
        
        self.sortPlayers()
        # Todo, remove nonexisting players..
        
    def updatePlayerFrames(self):
        # TODO: FIIXIXIXIXIXIIXIXXIIXII
        playerFrames = self.playerFrames[:]
        self.playerFrames = []
        
        for name,frame in self.players:
            if frame not in playerFrames:
                new = Frame(self.root,background="red")
                
            else:
                self.playerFrames.append(frame)
            #TODO: remove nonexisting players
    def stop(self):
        self.root.destroy()
        reactor.stop()
        sys.exit(1)
        
    def display_line(self,text,timestamp=None):
        print "Display",text
        if not timestamp: timestamp = time.time()
        print "scroll1:",self.text.yview()
        if self.text.yview()[1] == 1.0: scroll = True
        else: scroll = False
        
        self.text.config(state=NORMAL)
        asciitime = time.strftime('[%H:%M:%S]', time.localtime(float(timestamp)))
        #if owner: self.textarea.mark_set(start, END);self.textarea.mark_gravity(start,LEFT
        #text = self.wrap(text)
        text = [['black',text]]
        ts = ('grey',"%s "%(asciitime))
        text.insert(0,ts)
     
        for piece in text:
            self.text.insert(END, piece[1],piece[0])
        #if owner: self.textarea.mark_set(end, END);self.textarea.mark_gravity(end,LEFT)
        self.text.insert(END,'\n')
 
        
        
        print "scroll2",self.text.yview()
        if scroll: self.text.yview(END)
        '''
        if owner:
            print "Checking tag.."
            a,b= self.textarea.tag_ranges(tag)
            print dir(a)
            self.textarea.delete(a,b)
        '''  
        self.text.config(state=DISABLED)   
class Player:
    def __init__(self,name,window):
        self.name = name
        self.window = window
        
        if self.name not in self.window.players.keys():
            self.window.players[self.name] = self
        
        self.frame = LabelFrame(self.window.frame,text=self.name,background='white')
        
        self.history = []
        self.historyLabels = []
        for i in xrange(8):
            left  = Label(self.frame,image=self.window.empty)
            right = Label(self.frame,image=self.window.empty)
            left.grid(row=i,column=0)
            right.grid(row=i,column=1)
            self.historyLabels.append([left,right])
        
        if self.window.nickname == self.name:
            left.bind("<Button-1>",   self.left_click)
            right.bind("<Button-1>",   self.right_click)
            
            
    def remove(self):
        pass
        #grid_remove
        
    def updateHistory(self,history):
        self.history = history[:]
        for i in xrange(8):
            h = self.history[-i]
            l = self.historyLabels[-i]
            
    def left_click(self,event): 
        print "LEFT CLICK"
    
    def right_click(self,event):
        print "RIGHT CLICK"
        print event
        print dir(event)
        print event.x,event.y
        print event.x_root,event.y_root
        ActionDialog(self.window.root,self.window,event.x_root,event.y_root,event.x,event.y)


class ActionDialog(Toplevel):
    def __init__(self,parent,window,x_root,y_root,x,y):
        Toplevel.__init__(self, parent)
        #self.transient(parent)
        self.overrideredirect(1)
        self.geometry("+%d+%d" % (x_root-x,
                                  y_root-y))
                                
        self.body = Frame(self)
        self.body.pack()
        
        r0c0 = Label(self.body,image=window.empty)
        r0c1 = Label(self.body,image=window.palm)
        r0c2 = Label(self.body,image=window.digit)
        r0c3 = Label(self.body,image=window.wiggle)
        
        r1c0 = Label(self.body,image=window.wave)
        r1c1 = Label(self.body,image=window.clap)
        r1c2 = Label(self.body,image=window.snap)
        r1c3 = Label(self.body,image=window.empty)
        
        r0c0.grid(row=0,column=0)
        r0c1.grid(row=0,column=1)
        r0c2.grid(row=0,column=2)
        r0c3.grid(row=0,column=3)
        r1c0.grid(row=1,column=0)
        r1c1.grid(row=1,column=1)
        r1c2.grid(row=1,column=2)
        r1c3.grid(row=1,column=3)
        
        

    def buttonCallback(self):
        print "Exit time."
        self.parent.quit()
        
class Client(LineReceiver):
    def __init__(self,window):
        self.window   = window
        #LineReceiver.__init__(self)

        
    def connectionMade(self):
        self.window.display_line("Connected!")
        self.write("handshake pyspellcast 0.1 %s"%self.window.nickname)

        
        
    def lineReceived(self, data):
        data = data.decode('utf-8')
        #print "lineReceived",data
        if len(data) < 2: return
        tok = data.split(' ')
        hdr = tok[0]
        
        if hdr == 'updatePlayers':
            print "Update players received"
            parseplayers = " ".join(tok[1:]).split(';')
            players = []
            for player in parseplayers:
                name,history = player.split(':')
                players.append([name,json.loads(history)])
            print "Player list"
            print players
            self.window.updatePlayers(players)
            
        elif hdr == 'updateHealth':
            lines = " ".join(tok[1:]).split(';')
            self.window.list.delete(0, END)
            for line in lines:
                self.window.list.insert(END, line)
        
        
        elif hdr == 'msg':
            message = " ".join(tok[1:])
            self.window.display_line(message)
            
        else:
            print "Unknown packet"
            print data
    
    
    def connectionLost(self,reason):
        pass

    def write(self,data):
        data = data+'\r\n'
        data = data.encode('utf-8')
        print "Writing",data
        self.transport.write(data)
        


class CFactory(ReconnectingClientFactory):
    def __init__(self,window):
        self.window = window
        #ReconnectingClientFactory.__init__(self)
        
    def startedConnecting(self, connector):
        print ('Started to connect.')

    def buildProtocol(self, addr):
        print ('Connected.')
        print ('Resetting reconnection delay')
        
        self.resetDelay()
        client = Client(self.window)
        self.window.connection = client
        return client

    def clientConnectionLost(self, connector, reason):
        #self.window.display_line(' Lost connection. Reason:' + str(reason))
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        #self.window.display_line( 'Connection failed. Reason:' + str(reason))
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)

if __name__ == '__main__':
    window = Window()
    tksupport.install(window.root)
    reactor.connectTCP("127.0.0.1", 49500, CFactory(window))
    reactor.run()