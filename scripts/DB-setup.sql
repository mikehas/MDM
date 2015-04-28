-- The Rolling Pebbles
-- CPE366-03

create table Specialty (
	ParentID int,
	ID int primary key,
	Title varchar(64),
	Code varchar(10),
	Description varchar(255),
	constraint specialty_fk foreign key (ParentID) references Specialty(ID),
   constraint unique_code unique (Code) 
);

create table RawData (
	SourceID int primary key auto_increment,
	ProviderType varchar(20) not null,
	Name varchar(255) not null,
	Gender char(1),
	DateOfBirth varchar(255),
	isSoleProprietor char(1),
	MailAddress varchar(255),
	PracticeAddress varchar(255),
	Phone varchar(255),
	Speciality varchar(255)
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
	Constraint MA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
);

create table MatchedPracticeAddress (
	MasterID int,
	SourceID int,
	AddressType varchar(10),
	Primary key (MasterID, SourceID, AddressType),
	Constraint MA_MP foreign key (SourceID) references MedicalProvider(SourceID),
	Constraint MA_MMP foreign key (SourceID, AddressType) references Address(SourceID, AddressType)
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

