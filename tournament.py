# 
# tournament.py -- implementation of a Swiss-system tournament

import psycopg2
import sys


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

# define tournamentId - this is used as a global variable to
# set which tournament is being worked on
# all functions other than createTournament and
# selectTournament should check this is not set to zero
# and if not exit and return an error message
tournamentId = 0


def createTournament(tournamentName):
    #
    # checks name of tournament does not exist
    # then creates new tournament
    #
    
    # open database
    DB = connect()
    cur = DB.cursor()
    
    # get data
    SQL = "SELECT id, name from tournaments where name = %s;"
    data = (tournamentName,)
    cur.execute(SQL, data )
    count = cur.rowcount
    
    if count != 0:  # indicates tournament name already exists
        # tidy up
        cur.close
        DB.close
        
        returnStr = "ERROR - name already exists, please try again."
        return returnStr
    
    # add new name to database
    SQL = "INSERT INTO tournaments (name) VALUES(%s);"
    data =  (tournamentName,)
    cur.execute(SQL, data)
    DB.commit()
    
    # get id of added name from database
    SQL = "SELECT id from tournaments where name = %s;"
    data = (tournamentName,)
    cur.execute(SQL, data )
    tournamentId = str(cur.fetchone()[0])
    
    # tidy up
    cur.close
    DB.close
    returnStr = tournamentName + " added, id is " +  tournamentId
    return returnStr

    
def selectTournament(selectId):
    # takes an Id and returns the name of the tournament 
    # or an error if not found

    DB = connect()
    cur = DB.cursor()
    
    # get data
    SQL = "SELECT name from tournaments where id = %s;"
    data = (selectId,)
    cur.execute(SQL, data )
    row = cur.fetchall()
    # tidy up
    cur.close
    DB.close
    
    if row == []:
        returnStr = "ERROR " + str(selectId) + " not found!"
        return returnStr 
    else:
        global tournamentId
        tournamentId = selectId
        tournamentName = str(row[0][0])
        returnStr = str(selectId) + " " +  tournamentName + " selected."
        return returnStr
    
    
def deleteMatches(tournamentId=1):
    # takes an Id and delete all match with that tournamentId 
    # but not an error if no records to delete
    
    DB = connect()
    cur = DB.cursor()
    
    # delete data
    SQL = "DELETE from matches where tournament_id = %s;"
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = cur.statusmessage
    DB.commit()
    # tidy up
    cur.close
    DB.close

    return returnStr


def resetPlayersAndMatches():
    # delete all players from players table and resets
    # id to start at 1 and
    # delete all matches from matches table and resets
    # id to start at 1  
    
    DB = connect()
    cur = DB.cursor()
    
    # delete data
    SQL = "DELETE from matches where 1=1;"  # this deletes ALL records from matches
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = cur.statusmessage
    DB.commit()   
    
    # delete data
    SQL = "DELETE from players where 1=1;"  # this deletes ALL records from players
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = returnStr + ": " + cur.statusmessage
    DB.commit()
    
    # reset id key to start at 1
    SQL = "ALTER SEQUENCE players_id_seq RESTART WITH 1"  # this resets index to 1
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = returnStr + ": " + cur.statusmessage
    DB.commit()
 
    # reset id key to start at 1
    SQL = "ALTER SEQUENCE matches_id_seq RESTART WITH 1"  # this resets index to 1
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = returnStr + ": " + cur.statusmessage
    DB.commit()  
       
    # tidy up
    cur.close
    DB.close

    return returnStr


def deletePlayers(tournamentId=1):
    # takes tournamentId and deletes all records from tournament_player 
    # with that tournamentId 
    # but not an error if no records to delete
    # this does not delete the player from the players table
    
    DB = connect()
    cur = DB.cursor()
    
    # delete data
    SQL = "DELETE from tournament_player where tournament_id = %s;"
    data = (tournamentId,)
    cur.execute(SQL, data )
    returnStr = cur.statusmessage
    DB.commit()
    # tidy up
    cur.close
    DB.close
    
    resetPlayersAndMatches()

    return returnStr


def countPlayers(tournamentId=1):
    # takes tournamentId and count all players that match with that tournamentId 

    DB = connect()
    cur = DB.cursor()
 
    # get data
    SQL = "SELECT count(tournament_id) as player_count from tournament_player where tournament_id = %s;"
    data = (tournamentId,)
    cur.execute(SQL, data )
    player_count = cur.fetchone()[0]
    
    # tidy up
    cur.close
    DB.close
    
    return player_count


