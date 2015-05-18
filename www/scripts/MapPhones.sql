-- Nicole Martin
-- nlmartin@calpoly.edu
-- 2015-05-17

-- This SQL file will populate the Phones table using the data in the 
-- already-populated MedicalProvider and RawData tables.
-- It does not check that Phones already has data in it.
-- It will only populate phone numbers in the following normal formats:
--    (805) 555-5555
--    805-555-5555
--    805.555.5555
--    8055555555' 


-- My test code, populates MedicalProvider
-- INSERT INTO MedicalProvider(SourceID)
-- SELECT SourceID FROM RawData;

-- Grab all the SourceIDs that were mapped to MedicalProvider
INSERT INTO Phones (SourceID)
SELECT SourceID FROM MedicalProvider;

-- Update all the Phones with '(805) 555-5555' format
Update Phones, RawData
Set Area = SUBSTRING(Phone,2,3), 
Exchange = SUBSTRING(Phone,7,3),
Subscriber = SUBSTRING(Phone,11,4)
WHERE Phones.SourceID = RawData.SourceID
AND Phone REGEXP '^(.{3})+(\.{3}[-].{4})$';

-- Update all the Phones with 805-555-5555 format
Update Phones, RawData
Set Area = SUBSTRING(Phone,1,3), 
Exchange = SUBSTRING(Phone,5,3),
Subscriber = SUBSTRING(Phone,9,4)
WHERE Phones.SourceID = RawData.SourceID
AND Phone REGEXP '^(\.{3}[-]\.{3}[-].{4})$';

-- Update all the Phones with 805.555.5555 format
Update Phones, RawData
Set Area = SUBSTRING(Phone,1,3), 
Exchange = SUBSTRING(Phone,5,3),
Subscriber = SUBSTRING(Phone,9,4)
WHERE Phones.SourceID = RawData.SourceID
AND Phone REGEXP '^(\.{3}[.]\.{3}[.].{4})$';

-- Update all the Phones with 8055555555 format
Update Phones, RawData
Set Area = SUBSTRING(Phone,1,3), 
Exchange = SUBSTRING(Phone,4,3),
Subscriber = SUBSTRING(Phone,7,4)
WHERE Phones.SourceID = RawData.SourceID
AND Phone REGEXP '^[[:digit:]]{10}$';

