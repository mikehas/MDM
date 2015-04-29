-- The Rolling Pebbles
-- CPE366-03

ALTER TABLE Specialty ADD CONSTRAINT specialty_fk FOREIGN KEY (ParentID) REFERENCES Specialty(ID);
