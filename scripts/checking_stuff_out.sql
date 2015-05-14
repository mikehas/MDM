select * from rawdata. 
select * from specialty;
select * from rawdata r where r.MailingStreet like "%200 Medical%";
select r.sourceid, r.mailingstreet, r.mailingunit, r.mailingcity, r.mailingregion, r.mailingpostcode from rawdata r;
select * from rawdata r where r.name like "%&%";
select * from rawdata r where r.name like "%'%";
select * from rawdata r where r.name like "%(%";
select * from rawdata r where r.name like "%)%";
select * from rawdata r where r.name like "%,%";
select * from rawdata r where r.name like "%/%"; -- COTA /L, MS CCC/SLP, MA CCC SLP/L
select * from rawdata r where r.name like "%OTR%"; -- OTR-L, OTR L, OTRL, OTR, LOTR
select * from rawdata r where r.name like "%-%";
select * from rawdata r where r.name like "%PAC%";
select * from rawdata r where r.name like "%.%"; -- make PH.D. M.D consistent e.g., (PHD, MD)
select * from rawdata r where r.name like "%MD%"; -- make PH.D. M.D consistent
select * from rawdata r where r.name like "%.%";
select * from rawdata r where r.name like "%;%"; -- remove ;
select * from rawdata r where r.name like "%>%"; -- remove >
select * from rawdata r where r.name like "%`%"; -- convert ` to '
select * from rawdata r where r.name like "%D.o.o%"; -- Look for inconsistencies
select * from rawdata r where r.name like "%B.v.%"; 
select * from rawdata r where r.name like "%endom%"; -- appears to be a middle name 
select * from rawdata r where r.name like "%dup%"; -- appears to be a middle name 
select * from rawdata r where r.name like "%arar%"; -- appears to be a last name
select * from rawdata r where r.name like "%rph%";  
select * from rawdata r where r.name like "% PHARM %"; -- PHARM D, PHARM
select * from rawdata r where r.name like "%NGIAN%"; -- PHARM D, PHARM
select * from rawdata r where r.name like "%914%"; -- phone number in name
select * from rawdata r where r.name like "%2ND%"; -- 2nd location or address, not name
select * from rawdata r where r.name like "%AJO%"; -- Name
select * from rawdata r where r.name like "%ANU %"; -- firstname
select * from rawdata r where r.name like "%BED%"; -- firstname
select * from rawdata r where r.name like "%COM %"; -- name
select * from rawdata r where r.name like "%DAH %"; -- name
select * from rawdata r where r.name like "%DIV %"; -- name
select * from rawdata r where r.name like "%DOV %"; -- name
select * from rawdata r where r.name like "%EDS %"; -- TITLE

select * from rawdata r where r.name like "%EYA%"; -- name
select * from rawdata r where r.name like "%FAC%"; -- title

select * from rawdata r where r.name like "%FAD %"; -- name
select * from rawdata r where r.name like "%FAI %"; -- name
select * from rawdata r where r.name like "%FEN %"; -- name

select * from rawdata r where r.name like "%FRO %"; -- name
select * from rawdata r where r.name like "%GEH %"; -- name
select * from rawdata r where r.name like "% HIA%"; -- name
select * from rawdata r where r.name like "%HIS%"; -- title
select * from rawdata r where r.name like "%HOJ%"; -- name
select * from rawdata r where r.name like "%IYA%"; -- name
select * from rawdata r where r.name like "%J-J%"; -- name
select * from rawdata r where r.name like "%JAD%"; -- name
select * from rawdata r where r.name like "% JEF %"; -- name
select * from rawdata r where r.name like "% JER %"; -- name
select * from rawdata r where r.name like "%JOL %"; -- name
select * from rawdata r where r.name like "%JOS %"; -- name
select * from rawdata r where r.name like "%JR. %"; -- name
select * from rawdata r where r.name like "%KOJ%"; -- name
select * from rawdata r where r.name like "%MR %"; -- name interesting case
select * from rawdata r where r.name like "%KYO%"; -- name
select * from rawdata r where r.name like "%LHI%"; -- name
select * from rawdata r where r.name like "%LIC %"; -- title
select * from rawdata r where r.name like "%LUT %"; -- middle name
select * from rawdata r where r.name like "%MHA %"; -- title
select * from rawdata r where r.name like "%MOT %"; -- title
select * from rawdata r where r.name like "%NHA %"; -- middle name
select * from rawdata r where r.name like "%NHI %"; -- middle name
select * from rawdata r where r.name like "% NYI%"; -- name
select * from rawdata r where r.name like "% OZO%"; -- name
select * from rawdata r where r.name like "% PAC %"; -- title
select * from rawdata r where r.name like "%RUY%"; -- name
select * from rawdata r where r.name like "%SEW%"; -- name
select * from rawdata r where r.name like "%STA"; -- title
select * from rawdata r where r.name like "% STE %"; -- name
select * from rawdata r where r.name like "TEM%"; -- title
select * from rawdata r where r.name like "% USA %"; -- title
select * from rawdata r where r.name like "% WUI %"; -- name
select * from rawdata r where r.name like "% xay %"; -- name
select * from rawdata r where r.name like "% YUL %"; -- name
select * from rawdata r where r.name like "% zax%"; -- name
select * from rawdata r where r.name like "% zef%"; -- name
select * from rawdata r where r.name like "%zoi%"; -- name
select * from rawdata r where r.name like "%zvi%"; -- name
select * from rawdata r where r.name like "%ABOM%"; -- title
select * from rawdata r where r.name like "% ABRA %"; -- name





