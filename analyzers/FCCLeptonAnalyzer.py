from heppy.framework.analyzer import Analyzer
from heppy.utils.deltar import inConeCollection
from heppy.statistics.average import Average
from heppy_fcc.particles.physicsobjects import Particle 


class FCCLeptonAnalyzer(Analyzer):

    def beginLoop(self, setup):
        # call the function of the base class defining self.counters
        # and self.averages
        super(FCCLeptonAnalyzer, self).beginLoop(setup)
        self.counters.addCounter('leptons')
        self.counters['leptons'].register('all events')
        self.counters['leptons'].register('at least 1 lepton')
        self.counters['leptons'].register('lepton iso < 0.1')
        self.averages.add('lepton_iso', Average('lepton_isolation'))
        
    def process(self, event):

        self.counters['leptons'].inc('all events')
        # just a shortcut
        store = event.input
        # access particles, filter out particles with Type as specified in the config file,
        # and store in the event
        particles = map(Particle, store.get("GenParticle"))
        leptons = [ptc for ptc in particles
                   if abs(ptc.read().Core.Type) == self.cfg_ana.id ]
        # kinematic selection and ID
        leptons = [lep for lep in leptons if self.kine_sel(lep) and self.id_sel(lep)]

        # isolation
        for lepton in leptons:
            lepton.incone = inConeCollection(lepton, particles, deltaRMax=1.)
            lepton.iso = sum( ptc.read().Core.P4.Pt for ptc in lepton.incone)
            self.averages['lepton_iso'].add(lepton.iso)
            
        if(len(leptons)>0):
            self.counters['leptons'].inc('at least 1 lepton')
            if(leptons[0].iso < 0.1):
                self.counters['leptons'].inc('lepton iso < 0.1')
                
        # add to the event, with the name given in the config file
        setattr( event, self.cfg_ana.coll_name, leptons)
        if( not hasattr(event, 'leptons') ):
            event.leptons = []
        # if several LeptonAnalyzers run, event.leptons contains all leptons
        # identified by these analyzers
        event.leptons.extend(leptons) 
        
    def kine_sel(self, particle):
        p4 = particle.read().Core.P4
        if( p4.Pt > self.cfg_ana.pt and \
            abs(p4.Eta) < self.cfg_ana.eta ):
            return True
        else:
            return False

    def id_sel(self, lepton):
        the_type = lepton.read().Core.Type
        if the_type == 4:
            return self.electron_id_sel(lepton)
        elif the_type == 5:
            return self.muon_id_sel(lepton)

    # the following is temporary:
    # all leptons are considered to be identified for now
        
    # the rhs is a lambda statement defining a 2-parameter function
    # that returns True.
    # this function is bound to this class with the name dummy_id_sel
    dummy_id_sel = lambda x, y: True

    # the function electron_id_sel is in fact dummy_id_sel
    electron_id_sel = dummy_id_sel

    # same for muon id
    muon_id_sel = dummy_id_sel
