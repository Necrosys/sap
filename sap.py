import numpy as np
import matplotlib.pyplot as plt

from matplotlib import cm
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button
from mpl_toolkits.mplot3d import Axes3D

from libspectrumanalyzer import SpectrumAnalyzer

fig = plt.figure(1, figsize=(15, 8))
fig.subplots_adjust(top=0.85)
axspectrum = fig.add_subplot(121)
axspectrum3d = fig.add_subplot(122, projection='3d')

def displayspectrum(rsa):
    axspectrum.set_title('Spectrum')
    axspectrum.set_xlabel('Frequency (GHz)')
    axspectrum.set_ylabel('Amplitude (dBm)')

def updatespectrum(frameNum, rsa):
    if (rsa.initiate == True):
        N = 1
        #print(frameNum)

        spectrum = rsa.getSpectrumTrace()

        if(len(spectrum) == rsa.tracePoints):

            for i, line in enumerate(axspectrum.lines):
                axspectrum.lines.pop(i)
                try:
                    line.remove()
                except:
                    pass

            axspectrum.set_xlim(rsa.freqMin / 1e9, rsa.freqMax / 1e9)
            axspectrum.set_ylim(rsa.refLevel - 80, rsa.refLevel)
            axspectrum.plot(rsa.freq / 1e9, spectrum, 'y')

def displayspectrum3d(rsa):
    axspectrum3d.set_title('Spectrum (3D)')
    axspectrum3d.set_xlabel('Frequency (GHz)')
    axspectrum3d.set_zlabel('Amplitude (dBm)')
    rsa.spectrum3d = None
    rsa.Z = []

def updatespectrum3d(frameNum, rsa):
    if (rsa.initiate == True):
        N = 50
        #print(frameNum)

        spectrum = rsa.getSpectrumTrace()

        if(len(spectrum) == rsa.tracePoints):
            if (len(rsa.Z) == N):
                X = rsa.freq
                Y = np.arange(0, N, 1)
                X, Y = np.meshgrid(X, Y)
                Z = np.array(rsa.Z)

                try:
                    rsa.spectrum3d.remove()
                except:
                    pass

                axspectrum3d.set_zlim(rsa.refLevel - 80, rsa.refLevel)
                rsa.spectrum3d = axspectrum3d.plot_surface(X, Y, Z, cmap=cm.coolwarm, linewidth=0, antialiased=False)
                
                #rsa.Z[:-1] = rsa.Z[1:]
                #rsa.Z[-1] = list(spectrum)
                rsa.Z.pop()

            else:
                #rsa.Z.append(list(spectrum))
                rsa.Z.insert(0, list(spectrum))

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

    anispectrum = FuncAnimation(plt.gcf(), updatespectrum, fargs=(rsa,), init_func=displayspectrum(rsa), interval=1, blit=False)
    anispectrum3d = FuncAnimation(plt.gcf(), updatespectrum3d, fargs=(rsa,), init_func=displayspectrum3d(rsa), interval=1, blit=False)

    fig.canvas.mpl_connect('close_event', rsa.disconnect)
    
    plt.show()

    try:
        rsa.disconnect()
    except:
        pass

def main():
    sap('192.168.1.100', port=34835)

if __name__ == '__main__':
    main()
