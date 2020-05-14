## This is phiCDM cosmology

import numpy as np
from LCDMCosmology import *
from scipy.interpolate import interp1d
from scipy.integrate import odeint
from ParamDefs import plam_par, palp_par, pbeta_par, quipha_par
from scipy.optimize import newton

class PhiCosmology(LCDMCosmology):
    def __init__(self, poten='pow', varyalpha=False, varybeta=False,\
                 varyilam=False, varyquipha=False):
        """Is better to start the chains at masses equal one, othewise
        may take much longer"""


        self.poten    = poten  #Pow-law = pow, Exp = exp

        self.varyilam   = varyilam
        self.varybeta   = varybeta
        self.varyalpha  = varyalpha
        self.varyquipha = varyquipha

        self.alpha  = palp_par.value
        self.beta   = pbeta_par.value
        self.ilam   = plam_par.value
        self.qp     = quipha_par.value     #1=Quintes, -1=Panthom

        self.lna   = np.linspace(-5, 0, 400)
        self.z     = np.exp(-self.lna) - 1.
        self.zvals = np.linspace(0, 5, 200)

        self.ini_gamma = 1.0e-4

        LCDMCosmology.__init__(self, mnu=0)
        self.updateParams([])

    ## my free parameters. We add Ok on top of LCDM ones (we inherit LCDM)
    def freeParameters(self):
        l=LCDMCosmology.freeParameters(self)
        if (self.varyilam)   : l.append(plam_par)
        if (self.varybeta)   : l.append(pbeta_par)
        if (self.varyalpha)  : l.append(palp_par)
        if (self.varyquipha) : l.append(quipha_par)
        return l


    def updateParams(self,pars):
        ok=LCDMCosmology.updateParams(self, pars)
        if not ok:
            return False
        for p in pars:
            if p.name  == "plam":
                self.ilam= p.value
            if p.name  == "palp":
                self.alpha= p.value
            if p.name  == "pbeta":
                self.beta= p.value
            if p.name  == "quipha":
                self.qp= p.value
        self.set_ini()


        """ Testing
        import matplotlib.pyplot as plt
        dataHz = np.loadtxt('data/Hz_all.dat')
        redshifts, obs, errors = [dataHz[:,i] for i in [0,1,2]]
        plt.errorbar(redshifts, obs, errors, xerr=None,
                     color='purple', marker='o', ls='None',
                     elinewidth =2, capsize=5, capthick = 1, label='$Datos$')
        plt.xlabel(r'$z$')
        plt.ylabel(r'$H(z) [km/s Mpc^{-1}]$')
        plt.plot(self.zvals, [67.4*np.sqrt(self.RHSquared_a(1./(1+z))) for z in self.zvals])
        #plt.plot(self.zvals, [67.4*np.sqrt(self.hubble(1./(1+z))) for z in self.zvals])
        plt.title('mquin %f'%(self.alpha))
        plt.show()
        """
        return True


    def MG(self, lam):
        if self.poten == 'pow':
            return (self.alpha-1)/self.alpha*lam**2
        elif self.poten == 'exp':
            if self.alpha == 1:
                return 1
            else:
                fac = (self.alpha-1)/(self.beta*self.alpha)
                return 1 + fac*(lam/np.abs(self.beta*self.alpha))**(-self.alpha/(self.alpha-1))


    def RHS(self, x_vec, lna):
        gamma, Ophi, lam, hub = x_vec

        Mgamma= self.MG(lam)

        gamma_prime = (2 - self.qp*gamma)*(-3*gamma + lam*np.sqrt(3*gamma*Ophi))
        Ophi_prime  = 3*Ophi*((1-self.qp*gamma)*(1-Ophi))
        hub_prime   = -1.5*hub*(1 + (self.qp*gamma-1)*Ophi)
        if self.alpha ==0 or self.beta ==0:
            lam_prime =0
        else:
            lam_prime   = -np.sqrt(3)*lam**2*(Mgamma -1)*np.sqrt(gamma*Ophi)

        return [gamma_prime, Ophi_prime, lam_prime, hub_prime]



    def solver(self, ini_Ophi):
        phi0 = self.ilam
        if self.varyilam:
            ini_lam  =  self.alpha/phi0
        else:
            if self.poten == 'pow':
                ini_lam  =  self.alpha/phi0
            elif self.poten == 'exp':
                if self.alpha == 1:
                    ini_lam = self.beta
                else:
                    ini_lam  = self.beta*self.alpha*phi0**(self.alpha-1)

        ini_lam  = np.abs(ini_lam)
        ini_hub  = 100*self.h*self.Ocb**0.5*np.exp(-1.5*self.lna[0])
        y0       = [self.ini_gamma, 10**(-ini_Ophi), ini_lam, ini_hub]
        y_result = odeint(self.RHS, y0, self.lna, h0=1E-10)
        return y_result


    def logatoz(self, func):
        #change functions from lna to z
        tmp     = interp1d(self.lna, func)
        functmp = tmp(self.lna)
        return  np.interp(self.zvals, self.z[::-1], functmp[::-1])


    def rfunc(self, ini_Ophi0):
        #returns lambda that's solution
        sol  = self.solver(ini_Ophi0).T
        return (1-self.Om) - sol[1][-1]


    def set_ini(self):
        try:
            Ophi0 = newton(self.rfunc, 6)
            x_vec = self.solver(Ophi0).T
            self.do = 1
            self.hub_SF   = interp1d(self.lna, x_vec[3])
            #self.hub_SF_z = self.logatoz(x_vec[3])
            #self.w_eos    = interp1d(self.lna, x_vec[0])
        except RuntimeError:
            if np.abs(self.alpha) < 0.02: self.do = 0
            else:
                print('troubles', self.alpha, self.beta, self.ilam)
                self.do = 2





    def hubble(self, a):
        Ode = 1.0-self.Om
        return self.Ocb/a**3 + self.Omrad/a**4 + Ode


    ## this is relative hsquared as a function of a
    ## i.e. H(z)^2/H(z=0)^2
    def RHSquared_a(self,a):
        lna = np.log(a)
        if self.do==0:
            return self.hubble(a)
        elif self.do==1:
            if (lna > self.lna[0]):
                hubble = (self.hub_SF(lna)/100./self.h)**2.
            else:
                hubble = self.hubble(a)
        else:
            return 1.
        return hubble


    def w_de(self, a):
        lna = np.log(a)
        return self.qp*self.w_eos(lna)-1

