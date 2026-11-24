from bwlib import *
def A(name,loc,prod=None):
    r=[a for a in db if a['name']==name and a['location']==loc and (prod is None or a['reference product']==prod)]
    assert len(r)>=1,(name,loc)
    return r[0]
ELEC=A("market group for electricity, medium voltage","RER")
HEAT=A("market for heat, district or industrial, natural gas","Europe without Switzerland")
MACH=A("market for industrial machine, heavy, unspecified","RER")
LORRY=A("market for transport, freight, lorry, unspecified","RER")
SEA=A("market for transport, freight, sea, container ship, heavy fuel oil","GLO")
DIESEL=A("diesel, burned in building machine","GLO")
