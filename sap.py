import threading
import time

import numpy as np
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button
from mpl_toolkits.mplot3d import Axes3D

from libspectrumanalyzer import SpectrumAnalyzer

figspectrum3d = plt.figure(1, figsize=(7.5, 4))
axspectrum3d = figspectrum3d.add_subplot(111, projection='3d')

figspectrogram = plt.figure(2, figsize=(7.5, 4))
axspectrogram = figspectrogram.add_subplot(111)

figspectrum = plt.figure(3, figsize=(15, 4))
figspectrum.subplots_adjust(top=0.85)
axspectrum = figspectrum.add_subplot(111)

def displayspectrum(rsa):
    axspectrum.set_title('Spectrum')
    axspectrum.set_xlabel('Frequency (GHz)')
    axspectrum.set_ylabel('Amplitude (dBm)')

def updatespectrum(frameNum, rsa):
    if (rsa.initiate == True and rsa.readyToSpectrumDisplay == True):
        #print(frameNum)

        axspectrum.set_xlim(rsa.freqMin, rsa.freqMax)
        axspectrum.set_ylim(rsa.refLevel - 80, rsa.refLevel)

        for i, line in enumerate(axspectrum.lines):
            axspectrum.lines.pop(i)
            try:
                line.remove()
            except:
                pass

        axspectrum.plot(rsa.freq, rsa.trace, 'y')

def displayspectrogram(rsa):
    axspectrogram.set_title('Spectrogram')
    axspectrogram.set_xlabel('Frequency (GHz)')
    rsa.Z = []

def updatespectrogram(frameNum, rsa):
    if (rsa.initiate == True and rsa.readyToSpectrum3dDisplay == True):
        #print(frameNum)

        axspectrogram.set_xlim(rsa.freqMin, rsa.freqMax)
        #axspectrogram.set_ylim(0, N-1)

        try:
            rsa.spectrogram.remove()
        except:
            pass

        try:
            rsa.spectrogram = axspectrogram.pcolormesh(rsa.mX, rsa.mY, rsa.aZ, cmap=cm.coolwarm, vmin=rsa.refLevel - 80, vmax=rsa.refLevel, shading='gouraud')
        except:
            pass

        plt.draw()

def displayspectrum3d(rsa):
    axspectrum3d.set_title('Spectrum (3D)')
    axspectrum3d.set_xlabel('Frequency (GHz)')
    axspectrum3d.set_zlabel('Amplitude (dBm)')
    rsa.Z = []

def updatespectrum3d(frameNum, rsa):
    if (rsa.initiate == True and rsa.readyToSpectrum3dDisplay == True):
        #print(frameNum)

        axspectrum3d.set_zlim(rsa.refLevel - 80, rsa.refLevel)

        try:
            rsa.spectrum3d.remove()
        except:
            pass

        try:
            rsa.spectrum3d = axspectrum3d.plot_surface(rsa.mX, rsa.mY, rsa.aZ, cmap=cm.coolwarm, vmin=rsa.refLevel - 80, vmax=rsa.refLevel)
        except:
            pass

def updatespectrumdata(rsa):
    while (rsa.readyToTerminate == False):
        if(len(rsa.trace) == rsa.tracePoints):
            rsa.readyToSpectrumDisplay = True
        else:
            rsa.readyToSpectrumDisplay = False

        time.sleep(0.001)

def updatespectrum3ddata(rsa, N):
    while (rsa.readyToTerminate == False):
        if(len(rsa.trace) == rsa.tracePoints):

            if (len(rsa.Z) == N):
                rsa.X = rsa.freq
                rsa.Y = np.arange(0, N, 1)
                rsa.mX, rsa.mY = np.meshgrid(rsa.X, rsa.Y)
                rsa.aZ = np.array(rsa.Z)

                #rsa.Z[:-1] = rsa.Z[1:]
                #rsa.Z[-1] = list(rsa.trace)
                rsa.Z.pop()
            else:                
                #rsa.Z.append(list(rsa.trace))
                rsa.Z.insert(0, list(rsa.trace))

            rsa.readyToSpectrum3dDisplay = True
        else:
            rsa.readyToSpectrum3dDisplay = False

        time.sleep(0.01) 

def sap(ipAddress, port):
    rsa = SpectrumAnalyzer(host=ipAddress, port=port)
    rsa.connect()

    print(rsa.id)

    rsa.reset()
    rsa.write('format:data binary')

    rsa.write('spectrum:frequency:center {}'.format(rsa.cf))
    rsa.write('spectrum:frequency:span {}'.format(rsa.span))
    rsa.write('input:rlevel {}'.format(rsa.refLevel))

    rsa.write('initiate:continuous on')

    #rsa.write('trigger:status on')
    #rsa.write('trigger:event:source input')
    #rsa.write('trigger:event:input:level -50')

    axcf = plt.axes([0.15, 0.90, 0.05, 0.0375])
    tbcf = TextBox(axcf, 'Center Frequency (MHz)', initial=str(rsa.cf / 1e6))
    tbcf.on_submit(rsa.setCenterFrequencyMHz)

    axspan = plt.axes([0.26, 0.90, 0.05, 0.0375])
    tbspan = TextBox(axspan, 'Span (MHz)', initial=str(rsa.span / 1e6))
    tbspan.on_submit(rsa.setSpanMHz)

    axref = plt.axes([0.42, 0.90, 0.025, 0.0375])
    tbref = TextBox(axref, 'Reference Level (dBm)', initial=str(rsa.refLevel))
    tbref.on_submit(rsa.setReferenceLevel)

    axrun = plt.axes([0.7, 0.90, 0.1, 0.0375])
    axstop = plt.axes([0.81, 0.90, 0.1, 0.0375])
    brun = Button(axrun, 'Run')
    bstop = Button(axstop, 'Stop')
    brun.on_clicked(rsa.run)
    bstop.on_clicked(rsa.stop)

    anispectrum = FuncAnimation(figspectrum, updatespectrum, fargs=(rsa,), init_func=displayspectrum(rsa), interval=1, blit=False)
    anispectrogram = FuncAnimation(figspectrogram, updatespectrogram, fargs=(rsa,), init_func=displayspectrogram(rsa), interval=50, blit=False)
    anispectrum3d = FuncAnimation(figspectrum3d, updatespectrum3d, fargs=(rsa,), init_func=displayspectrum3d(rsa), interval=50, blit=False)

    figspectrum.canvas.mpl_connect('close_event', rsa.disconnect)

    rsa.readyToTerminate = False

    tspectrum = threading.Thread(target=updatespectrumdata, args=(rsa,))
    tspectrum.start()
    tspectrum3d = threading.Thread(target=updatespectrum3ddata, args=(rsa,50,))
    tspectrum3d.start()

    plt.show()

    rsa.readyToTerminate = True

    try:
        rsa.disconnect()
    except:
        pass

def main():
    sap('192.168.1.100', port=34835)

if __name__ == '__main__':
    main()
