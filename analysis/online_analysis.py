""" This file contains things for online analysis and provides the interaction
    with the database so that the actual analysis code and the code that stores
    the results can be safely segregated """

from sqlalchemy.orm import object_session
from analysis.abf_analysis import print_tp_stats

def update_online_res_dict(thing,results_dict): #FIXME this might go in the 'dataio.py' file in database??? been awhile since I grocked any of that, looks nuts...
    current_results_dict=thing.online_results #FIXME this could be nasty if is a super large HSTORE
    current_results_dict.update(results_dict)
    thing.online_results=current_results_dict #TODO make sure this works as expected
    session=object_session(thing)
    session.commit()

#TODO ideally what we really want to do is write the stimulaiton and analysis code at the some time so that all the timings match up properly...

#Online analysis
def abf_basic_vc_analysis(datafile): #TODO dump the online stats to the DB?
    Taus,Rss,Rs_ests,Rms=print_tp_stats(datafile.local_path)
    new_results_dict={
            'taus':Taus,
            'rss':Rss,
            'rs_ests':Rs_ests,
            'rms':Rms,
    }
    update_online_res_dict(datafile,new_results_dict)

    return results_dict

def analysis_protocol_lookup(protocol_filename):
    """ get the correct analysis function by protocol name """
    func=lambda:None
    pro_ana_dict={
        '.pro':func
    }

    return pro_ana_dict[protocol_filename]