def  registerPlayerMatches(playerId,roundId=1, tournamentId=1):
    # Add a player that has been registered for a tournament into the matches table.
    # If there is a row in matches without a player2_id then UPDATE as player2_id
    # otherwise INSERT a new row with player_id in player1_id.

    # open database
    DB = connect()
    cur = DB.cursor()   

    #check if row with empty playerId2 for tournamentId
    SQL = "SELECT id from matches where player2_id = 0 and tournament_id = %s and round_id = %s;"
    data = (tournamentId,roundId,)
    cur.execute(SQL, data )
    count = cur.rowcount
    if count == 1:
        matchesId = cur.fetchone()[0]
        SQL = "UPDATE matches SET player2_id = %s WHERE id = %s;"
        data = (playerId, matchesId, )
        cur.execute(SQL, data )
        returnStr = cur.statusmessage
        DB.commit()
    else:
        # player2_id set to 0 for ease of recognising row with only 1 player.
        SQL = "INSERT INTO matches (tournament_id, round_id, player1_id, player2_id ) VALUES (%s, %s, %s, 0);"
        data =  (tournamentId, roundId, playerId, )
        cur.execute(SQL, data)
        returnStr = cur.statusmessage
        DB.commit()
                
    # tidy up
    cur.close
    DB.close

    return   


def registerPlayerTournament(playerId,tournamentId=1):
    """Adds an existing player to the tournament database tournament_player table.
       Also adds player_id into matches table in order as registered.
    """
     
    # open database
    DB = connect()
    cur = DB.cursor()
    
    #check if playerId exists for tournamentId
    SQL = "SELECT player_id, tournament_id from tournament_player where player_id = %s and tournament_id = %s;"
    data = (playerId,tournamentId,)
    cur.execute(SQL, data )
    count = cur.rowcount
    
    if count != 0:  # indicates player already in tournament_player
        # tidy up
        cur.close
        DB.close
        
        returnStr = "ERROR - playerId already in tournament, please try again."
        return returnStr
     
    # add new name to database
    SQL = "INSERT INTO tournament_player (player_id, tournament_id) VALUES (%s, %s);"
    data =  (playerId,tournamentId,)
    cur.execute(SQL, data)
    returnStr = cur.statusmessage
    DB.commit()
    
    # add id to matches
    roundId = 1
    registerPlayerMatches(playerId,tournamentId,roundId)
    
    # tidy up
    cur.close
    DB.close

    return returnStr


def registerPlayer(name):
    """Adds a player to the tournament database player table.
    The database assigns a unique serial id number for the player.  
    Args:
      name: the player's full name (need not be unique).
    """
    
    # open database
    DB = connect()
    cur = DB.cursor()
    
    # add new name to database
    SQL = "INSERT INTO players (name) VALUES(%s);"
    data =  (name,)
    cur.execute(SQL, data)
    DB.commit()
    
    # get id of added name from database
    SQL = "SELECT max(id) from players where name = %s;"
    data = (name,)
    cur.execute(SQL, data )
    playerId = cur.fetchone()[0]
    
    # tidy up
    cur.close
    DB.close

    registerPlayerTournament(playerId,tournamentId=1)

    return playerId


def playerStandings(tournamentId=1):
#     """Returns a list of the players and their win records, sorted by wins.
# 
#     The first entry in the list should be the player in first place, or a player
#     tied for first place if there is currently a tie.
# 
#     Returns:
#       A list of tuples, each of which contains (id, name, wins, matches):
#         id: the player's unique id (assigned by the database)
#         name: the player's full name (as registered)
#         wins: the number of matches the player has won
#         matches: the number of matches the player has played
#     """
    # check tournamentId set if not return
    
    DB = connect()
    cur = DB.cursor()
 
    # get data
    SQL = "SELECT scores.player_id, players.name, scores.scores, scores.num_matches from scores left join players on scores.player_id = players.id where scores.tournament_id = %s;"
    data = (tournamentId,)
    cur.execute(SQL, data )
    row = cur.fetchall()
     
    # tidy up
    cur.close
    DB.close
    
    return row


def reportMatch(winner, loser, tournamentId=1):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
       
    """
    
    DB = connect()
    cur = DB.cursor()
 
    # get match record id
    SQL = "SELECT id, player1_id from matches where result = 0 and (player1_id = %s or player2_id = %s) and tournament_id = %s;"
    data = (winner, winner, tournamentId,)
    cur.execute(SQL, data )
    row = cur.fetchone()
    match_id = str(row[0]) 
    player1 = int(row[1])
    
    # set data
    if player1 == winner:
        result = 1
    else:
        result = 2
    SQL = "UPDATE matches SET result = %s WHERE id = %s;"
    data = (result, match_id, )
    cur.execute(SQL, data )
    DB.commit()
    
    # tidy up
    cur.close
    DB.close
    
    return
 
 
def swissPairings(tournamentId=1):
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    DB = connect()
    cur = DB.cursor()
 
    # get data
    SQL = "SELECT scores.player_id, players.name from scores left join players on scores.player_id = players.id where scores.tournament_id = %s order by scores.scores;"
    data = (tournamentId,)
    cur.execute(SQL, data )
    row = cur.fetchall()
        
    #reformat row into expected format    
    listrow = []
    for k in range(len(row)):
        l = k + 1 
        if (l % 2) <> 0: # l is odd
            temp = row[k]
        else:
            temp = temp + row[k] 
            listrow.append(temp)    
                 
    # tidy up
    cur.close
    DB.close
  
    return listrow
    


