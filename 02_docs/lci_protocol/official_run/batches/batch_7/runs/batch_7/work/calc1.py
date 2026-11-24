import bwx
ELEC='42ec2f4634364ee86921b4c6dfe2de31'; HEAT='eda02fda34ab477c467e7913b32b7649'; MACH='5a0b37c3a698f020385f42dbdfbf1b1f'
CHIPS='0f745572d5c532c4b19eaf202f8123b7'; PUR='387dfd53d03ac4257183b4557377608c'; PARA='2a6ee0cf5ef883afd641ac5e84a2aa7b'; AL='38b174060ab1bc1ab84e81c0a75f7666'
print('heat MJ',bwx.gwp([(HEAT,1)])[0])
# SWFB built
elec=0.265+0.125+2*2.2/6000+13.5/6000+0.05/0.685
heat=(0.91+1.095+0.21/0.685)*3.6
wear=51600/(62500*1e5)+36000/(3200*1e5)
items=[(CHIPS,0.945),(PUR,0.04),(PARA,0.015),(ELEC,elec),(HEAT,heat),(MACH,wear)]
t,per=bwx.gwp(items); print('SWFB built',t,per,'elec',elec,'heat MJ',heat,'wear',wear,'wear share',per[-1]/t)
# Al built
elec=0.196; heat=(0.195+0.080)*3.6
t,per=bwx.gwp([(AL,1),(ELEC,elec),(HEAT,heat)]); print('Al built',t,per)
