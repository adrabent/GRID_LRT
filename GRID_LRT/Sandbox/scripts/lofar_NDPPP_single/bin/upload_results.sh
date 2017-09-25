#!/bin/bash

function upload_results(){
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading_results'
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

 case "${PIPELINE}" in
    ndppp_cal) upload_results_cal ;;
    ndppp_targ) upload_results_targ ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac

}


function upload_results_cal(){

 uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/leah/${OBSID} 
 tar -cvf ${OBSID}_SB${STARTSB}.tar *_iflag.MS
 globus-url-copy ${OBSID}_SB${STARTSB}.tar  gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/leah/${OBSID}/
 cp *clean0-image.fits ${JOBDIR}
}

function upload_results_targ(){

         globus-url-copy file:`pwd`/calib_solutions.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_sols/${OBSID}_solutions.tar
        wait
}



function upload_results_from_token(){

echo ""

}