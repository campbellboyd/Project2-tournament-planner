-- SQL to create the database, tbles and views for the full-stack web developer
-- Intro to Relational Databases Final Project
-- This should be run as \i tournament.sql from the psql command line from the folder containing the tournament files
--
-- The project was written to include more than one tournament. It was subsequently discovered that
-- udacity did not have a mechanism for testing extra credit features.
-- The project was adapated to pass the basic version tests,  but without the extra features being completely removed.


CREATE DATABASE tournament;

-- The table tournaments contains the name of each tournament.

CREATE TABLE tournaments (
    id serial PRIMARY KEY,
    name text NOT NULL
);

-- For the tests to be passed, there has to be an entry in the tournaments table
INSERT INTO tournaments (name) VALUES ('Leonard Nimoy Memorial');

-- Ther table matches contains a record of each match set up or played. If a match has not been played, result is 0.
CREATE TABLE matches (
    id serial PRIMARY KEY,
    tournament_id integer NOT NULL,
    round_id integer NOT NULL,
    player1_id integer NOT NULL,
    player2_id integer,
    result integer DEFAULT 0
);

-- This table contains a record for each player entered into a tournament.
CREATE TABLE tournament_player (
    player_id integer,
    tournament_id integer
);

-- This table contains a record for each player registered to play in any tournament.
CREATE TABLE players (
    id serial PRIMARY KEY,
    name text NOT NULL
);


-- add two column index to prevent double entries -i.e. same player in same tournament more than once

CREATE UNIQUE INDEX tournament_id_player_id ON tournament_player USING btree (player_id, tournament_id);

-- add foreign keys to ensure data integrity, e.g. you can't delete a player fomr plasyers if they have entries in matches
ALTER TABLE ONLY matches
    ADD CONSTRAINT fk_player1_id FOREIGN KEY (player1_id) REFERENCES players(id);

ALTER TABLE ONLY matches
    ADD CONSTRAINT fk_tournament_id FOREIGN KEY (tournament_id) REFERENCES tournaments(id);


ALTER TABLE ONLY tournament_player
    ADD CONSTRAINT tournament_player_player_id_fkey FOREIGN KEY (player_id) REFERENCES players(id);

ALTER TABLE ONLY tournament_player
    ADD CONSTRAINT tournament_player_tournament_id_fkey FOREIGN KEY (tournament_id) REFERENCES tournaments(id);


-- The views produce the data used in the function playerStandings
--                     scores
--                     ^  ^ ^
--                _____|  | |_________
--                |       |           | 
--    scores_player1      |           matches_sum  
--                 scores_player2     ^         ^     
--                                    |         |               
--                        matches_player1    matches_player2
--
--  I'm sure there is a more elegant solution but this does work.
 
CREATE VIEW matches_player1 AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    (COALESCE(count(matches.result), (0)::bigint) * 1) AS num_matches
   FROM (tournament_player
     LEFT JOIN matches ON (((tournament_player.player_id = matches.player1_id) AND (tournament_player.tournament_id = matches.tournament_id))))
  WHERE (matches.result > 0)
  GROUP BY tournament_player.tournament_id, tournament_player.player_id
  ORDER BY tournament_player.tournament_id, tournament_player.player_id;

CREATE VIEW matches_player2 AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    COALESCE(count(matches.result), (0)::bigint) AS num_matches
   FROM (tournament_player
     LEFT JOIN matches ON (((tournament_player.player_id = matches.player2_id) AND (tournament_player.tournament_id = matches.tournament_id))))
  WHERE (matches.result > 0)
  GROUP BY tournament_player.tournament_id, tournament_player.player_id
  ORDER BY tournament_player.tournament_id, tournament_player.player_id;

CREATE VIEW matches_sum AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    (COALESCE(sum(matches_player1.num_matches), (0)::numeric) + COALESCE(sum(matches_player2.num_matches), (0)::numeric)) AS num_matches
   FROM ((tournament_player
     LEFT JOIN matches_player1 ON (((tournament_player.player_id = matches_player1.player_id) AND (tournament_player.tournament_id = matches_player1.tournament_id))))
     LEFT JOIN matches_player2 ON (((tournament_player.player_id = matches_player2.player_id) AND (tournament_player.tournament_id = matches_player2.tournament_id))))
  GROUP BY tournament_player.tournament_id, tournament_player.player_id;

CREATE VIEW scores_player1 AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    COALESCE(sum(matches.result), (0)::bigint) AS points
   FROM (tournament_player
     LEFT JOIN matches ON (((tournament_player.player_id = matches.player1_id) AND (tournament_player.tournament_id = matches.tournament_id))))
  GROUP BY tournament_player.tournament_id, tournament_player.player_id
  ORDER BY tournament_player.tournament_id, tournament_player.player_id;

CREATE VIEW scores_player2 AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    COALESCE((sum(matches.result) / 2), (0)::bigint) AS points
   FROM (tournament_player
     LEFT JOIN matches ON (((tournament_player.player_id = matches.player2_id) AND (tournament_player.tournament_id = matches.tournament_id))))
  GROUP BY tournament_player.tournament_id, tournament_player.player_id
  ORDER BY tournament_player.tournament_id, tournament_player.player_id;

CREATE VIEW scores AS
 SELECT tournament_player.tournament_id,
    tournament_player.player_id,
    ((sum(scores_player1.points) + sum(scores_player2.points)) + (0)::numeric) AS scores,
    sum(matches_sum.num_matches) AS num_matches
   FROM (((tournament_player
     LEFT JOIN scores_player1 ON ((tournament_player.player_id = scores_player1.player_id)))
     LEFT JOIN scores_player2 ON ((tournament_player.player_id = scores_player2.player_id)))
     LEFT JOIN matches_sum ON ((tournament_player.player_id = matches_sum.player_id)))
  GROUP BY tournament_player.tournament_id, tournament_player.player_id
  ORDER BY tournament_player.tournament_id, ((sum(scores_player1.points) + sum(scores_player2.points)) + (0)::numeric) DESC;

-- end









