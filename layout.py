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

class Window:
    def __init__(self):
        
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
        
        self.list.insert(END, "Matti          15hp")
        self.list.insert(END, "Pietu          15hp")
        self.list.insert(END, "Richard         1hp")
        
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
    
    
        myplayer = Player("Matti",self)
        pietu = Player("Pietu",self)
        samu = Player("Richard",self)
        self.sortPlayers()
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
        
    def updatePlayers(self):
        playerFrames = self.playerFrames[:]
        self.playerFrames = []
        
        for name,frame in self.players:
            if frame not in playerFrames:
                new = Frame(self.root,background="red")
                
            else:
                self.playerFrames.append(frame)
    def stop(self):
        self.root.destroy()
        reactor.stop()
        sys.exit(1)
        
class Player:
    def __init__(self,name,window):
        self.name = name
        self.window = window
        
        if self.name not in self.window.players.keys():
            self.window.players[self.name] = self
        
        self.frame = LabelFrame(self.window.frame,text=self.name,background='white')
        
        self.history = []
        for i in xrange(8):
            left  = Label(self.frame,image=self.window.empty)
            right = Label(self.frame,image=self.window.empty)
            left.grid(row=i,column=0)
            right.grid(row=i,column=1)
            self.history.append([left,right])
            
            
    def remove(self):
        pass
        #grid_remove
        
if __name__ == '__main__':
    window = Window()
    tksupport.install(window.root)
    reactor.run()