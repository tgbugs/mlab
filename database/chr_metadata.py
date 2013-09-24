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
    #frame of reference stuff for automatically driving the rig
    spline=None
    layer23coords=None
    surfaceCoords=None
    #choices... these should be from espX and espY and there should be 5 each, that is how the should be SAVED but I need an invertible function that will convert between the np array used for actually calculating the spline and the data stored in the db, fortunately alot of this stuff is going to go in the online analysis which probably will be done before writing to the database since that will maintain consistency in the event that something happens befroe the online analysis finishes? think think think
    scoord1=None
    scoord2=None


#TODO *which* metadata does pipette resistance belong to?!?! cell? df?
#I think it is cell just like hs_id is in cell md
