import threading

import numpy as np

from socket_instrument import SocketInstrument

class SpectrumAnalyzer:
    def __init__(self, host, port, timeout=60):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.initiate = False

        self.trace = []
        self.tracePoints = 501

        self.cf = 2.45e9
        self.span = 100e6
        self.refLevel = -40

        self.recalculateFrequency()
        
    def connect(self, event=None):
        self.si = SocketInstrument(self.host, self.port, self.timeout)
        self.id = self.si.instId

    def disconnect(self, event=None):
        self.si.disconnect()

    def run(self, event=None):
        if(self.initiate == False):
            self.initiate = True
            t = threading.Thread(target=self.fetchSpectrumTrace)
            t.start()

    def stop(self, event=None):
        self.initiate = False

    def reset(self):
        self.si.write("about")
        self.si.write("*CLS")
        self.si.write("*RST")

    def write(self, string):
        self.si.write(string)

    def query(self, string):
        return self.si.query(string)

    def setCenterFrequencyMHz(self, cfMHz):
        self.setCenterFrequency(np.float32(cfMHz) * 1e6)

    def setCenterFrequency(self, cf):
        self.cf = cf
        self.write('spectrum:frequency:center {}'.format(self.cf))
        self.recalculateFrequency()

    def setSpanMHz(self, spanMHz):
        self.setSpan(np.float32(spanMHz) * 1e6)

    def setSpan(self, span):
        self.span = span
        self.write('spectrum:frequency:span {}'.format(self.span))
        self.recalculateFrequency()

    def recalculateFrequency(self):
        self.freqMin = self.cf - self.span / 2
        self.freqMax = self.cf + self.span / 2
        self.freq = np.linspace(self.freqMin, self.freqMax, self.tracePoints)

    def setReferenceLevel(self, refLevel):
        self.refLevel = int(refLevel)
        self.write('input:rlevel {}'.format(self.refLevel))

    def fetchSpectrumTrace(self):
        while (self.initiate == True):
            #self.write('initiate')
            #self.query('*opc?')
            self.write('fetch:spectrum:trace?')
            self.trace = self.si.binblockread(dtype=np.float32)

    def getSpectrumTrace(self):
        return self.trace
