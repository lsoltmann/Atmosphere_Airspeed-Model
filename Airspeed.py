# Description: Airspeed class used to convert airspeeds from
#              one type to another based on altitude.
#
# References:
#    [1] https://en.wikipedia.org/wiki/Calibrated_airspeed
#    [2] https://en.wikipedia.org/wiki/Equivalent_airspeed
#    [3] https://en.wikipedia.org/wiki/True_airspeed

import numpy as np
from Atmosphere.Atmosphere import Atmosphere

class Airspeed:
    def __init__(self):
        # Load the atmosphere model (standard atmosphere)
        self.ATMOSPHERE = Atmosphere()
        # Define conversion constants
        self.kts_fps = 1.6878099
        # Get sea level conditions
        ATMO = self.ATMOSPHERE.GetConditions(0)
        self.RHO_SL = ATMO['DENSITY']
        self.P_SL   = ATMO['PRESSURE']
        self.SOS_SL = ATMO['SPEEDOFSOUND']

    # Returns a dictionary of speeds based on the input speed(s) and altitude(s).
    # The inputs must fall into one of the following cases:
    #     1. Both are single inputs - output = single value in a 1d array
    #     2. One is a single input and the other is an 1d array - output = 1d array
    #     3. Both are 1d arrays or lists - output = axb 2d array where 'a' is len(ALT)
    #        'b' is len(SPEED)
    def GetSpeeds(self,ALT,SPEED,TYPE):
        # Convert 'float', 'int', 'list' to a 1D numpy array
        if isinstance(ALT,int) or isinstance(ALT,float):
            ALT = np.array([ALT])
        elif isinstance(ALT,list):
            ALT = np.array(ALT)
        # Get shape
        AltShape = np.shape(ALT)
        
        if isinstance(SPEED,int) or isinstance(SPEED,float):
            SPEED = np.array([SPEED])
        elif isinstance(SPEED,list):
            SPEED = np.array(SPEED)
        # Get shape
        SpeedShape = np.shape(SPEED)

        # Check to make sure the input conforms to the one of the required cases
        # Case 1/2 - at least one is a single inputs
        if ((np.size(ALT)==1 and np.size(SPEED)==1) or # both single values
        (np.size(ALT)==1 and (SpeedShape[0] == np.size(SPEED))) or # alt is single, speed is 1d
        (np.size(SPEED)==1 and (AltShape[0] == np.size(ALT)))): # alt is 1d, speed is 1d
            OutputShape = 1
        # Case 3 - both are 1d arrays
        elif (AltShape[0] == np.size(ALT)) and (SpeedShape[0] == np.size(SPEED)):
            OutputShape = 2
        else:
        # If the inputs do not conform, output an empty dictionary
            OutputShape = 0
        # Initialize an empty dictionary
        Output = {}

        if OutputShape > 0:
            # Get atmospheric conditions
            ATMO = self.ATMOSPHERE.GetConditions(ALT)
            # Convert the input TYPE to ft/s
            if TYPE[0].upper() == 'K':
                SPEED = SPEED*self.kts_fps
            # Calculate pressure and density ratios
            Pratio = ATMO['PRESSURE']/self.P_SL
            Dratio = ATMO['DENSITY']/self.RHO_SL
            SOS    = ATMO['SPEEDOFSOUND']
            if OutputShape == 2:
                Pratio = np.reshape(Pratio,(np.size(Pratio),1))
                Dratio = np.reshape(Dratio,(np.size(Dratio),1))
                SOS    = np.reshape(SOS,(np.size(SOS),1))
            # Calcluate all airspeeds based on input type
            if TYPE.upper() in ['KTAS','VTAS']:
                # The input speed is just repeated in the output, but it must be of the correct shape
                if OutputShape == 1:
                    Output['VTAS'] = SPEED*np.ones(AltShape)
                elif OutputShape == 2:
                    Output['VTAS'] = SPEED*np.ones((AltShape[0],1))
                # Calculate the other speeds
                Output['KTAS'] = Output['VTAS']*(1/self.kts_fps)
                Output['VEAS'] = Output['VTAS']*np.sqrt(Dratio)
                Output['KEAS'] = Output['VEAS']*(1/self.kts_fps)
                Output['MACH'] = Output['VTAS']*(1/SOS)
                Output['VCAS'] = Output['VEAS']*(1+0.125*(1-Pratio)*Output['MACH']**2+0.0046875*(1-10*Pratio+9*Pratio**2)*Output['MACH']**4)
                Output['KCAS'] = Output['VCAS']*(1/self.kts_fps)
                Output['VIAS'] = Output['VCAS']
                Output['KIAS'] = Output['KCAS']
                
            elif TYPE.upper() in ['KIAS','VIAS','KCAS','VCAS']:
                # The input speed is just repeated in the output, but it must be of the correct shape
                if OutputShape == 1:
                    Output['VIAS'] = SPEED*np.ones(AltShape)
                elif OutputShape == 2:
                    Output['VIAS'] = SPEED*np.ones((AltShape[0],1))
                Output['KIAS'] = Output['VIAS']*(1/self.kts_fps)
                Output['KCAS'] = Output['KIAS']
                Output['VCAS'] = Output['VIAS']
                # Calculate impact pressure [1]
                qc = self.P_SL*((Output['VCAS']**2/(5*self.SOS_SL**2))+1)**(7/2)-self.P_SL
                # Calculate EAS [2]
                Output['VEAS'] = self.SOS_SL*np.sqrt(5*Pratio*(((qc/(Pratio*self.P_SL))+1)**(2/7)-1))
                Output['KEAS'] = Output['VEAS']*(1/self.kts_fps)
                # Calculate the other speeds
                Output['VTAS'] = Output['VEAS']*np.sqrt(1/Dratio)
                Output['KTAS'] = Output['VTAS']*(1/self.kts_fps)
                Output['MACH'] = Output['VTAS']*(1/SOS)

            
            elif TYPE.upper() in ['KEAS','VEAS']:
                # The input speed is just repeated in the output, but it must be of the correct shape
                if OutputShape == 1:
                    Output['VEAS'] = SPEED*np.ones(AltShape)
                elif OutputShape == 2:
                    Output['VEAS'] = SPEED*np.ones((AltShape[0],1))
                # Calculate the other speeds
                Output['KEAS'] = Output['VEAS']*(1/self.kts_fps)
                Output['VTAS'] = Output['VEAS']*np.sqrt(1/Dratio)
                Output['KTAS'] = Output['VTAS']*(1/self.kts_fps)
                Output['MACH'] = Output['VTAS']*(1/SOS)
                Output['VCAS'] = Output['VEAS']*(1+0.125*(1-Pratio)*Output['MACH']**2+0.0046875*(1-10*Pratio+9*Pratio**2)*Output['MACH']**4)
                Output['KCAS'] = Output['VCAS']*(1/self.kts_fps)
                Output['KIAS'] = Output['KCAS']
                Output['VIAS'] = Output['VCAS']
                
            elif TYPE.upper() == 'MACH':
                # The input speed is just repeated in the output, but it must be of the correct shape
                if OutputShape == 1:
                    Output['MACH'] = SPEED*np.ones(AltShape)
                elif OutputShape == 2:
                    Output['MACH'] = SPEED*np.ones((AltShape[0],1))
                # Calculate the other speeds
                Output['VTAS'] = Output['MACH']*SOS
                Output['KTAS'] = Output['VTAS']*(1/self.kts_fps)
                Output['VEAS'] = Output['VTAS']*np.sqrt(Dratio)
                Output['KEAS'] = Output['VEAS']*(1/self.kts_fps)
                Output['VCAS'] = Output['VEAS']*(1+0.125*(1-Pratio)*Output['MACH']**2+0.0046875*(1-10*Pratio+9*Pratio**2)*Output['MACH']**4)
                Output['KCAS'] = Output['VCAS']*(1/self.kts_fps)
                Output['KIAS'] = Output['KCAS']
                Output['VIAS'] = Output['VCAS']
                              
        return Output
            
            
