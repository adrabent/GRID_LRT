#########
#Fields LRT reduces a field automatically by keeping track of states of different stages
#
#
#######
import sys,os
sys.path.append('./LRT/classes')

import pdb

from class_prefactor_LRT import pref_LRT
import time

class Field(object):
    '''The Field object holds information for each field. It contains OBSIDs, srms, parsets, 
        as well as the steps to be run in an ordered list. Adding a step links it to the previous step
        so that upon starting it can check whether the previous step has completed (and loop if not)
    '''
    def __init__(self,name=""):
        self.name=name
        self.OBSIDs={}
        self.srms={}
        self.parsets={}
        self.steps=[]

    def add_step(self,step):
        '''Adds a link for each step to check if its predecessor has finished
        '''
        if len(self.steps)==0:
            self.steps.append(step)
        else:
            step.prev_step=self.steps[len(self.steps)-1]
            self.steps.append(step)

    
    def initialize(self,targ_OBSID,tim_avg=4,freq_avg=4):
        '''Initializes the field object by calculating the averaging parameters (default is 4 chan/SB and 4sec)
            initialize also calls find_cal_obsid which searches a (hardcoded???) file for a matching calibrator
            if there are no list of URI links to either calibrator of target, the field object exits here.
        '''
        self.OBSIDs['targ']=targ_OBSID
        self.OBSIDs['cal']=self.find_cal_obsid(targ_OBSID)
        (self.parsets['cal'],self.parsets['targ'])=self.create_field_parsets(tim_avg,freq_avg)
        self.srms['cal']=self.findsrm('SKSP/srmfiles',self.OBSIDs['cal'])
        self.srms['targ']=self.findsrm('SKSP/srmfiles',self.OBSIDs['targ'])
        if len(self.srms['cal'])==0 or len(self.srms['targ'])==0:
            print "Srms failed to be found"
            print self.srms
            sys.exit()


    def find_cal_obsid(self,targ_Obsid):
        cal_OBSID=""
        allcals=[]
        with open("SKSP/fields.txt","r") as cal_file:
            for i in cal_file:
                allcals.append(i.split(','))
        for i in allcals: 
            if "L"+i[0]==str(targ_Obsid):
                cal_OBSID="L"+i[5]

        #TODO: This 
        return cal_OBSID

    def create_field_parsets(self,tim_avg,freq_avg):
        '''Uses the modify_parsets function to add the Calibrator/Target OBSID, and averaging 
            parameters, then write out to a field specific parsets (Fields are labeled as 'field_'+targ_obsid
        '''
        orig_parsets=("Pre-Facet-Calibrator.parset","Pre-Facet-Target.parset")
        filedata=None
        for tar_cal in [0,1]:
            filename=orig_parsets[tar_cal]
            filedata=self.modify_parsets(tim_avg[tar_cal],freq_avg[tar_cal],filename)
            with open(os.path.splitext(filename)[0]+"_"+self.name+".parset",'w') as file:
                file.write(filedata)
            if "Calibrator" in filename:
                cal_parset=os.path.splitext(filename)[0]+"_"+self.name+".parset"
            elif "Target" in filename:
                targ_parset=os.path.splitext(filename)[0]+"_"+self.name+".parset" 
        return(cal_parset,targ_parset)


    def modify_parsets(self,time,freq,parset):
        '''Some regular expressions that will hopefully not need refactoring \s\S matches one+Spaces
        '''
        with open(parset,'r') as file:
            filedata = file.read()
            import re
            filedata=re.sub(r'\! avg_timestep\s+=\s\S?',"! avg_timestep         = "+str(time),filedata)
            filedata=re.sub(r'\! avg_freqstep\s+=\s\S?',"! avg_freqstep         = "+str(freq),filedata)
            filedata=re.sub(r'\! cal_input_pattern\s+=\s\S+',"! cal_input_pattern    = "+str(self.OBSIDs['cal'])+"*MS",filedata)
            filedata=re.sub(r'\! target_input_pattern\s+=\s\S+',"! target_input_pattern    = "+str(self.OBSIDs['targ'])+"*MS",filedata)
            return filedata
      

    def findsrm(self,srmfolder,obsid):
        '''Automates srmfile traversing by finding an list of SURLS based on the OBSID
            It traverses all the srms in a folder (assuming one OBSID/file) but even 
            concatenated files are ok as long as the LRT processing the OBSID calls split_srms()
        '''
        import mmap
        srmfiles=[]
        for fn in os.listdir(srmfolder):
            try:
                with open(srmfolder+'/'+fn,'r') as srmf:
                    s = mmap.mmap(srmf.fileno(), 0, access=mmap.ACCESS_READ)
                    if s.find(obsid) != -1:
                        srmfiles.append(srmfolder+'/'+fn)
                        print obsid+" was found in "+fn
            except:
                pass
        return srmfiles

