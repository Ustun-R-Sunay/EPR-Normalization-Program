# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 14:50:21 2018
Made for normalizing asc files from bruker system.
@author: Ustun R. Sunay
"""

import sys
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QVBoxLayout, QFileDialog, QLabel

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os


class Window(QDialog):
    # __init__ initializes the parameters
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

     

        # Create buttons and their link to a function
        self.button = QPushButton('Normalize 1 file',self)
        self.button.clicked.connect(self.Norm1file)
        self.button2 = QPushButton('Normalize 1 folder',self)
        self.button2.clicked.connect(self.Norm1Folder)
        # Create a label
        self.label1 =QLabel('Welcome to the Normalization program!',self)
        #self.label1.setFont(self,14)
        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.button2)
        layout.addWidget(self.label1)
        self.setLayout(layout)

    def plot(self,data):
        ''' plot your EPR spectrum '''
        #clear previous data
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # plot data
        ax.plot(data[:,0],data[:,1], '*-')

        # refresh canvas
        self.canvas.draw()
        
    def norm(self,ascFname,data,saveFileName):
        ''' Normalizes data and saves  '''
        self.label1.setText(' ')
        parFname=ascFname.replace('asc','par')
        chkExist=Path(parFname)
        #Check to see if par file exists
        if  chkExist.exists():    
            parFile=np.genfromtxt(parFname,dtype='str')
       
            #find Normalization parameters. Since each word is an element, go from end
            RRG = parFile[-9].astype(np.float)              
            RCT = parFile[-13].astype(np.float) 
            JSD = parFile[-21].astype(np.float)              
        
            # normalize data
            data[:,1]=data[:,1]*(2*10**5/RRG)*(1/JSD)*(81.92/RCT)  
            # save data that is tab spaced
            np.savetxt(saveFileName,data,delimiter='\t')  
            self.label1.setText('Normalization successfull!')
        else:
            self.label1.setText('unable to locate PAR file: \n '+ascFname)
            
            
    def ErrRprt(self,ErrList):
        '''Used to report any missing files '''
        Report='Uh oh SpaghettiOs! Cannot find following asc files: \n'
        for i in range(0,len(ErrList),1):
            Report=Report+ErrList[i]+' \n'
        if len(ErrList)==0:
            self.label1.setText('Normalization successfull!')
        else:
            self.label1.setText(Report)
            
            
    def Norm1file(self):
        '''Normalize one file '''
        #find asc file and store info
        self.fname = QFileDialog.getOpenFileName(self, 'Open file',filter='asc files (*.asc)')  
        #define the save file name by adding n to end of file name but keeing asc extension
        saveFileName = self.fname[0].replace('.asc','n.asc')
        print(saveFileName)
        if self.fname[0]:
            #load data into 2 columns. First 4 lines are not data
            data=np.loadtxt(self.fname[0],delimiter='\t',skiprows=4)
            self.plot(data)
            self.norm(self.fname[0],data,saveFileName)
           
    def Norm1Folder(self):
        '''Normalize one folder Function '''
        self.label1.setText(' ')
        #create list of files where there are no matching asc files
        ErrList=[]
        self.fname= str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        #create save directory of normalized files
        savedir=self.fname + '/norm'
        if not os.path.exists(savedir):
             os.makedirs(savedir)
             
        #load each asc file      
        for file in os.listdir(self.fname):
            #obtain only par files
            if file.endswith('.par'):
                #find corresponding asc file
                file=file.replace('.par','.asc')
                my_file= Path(os.path.join(self.fname,file))
                
                #confirm that the asc file exists
                if my_file.exists():
                    
                    data=np.loadtxt(os.path.join(self.fname,file),delimiter='\t',skiprows=4)
                    saveFileName = savedir + '/' +file.replace('.asc','n.asc')
                    self.norm((os.path.join(self.fname,file)),data,saveFileName)
                else:
                #if the file doesn't exist, add to error report list
                    ErrList[:0]=[file]
        #print out error report list
        self.ErrRprt(ErrList)  
           
# run code without errors        
if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance() 
    main = Window()
    main.show()
    sys.exit(app.exec_())