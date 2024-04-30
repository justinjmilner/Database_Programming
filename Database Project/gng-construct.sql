drop table Entity cascade;
CREATE TABLE Entity (
    email VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255)
);

drop table Campaigns cascade;
CREATE TABLE Campaigns (
    issue VARCHAR(255),
    location VARCHAR(255),
    start_date DATE,
    duration_days INT,
    phase VARCHAR(255),
    budget NUMERIC,
    website_push_date DATE,
    PRIMARY KEY (issue, location, start_date)
);

drop table Donations cascade;
CREATE TABLE Donations (
    entity_email VARCHAR(255),        
    campaign_issue VARCHAR(255),     
    campaign_location VARCHAR(255),  
    campaign_start_date DATE,        
    donation_date DATE,              
    amount NUMERIC,                  
    PRIMARY KEY (entity_email, campaign_issue, campaign_location, campaign_start_date, donation_date),
    FOREIGN KEY (entity_email) REFERENCES Entity(email),
    FOREIGN KEY (campaign_issue, campaign_location, campaign_start_date) REFERENCES Campaigns(issue, location, start_date) 
);

drop table Volunteer cascade;
CREATE TABLE Volunteer (
    entity_email VARCHAR(255),
    tier INT,
    FOREIGN KEY (entity_email) REFERENCES Entity(email),
    PRIMARY KEY (entity_email)
);


drop table Member cascade;
CREATE TABLE Member (
    entity_email VARCHAR(255),
    enrollment_date DATE,
    FOREIGN KEY (entity_email) REFERENCES Entity(email),
    PRIMARY KEY (entity_email)
);

drop table Employee cascade;
CREATE TABLE Employee (
    entity_email VARCHAR(255),
    salary NUMERIC,
    FOREIGN KEY (entity_email) REFERENCES Entity(email),
    PRIMARY KEY (entity_email)
);

drop table Scheduled cascade;
CREATE TABLE Scheduled (
    entity_email VARCHAR(255),
    campaign_issue VARCHAR(255),
    campaign_location VARCHAR(255),
    campaign_start_date DATE,
    scheduled_date DATE, -- The date when the entity is scheduled for the campaign
    PRIMARY KEY (entity_email, campaign_issue, campaign_location, campaign_start_date, scheduled_date),
    FOREIGN KEY (entity_email) REFERENCES Entity(email),
    FOREIGN KEY (campaign_issue, campaign_location, campaign_start_date)
      REFERENCES Campaigns(issue, location, start_date)
);

-- Insert into Entity
INSERT INTO Entity (email, name) VALUES 
('alice@example.com', 'Alice Johnson'),
('bob@example.com', 'Bob Smith'),
('carol@example.com', 'Carol Danvers'),
('dave@example.com', 'Dave Wilson'),
('duncan@example.com', 'Duncan Douglas'),
('victoria@example.com', 'City of Victoria'),
('craig@example.com', 'Craig Wright');

-- Insert into Campaigns
INSERT INTO Campaigns (issue, location, start_date, duration_days, phase, budget, website_push_date) VALUES 
('Save the Bees', 'Meadowville', '2023-04-01', 30, 'Planning', 5000, '2023-03-01'),
('Clean the Seas', 'Oceanview', '2023-05-15', 45, 'Execution', 7500, '2023-04-15'),
('Plant Trees', 'Greenfield', '2023-06-05', 60, 'Finalizing', 6000, '2023-05-20'),
('Save the Bees', 'Carolina', '2023-04-01', 25, 'Planning', 3500, '2023-02-02'),
('Save the Bees', 'Oceanview', '2023-05-15', 50, 'Executing', 2500, '2023-04-16'),
('Plant Trees', 'Greenfield', '2023-07-15', 15, 'Executing', 2000, '2023-06-06'),
('Save the Bees', 'Oceanview', '2024-05-15', 50, 'Planning', 2500, '2023-04-16'),
('Clean The Lake', 'Grapeville', '2025-07-15', 15, 'Planning', 20000, '2024-06-06');

