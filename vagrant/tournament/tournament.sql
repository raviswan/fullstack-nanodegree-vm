-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE tournamentdb;
DROP TABLE Players,Matches CASCADE;
DROP VIEW IF EXISTS WinList;
DROP VIEW IF EXISTS OrderedWinList;
DROP VIEW IF EXISTS OddList;
DROP VIEW IF EXISTS EvenList;
DROP VIEW IF EXISTS OddTable;
DROP VIEW IF EXISTS EvenTable;
DROP VIEW IF EXISTS sPairs;

CREATE DATABASE tournamentdb;
\c tournamentdb;

--'Players' table will be used to store the Players name, wins, loses,games
CREATE TABLE Players(
	name text,
	wins int,
	losses int,
	games int,
	p_id SERIAL PRIMARY KEY
);

--'Matches' table will be used to store the id of winner and loser. The draw
-- field used to indicate a tie is not presently used.
CREATE TABLE Matches(
	m_id SERIAL PRIMARY KEY,
	winner int REFERENCES Players(p_id),
	loser int REFERENCES Players(p_id),
	draw boolean
);

--To get the Swiss pairings , the players list is sorted in descending order
-- of matches won, and given a serial no starting with 1 in OrderedWinList.
-- All the odd numbered rows are placed in OddList which is then given a row 
--number in OddTable.Likewise, for even rows. To form swiss pair, Odd and
-- Even Tables are combined based on their row numbers. 
CREATE VIEW winList  as SELECT p_id,name,wins as winCount from players 
group by players.p_id order by winCount  desc;

CREATE VIEW OrderedWinList as SELECT row_number() over (order by winCount desc)
as row_id,p_id,name,winCount from winList;

CREATE VIEW OddList AS SELECT * from OrderedWinList WHERE mod(row_id,2)=1;

CREATE VIEW EvenList AS SELECT * from OrderedWinList WHERE mod(row_id,2)=0;

CREATE VIEW OddTable as select row_number() over (order by winCount desc) as 
o_no,p_id,name,winCount from OddList;

CREATE VIEW EvenTable as select row_number() over (order by winCount desc) as 
e_no,p_id,name,winCount from EvenList;

CREATE VIEW sPairs AS SELECT OddTable.p_id as o_id,OddTable.name as o_name,
EvenTable.p_id as e_id,EvenTable.name as e_name from OddTable full outer join
EvenTable ON OddTable.o_no = EvenTable.e_no;


