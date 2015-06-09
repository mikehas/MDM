select mmp.*,
   (select CleanPhone from Phones ph, MatchedPhone mph where ph.sourceid = mph.sourceid and mph.masterid = mmp.masterid limit 1) as Phone,
   (select Specialty from MatchedPrimarySpecialties mps where mps.masterid = mmp.masterid limit 1) as PrimarySpecialty,
   (select Specialty from MatchedSecondarySpecialties mss where mss.masterid = mmp.masterid limit 1) as SecondarySpecialty
from MasteredMedicalProvider mmp;

