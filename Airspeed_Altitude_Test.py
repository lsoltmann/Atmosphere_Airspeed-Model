from Airspeed import Airspeed
from Atmosphere.Atmosphere import Atmosphere

ASPD = Airspeed()
ATM  = Atmosphere()

# ---- Airspeed ----
#AS_Out = ASPD.GetSpeeds([10000,15000,20000],150,'KEAS')
#AS_Out = ASPD.GetSpeeds(10000,150,'KTAS')
#AS_Out = ASPD.GetSpeeds(10000,[150,200,250],'KTAS')
AS_Out = ASPD.GetSpeeds([10000,20000,30000,],[100,200,300],'KEAS')
#AS_Out = ASPD.GetSpeeds(100,np.random.random((5,2)),'KTAS')

# ---- Altitude ----
ATM.SetType('TROPICAL')
AT_Out = ATM.GetConditions([0,10000,20000,30000])
#AT_Out = ATM.GetConditions(1000)

print('AIRSPEED OUTPUT:')
for key,value in AS_Out.items():
    print(key,': ',value)

print('\n')

print('ALTITUDE OUTPUT:')
for key,value in AT_Out.items():
    print(key,': ',value)
