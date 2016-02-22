__ PROJECT 2- TOURNAMENT RESULTS __

The following files were modified for this project
*tournament.sql
*tournament.py

__DESCRIPTION__

1. _tournament.sql_ - defines the  PSQL database  "tournamentdb" to store details
	of players and record the outcome of the matches played in a tournament.
2. _tournament.py_ - a python script to query the above database to  add/delete
	players, record outcome of matches played and to form pairings in the form
	of a swiss pair for a given round of a tournament.


__SOFTWARE NEEDED__

The project was run on Vagrant Virtual box provided by Udacity. The following
software were used
*Python 2.7.6
*PostgreSQL 9.3.10

__HOW TO RUN__

* Fire up vagrant/virtual box on your machine as follows:
	* vagrant up
	* vagrant ssh
 
* Goto tournament folder 
	* cd /vagrant/tournament
* Run the following to set up the database,tables and views
	*psql -f tournament.sql
* To test the code, run the  python test script that's provided by Udacity
	* python tournament_test.py

All 8 tests have to pass to see SUCCESS!!



