import numpy as np
import matplotlib.pyplot as plt
from logging import getLogger


class QuasiparticleTimeStream:
    """ A time series with values proportional to the change in quasiparticle density relative to the
    quasiparticle density when there are no photons hitting the depvice.
    ...
    Attributes:
     @type fs: float
         sample rate [Hz]
     @type ts: float
         sample time [uSec]
     @type tvec: np.array
         time vector [Sec]
     @type points: int
         number of samples
     @type data_nonoise: np.array
         timestream with no added noise
     @type photon_arrivals: np.array of booleans
          whether or not a photon arrived in that time step
    1 per quasiparticle = 2 * gap energy
    # qp = photon energy / (2*gap energy) * efficiency_factor
    # normalized quasiparticle timestream
    # some class knows constants that turn it into frequency shifts (material dependent)
    # energy of photon
    # usually want 90 degree phase response
     """

    def __init__(self, fs, ts):
        self.fs = fs #Hz
        self.ts = ts #sec
        self.points = int(self.ts * self.fs)
        self.tvec = np.arange(0, self.points) / self.fs
        self.data = np.zeros(self.points)
        self._holdoff = None
        self.photon_arrivals = None
        self.photon_pulse = None
        self.pulse_time = None

    @property
    def dt(self):
        return self.tvec[1]-self.tvec[0]

    def plot_timeseries(self, data, ax=None, fig=None):
        plt.figure()
        plt.plot(self.tvec, data)
        plt.xlabel('time (sec)')
        plt.ylabel(r"$\propto \Delta$ Quasiparticle Density")

    def gen_quasiparticle_pulse(self, magnitude=1, tf=30):
        """generates an instantaneous change in quasipaprticle density
         which relaxes in tf fall time in usec."""
        tp = np.linspace(0, 10 * tf, int(self.fs*(10 * tf * 1e-6)))  # pulse duration
        self.photon_pulse = magnitude*np.exp(-tp / tf)
        self.pulse_time = tp

    def plot_pulse(self, ax=None, fig=None):
        plt.figure()
        plt.plot(self.pulse_time, self.photon_pulse)
        plt.xlabel('Time (usec)')
        plt.ylabel(r"$\propto \Delta$ Quasiparticle Density")

    def gen_photon_arrivals(self, seed=3, cps=500):
        """ generate boolean list corresponding to poisson-distributed photon arrival events.
        Inputs:
        - cps: int, photon co
        unts per second.
        """
        self.photon_arrivals = None
        rng = np.random.default_rng() if seed == None else np.random.default_rng(seed = seed)
        photon_events = rng.poisson(cps / self.fs, self.tvec.shape[0])
        self.photon_arrivals = np.array(photon_events, dtype=bool)
        if sum(photon_events) > sum(self.photon_arrivals):
            getLogger(__name__).warning(f'More than 1 photon arriving per time step. Lower the count rate?')
        if sum(photon_events) == 0:
            getLogger(__name__).warning(f"Warning: No photons arrived. :'(")
        return self.photon_arrivals

    def populate_photons(self):
        self.data = np.zeros(self.points)
        for i in range(self.data.size - self.photon_pulse.shape[0]):
            if self.photon_arrivals[i]:
                self.data[i:i + self.photon_pulse.shape[0]] = self.photon_pulse
        return self.data