class processing_step(object):
    '''Generic processing step class (Currently only staging and prefactor implemented)
        It has a start() method that needs to be run by all children (!!!) before processing
        And a get_progress() method which should throw an error if not implemented in children ( TODO )  
    '''
    def __init__(self,name=""):
        self.name=name
        self.start_time=0.0
        self.progress=0.0
        self.done=False
        self.token=""
        self.prev_step=None

    def start(self):
        if self.prev_step:
            while self.prev_step.progress<1.0:
                print "Previous step hasn't finished"
                time.sleep(120)
                self.prev_step.check_progress()
        self.start_time=time.time()


    def check_progress(self):
        raise NotImplementedError

       

class Stage_step(processing_step):
    def start(self,srmfile="srmtxt",threshold=0.05,sleep=120):
        ''' Stages the surls in the srmfile and continues only if less than the
           threshold are unstaged (threshold goes from 0->1) 
        '''
        processing_step.start(self)
        import re
        from class_prefactor_LRT import pref_LRT
        print self.start_time
        self.threshold=threshold
        self.l=pref_LRT()
        self.l.srmfile = srmfile

        with open(srmfile,'r') as f:
            line=f.readline()
            self.l.OBSID='L'+str(re.search("L(.+?)_",line).group(1))

        self.l.setup_dirs()
        self.l.parsetfile=""
        self.l.nostage=False
        self.l.ignoreunstaged=True
        self.l.check_state_and_stage() 
        self.progress=1-(self.l.perc_left -self.threshold)
        if self.l.perc_left <= self.threshold:
            self.stop_time=time.time()
            self.done=True
            self.progress=1.0
            print "exiting, done"
            return
        else:
            self.progress=1-(self.l.perc_left -self.threshold)
            print self.progress
            while not self.done:
                time.sleep(sleep)
                self.stop_time=time.time()
                self.check_progress()
   
    def check_progress(self):
        '''Uses the LRT class to check the state of the files 
            calculates the progress (taking the threshold in account) 
            and only finishes the step if the threshold of unstaged files is reached
        '''
        self.l.check_state_and_stage()
        self.progress=1-(self.l.perc_left -self.threshold)
        if self.l.perc_left < self.threshold:
            self.done=True
            self.progress=1.0
        return


class pref_Step(processing_step):
    def start(self,srmfile,parset,OBSID,fieldname,args=[]):
        print parset
        processing_step.start(self)
        self.LRT=pref_LRT() 
        self.LRT.parse_arguments(args+[srmfile,parset]) #include srmfile, parset of calib

        self.LRT.OBSID=OBSID
        self.LRT.parsetfile=os.environ['PWD']+"/"+parset
        self.LRT.srmfile=os.environ['PWD']+"/"+srmfile[0]

        self.LRT.setup_dirs()
        self.LRT.prepare_sandbox()
        self.LRT.jdlfile="remote_prefactor.jdl"
        #pdb.set_trace()
        import itertools
        progress_keys={'times':{}}
        progress_keys["times"]["queued"]=time.time()
        s=self #why? #oh nvm, this hella cool
        while True:
            try:
                s=s.prev_step #recursively adds the start times of all the previous steps into the token
                progress_keys["times"][s.name+"_start"]=s.start_time
            except:
                break
        other_keys={"pipeline":self.name,"progress":0,"status":"queued"}
        all_keys = dict(itertools.chain(other_keys.iteritems(), progress_keys.iteritems()))
        self.LRT.submit_to_picas(pref_type="_"+fieldname,add_keys=all_keys)
        self.LRT.start_jdl()     
        return


    def check_progress(self):
        '''Takes all the token from the step_obj.LRT.tokens (which are created in default_LRT.submit_to_picas()
            and checks if all of them are set as 'done' (done by pilot.py upon successful completion).
            The progress is currently {0,1} but I may find a way to make it a float  
        '''
        import couchdb
        server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (os.environ['PICAS_USR'],os.environ['PICAS_USR_PWD'])
        db = server[os.environ['PICAS_DB']] 
        for i in self.LRT.tokens:       #Goes through all the tokens launched in this step and checks
            if db[i]['status']!='done': #if any of them are not done, and returns step finished only
                return                  #if al of the tokens are 'done'
        self.done=True
        self.progress=1.0
        self.stop_time=time.time()




