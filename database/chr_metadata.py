class cell_metadata:
    WholeCell=None, protocol/experimenal conditions
    LoosePatch=None, protocol/experimenal conditions
    X=None, espX
    Y=None, espY
    Z=None, tomseyeballs
    headstage=None
    abffile_channel=None #should be equivalent to HS
    rheobase=None #FIXME this probably should go in online analysis...
    breakInTime=None #this is a time, time usually goes in the regular location...


class slice_metadata:
    coordinates=None #aka ap_pos
    hemisphere=None


#TODO *which* metadata does pipette resistance belong to?!?! cell? df?
#I think it is cell just like hs_id is in cell md