-- Insert into Donations
INSERT INTO Donations (entity_email, campaign_issue, campaign_location, campaign_start_date, donation_date, amount) VALUES 
('alice@example.com', 'Save the Bees', 'Meadowville', '2023-04-01', '2023-04-02', 1000),
('alice@example.com', 'Save the Bees', 'Carolina', '2023-04-01', '2023-04-02', 1500),
('bob@example.com', 'Clean the Seas', 'Oceanview', '2023-05-15', '2023-05-16', 1500),
('bob@example.com', 'Save the Bees', 'Oceanview', '2023-05-15', '2023-05-16', 500),
('carol@example.com', 'Plant Trees', 'Greenfield', '2023-06-05', '2023-06-06', 200),
('victoria@example.com', 'Plant Trees', 'Greenfield', '2023-07-15', '2023-07-06', 500);

-- Insert into Volunteer
INSERT INTO Volunteer (entity_email, tier) VALUES 
('alice@example.com', 1),
('dave@example.com', 2);

-- Insert into Member
INSERT INTO Member (entity_email, enrollment_date) VALUES 
('bob@example.com', '2022-01-10'),
('carol@example.com', '2022-05-20'),
('duncan@example.com', '2020-05-20');

-- Insert into Employee
INSERT INTO Employee (entity_email, salary) VALUES 
('duncan@example.com', 40000),
('craig@example.com', 20000);

-- Insert into Scheduled
INSERT INTO Scheduled (entity_email, campaign_issue, campaign_location, campaign_start_date, scheduled_date) VALUES 
('alice@example.com', 'Save the Bees', 'Meadowville', '2023-04-01', '2023-04-05'),
('bob@example.com', 'Clean the Seas', 'Oceanview', '2023-05-15', '2023-05-20'),
('dave@example.com', 'Plant Trees', 'Greenfield', '2023-06-05', '2023-06-10');

-- List all entities who have made a donation
create view Query1 as
select e.email, e.name
from Entity e
where exists (
    select d.entity_email 
    from donations d
    where e.email = d.entity_email
);

-- List total donations from each entity
create view Query2 as
select d.entity_email, SUM(d.amount) as total_donations
from donations d
group by d.entity_email;

-- List campaigns with donations exceeding 1000$
create view Query3 as
select c.*
from Campaigns c
where c.issue in ( 
    select d.campaign_issue
    from Donations d
    group by d.campaign_issue
    having SUM(d.amount) > 1000
);

-- List entities who are both a member and employee
create view Query4 as
select entity_email from Member
intersect
select entity_email from Employee;

-- List campaigns with no donations
create view Query5 as
select * from Campaigns c
where not exists (
    select 1
    from Donations d
    where d.campaign_issue = c.issue
    and d.campaign_location = c.location
    and d.campaign_start_date = c.start_date
);

-- List of entities scheduled for a campaign from 2023-06-01 and beyond
create view Query6 as
select distinct s.entity_email 
from Scheduled s
where s.campaign_start_date >= '2023-06-01';

-- List all entities and their roles
create view Query7 as
select e.email, e.name, 'Volunteer' as role
from entity e
join volunteer v on e.email = v.entity_email
union
select e.email, e.name, 'Member' as role
from entity e
join member m on e.email = m.entity_email
union
select e.email, e.name, 'Employee' as role
from entity e
join employee p on e.email = p.entity_email;

-- Highest single donation for each campaign
create view Query8 as
select campaign_issue, MAX(amount) as highest_donation 
from donations
group by campaign_issue;

-- Campaign issues with more than 1 donation
create view Query9 as
select campaign_issue, count(*) as donation_counts
from donations 
group by campaign_issue
having count (*) > 1;

-- Total length of combined phases of campaigns
create view Query10 as
select issue, SUM(duration_days) as total_days
from campaigns
group by issue;




