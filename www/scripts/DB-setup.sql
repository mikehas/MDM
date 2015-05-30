-- The Rolling Pebbles
-- CPE366-03

create table Specialty (
	ParentID int,
	ID int primary key,
	Title varchar(128),
	Code char(10),
	Description varchar(128),
   CONSTRAINT unique_code UNIQUE (Code) 
);

create table RawData (
	SourceID int primary key,
	ProviderType varchar(20) NOT NULL,
	Name varchar(64) NOT NULL,
	Gender char(1),
	DateOfBirth varchar(32),
	isSoleProprietor char(1),
	MailingStreet varchar(64),
	MailingUnit varchar(64),
	MailingCity varchar(64),
	MailingRegion varchar(16),
	MailingPostCode varchar(16),
	MailingCounty varchar(32),
	MailingCountry varchar(16),
	PracticeStreet varchar(64),
	PracticeUnit varchar(64),
	PracticeCity varchar(64),
	PracticeRegion varchar(16),
	PracticePostCode varchar(16),
	PracticeCounty varchar(32),
	PracticeCountry varchar(16),
	Phone varchar(32),
	PrimarySpecialty char(10),
	SecondarySpecialty char(10)
);

create table MedicalProvider (
	SourceID int primary key,
	ProviderType varchar(20) NOT NULL,
	Name varchar(64) NOT NULL,
	Gender char(1),
	DateOfBirth varchar(32),
	isSoleProprietor char(1),
	PrimarySpecialty char(10),
	SecondarySpecialty char(10),
	Timestamp datetime,
	Message varchar(128),
	Constraint MP_RD FOREIGN KEY (SourceID) REFERENCES RawData(SourceID),
	Constraint MP_SPP FOREIGN KEY (PrimarySpecialty) REFERENCES Specialty(Code),
	Constraint MP_SPS FOREIGN KEY (SecondarySpecialty) REFERENCES Specialty(Code)
);

create table Address (
	SourceID int,
	AddressType varchar(16),
	Country varchar(16),
	Region varchar(16),
	County varchar(32),
	City varchar(64),
	PostalCode varchar(16),
   Street varchar(64),
	Unit varchar(64),
	Primary key (SourceID, AddressType),
	Constraint A_MP FOREIGN KEY (SourceID) REFERENCES MedicalProvider(SourceID)
);

create table Phones (
	SourceID int primary key,
	Country varchar(6),
	Area varchar(6),
	Exchange varchar(6),
	Subscriber varchar(6),
	Ext varchar(6),
   CleanPhone varchar(12),
	Constraint P_MP foreign key (SourceID) references MedicalProvider(SourceID)
);

create table MasteredMedicalProvider (
	MasterID int primary key auto_increment,
	ProviderType varchar(20) NOT NULL,
	Name varchar(64) NOT NULL,
	Gender char(1),
	DateOfBirth varchar(32),
	isSoleProprietor char(1)
);

create table Matched (
	SourceID int,
	MasterID int,
	Timestamp datetime,
	MatchRule varchar(32),
	Message varchar(128),
	Primary key (SourceID, MasterID),
	Constraint M_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint M_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID)
);

create table MatchedPhone (
	MasterID int,
	SourceID int,
	Primary key (SourceID, MasterID),
	Constraint MPH_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MPH_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID)
);

create table MatchedMailingAddress (
	MasterID int,
	SourceID int,
	AddressType varchar(16),
	Primary key (MasterID, SourceID, AddressType),
	Constraint MMA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MMA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
);

create table MatchedPracticeAddress (
	MasterID int,
	SourceID int,
	AddressType varchar(16),
	Primary key (MasterID, SourceID, AddressType),
	Constraint MPA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MPA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
);

create table MatchedPrimarySpecialties (
	MasterID int,
	Specialty char(10),
	Primary key(MasterID, Specialty),
	Constraint MPS_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID),
	Constraint MPS_S foreign key (Specialty) references Specialty(Code)
);

create table MatchedSecondarySpecialties (
	MasterID int,
	Specialty char(10),
	Primary key(MasterID, Specialty),
	Constraint MSS_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID),
	Constraint MSS_S foreign key (Specialty) references Specialty(Code)
);

