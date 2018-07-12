'''
WRITE DESCRIPTION HERE!

This script takes as argument the name of the animal to process.

TO DO:
- Make sure inforec files get reloaded (by celldatabase.py)
'''

from jaratoolbox import settings

import database_generic
reload(database_generic)
import database_photoidentification
reload(database_photoidentification)
import database_inactivation
reload(database_inactivation)
import subjects_info
reload(subjects_info)

 
# creates and saves a database for photoidentified cells
chr2mice = subjects_info.PV_CHR2_MICE + subjects_info.SOM_CHR2_MICE
basicDB = database_generic.generic_database(chr2mice)
database_photoidentification.photoIDdatabase(basicDB, baseStats = True, indices = True)

# creates and saves a database for inactivation
archTmice = subjects_info.PV_ARCHT_MICE + subjects_info.SOM_ARCHT_MICE
basicDB = database_generic.generic_database(archTmice)
database_inactivation.inactivation_database(basicDB, baseStats = True, indices = True)