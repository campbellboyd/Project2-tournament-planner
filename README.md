# Project2-tournament-planner
Project 2 for Udacity Full Stack Web Developer Course

This repo contains the three files for running the Project:

tournament.py - the source code for the engine
tournament_test.py  - supplied test code
tournament.sql - sql to set up tournament database - this also describes the data structure adopted

To set up the database (taken from tournaments.sql):
1.	change to the folder/sub-directory containing the tournament files
2.	psql
3. (at psql prompt)	\i tournament.sql	(creates database)
4. (at psql prompt)	\q			(quits psql)
5. python tournament_test.py  (runs the tests)

The project was written to include more than one tournament for extra credit. It was subsequently discovered that
udacity did not have a mechanism for testing extra credit features. The project was adapted to pass the basic version tests,  but without the extra features being completely removed.

Note that tournament.py is a module of what would be an application and does not include user I/O. Running tournament.py directly does nothing.



