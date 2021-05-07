from scipy import interpolate as interp
import pandas as pd
import numpy as np

# Atmosphere files must contain the following headers at minimum:
#   Geometric altitude (ft)
#   Temperature (degR)
#   Temperature (degF)
#   Ambient pressure (lb/ft^2)
#   Density (slug/ft^3)
#   Speed of sound (ft/sec)
#   Absolute viscosity (lb-sec/ft^2)

class Atmosphere:
    def __init__(self):
        # Atmosphere options and associated lookup table files
        self.AtmosphereTables = {
        'STANDARD':'./Atmosphere/Atmosphere_Standard.csv',
        'POLAR':'./Atmosphere/Atmosphere_Polar.csv',
        'TROPICAL':'./Atmosphere/Atmosphere_Tropical.csv'}
        # Default atmosphere
        self.AtmoType = 'STANDARD'
        # Loaded atmosphere
        self.AtmosphereTable  = None
        # Atmosphereic properties functions
        self.Temperature_F = None
        self.Temperature_R = None
        self.Pressure      = None
        self.Density       = None
        self.SpeedOfSound  = None
        self.Viscosity     = None
        # Load the default atmosphere
        self.LoadAtmosphere()


    def SetType(self,Type):
        # Type can be: 'STANDARD', 'POLAR', 'TROPICAL'
        self.AtmoType = Type.upper()
        self.LoadAtmosphere()
        return None


    def GetConditions(self,ALT):
        # Get shape of altitude to make sure output is the same shape
        AltShape = np.shape(ALT)
        # Initialize an empty dictionary
        Output = {}
        # Add all interpolated outputs to the dictionary
        Output['TEMPERATURE_F'] = np.reshape(self.Temperature_F(np.squeeze(ALT)),AltShape)
        Output['TEMPERATURE_R'] = np.reshape(self.Temperature_R(np.squeeze(ALT)),AltShape)
        Output['PRESSURE']      = np.reshape(self.Pressure(np.squeeze(ALT)),AltShape)
        Output['DENSITY']       = np.reshape(self.Density(np.squeeze(ALT)),AltShape)
        Output['SPEEDOFSOUND']  = np.reshape(self.SpeedOfSound(np.squeeze(ALT)),AltShape)
        Output['VISCOSITY']     = np.reshape(self.Viscosity(np.squeeze(ALT)),AltShape)
        return Output

        
    def LoadAtmosphere(self):
        # Open atmosphere file
        self.AtmosphereTable = pd.read_csv(self.AtmosphereTables[self.AtmoType])
        # Build interpolation models
        self.Temperature_F = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Temperature_F'],
                                             bounds_error=False,fill_value='extrapolate')
        self.Temperature_R = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Temperature_R'],
                                             bounds_error=False,fill_value='extrapolate')
        self.Pressure      = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Pressure_PSF'],
                                             bounds_error=False,fill_value='extrapolate')
        self.Density       = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Density_slug_ft3'],
                                             bounds_error=False,fill_value='extrapolate')
        self.SpeedOfSound  = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Speed_of_Sound_FPS'],
                                             bounds_error=False,fill_value='extrapolate')
        self.Viscosity     = interp.interp1d(self.AtmosphereTable['Geometric_Altitude_ft'],
                                             self.AtmosphereTable['Absolute_Viscosity_lbsec_ft2'],
                                             bounds_error=False,fill_value='extrapolate')
        return None
