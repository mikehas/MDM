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
	SourceID int primary key auto_increment,
        ProviderID varchar(255),
	ProviderType varchar(255) not null,
	Name varchar(255) not null,
	Gender char(255),
	DateOfBirth varchar(255),
	isSoleProprietor char(255),
	MailingStreet varchar(255),
	MailingUnit varchar(255),
	MailingCity varchar(255),
	MailingRegion varchar(255),
	MailingPostCode varchar(255),
	MailingCounty varchar(255),
	MailingCountry varchar(255),
	PracticeStreet varchar(255),
	PracticeUnit varchar(255),
	PracticeCity varchar(255),
	PracticeRegion varchar(255),
	PracticePostCode varchar(255),
	PracticeCounty varchar(255),
	PracticeCountry varchar(255),
	Phone varchar(255),
	PrimarySpecialty varchar(255),
	SecondarySpecialty varchar(255)
);

create table MedicalProvider (
	SourceID int primary key,
	ProviderType varchar(20) not null,
	Name varchar(255) not null,
	Gender char(1),
	DateOfBirth varchar(255),
	isSoleProprietor char(1),
	PrimarySpeciality varchar(10),
	SecondarySpeciality varchar(10),
	Timestamp datetime,
	Message varchar(255),
	Constraint MP_RD foreign key (SourceID) references RawData(SourceID),
	Constraint MP_SPP foreign key (PrimarySpeciality) references Specialty(Code),
	Constraint MP_SPS foreign key (SecondarySpeciality) references Specialty(Code)
);

create table Address (
	SourceID int,
	AddressType varchar(10),
	Country varchar(255),
	Region varchar(255),
	County varchar(255),
	City varchar(255),
	PostalCode varchar(255),
	Unit varchar(255),
	Primary key (SourceID, AddressType),
	Constraint A_MP foreign key (SourceID) references MedicalProvider(SourceID)
);

create table Phones (
	SourceID int primary key,
	Country varchar(6),
	Area varchar(6),
	Exchange varchar(6),
	Subscriber varchar(6),
	Ext varchar(6),
	Constraint P_MP foreign key (SourceID) references MedicalProvider(SourceID)
);

create table MasteredMedicalProvider (
	MasterID int primary key auto_increment,
	ProviderType varchar(20) not null,
	Name varchar(255) not null,
	Gender char(1),
	DateOfBirth varchar(255),
	isSoleProprietor char(1)
);

create table Matched (
	SourceID int,
	MasterID int,
	Timestamp datetime,
	MatchRule varchar(255),
	Message varchar(255),
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
	AddressType varchar(10),
	Primary key (MasterID, SourceID, AddressType),
	Constraint MMA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MMA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
);

create table MatchedPracticeAddress (
	MasterID int,
	SourceID int,
	AddressType varchar(10),
	Primary key (MasterID, SourceID, AddressType),
	Constraint MPA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MPA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
);

create table MatchedPrimarySpecialities (
	MasterID int,
	Speciality varchar(10),
	Primary key(MasterID, Speciality),
	Constraint MPS_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID),
	Constraint MPS_S foreign key (Speciality) references Specialty(Code)
);

create table MatchedSecondarySpecialities (
	MasterID int,
	Speciality varchar(10),
	Primary key(MasterID, Speciality),
	Constraint MSS_MMP foreign key (MasterID) references MasteredMedicalProvider(MasterID),
	Constraint MSS_S foreign key (Speciality) references Specialty(Code)
);

