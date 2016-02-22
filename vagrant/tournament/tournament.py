#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
#from psycopg2.extensions import AsIs

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournamentdb")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect();
    c = conn.cursor();
    c.execute("DELETE FROM matches");
    conn.commit();
    c.close();
    conn.close();


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect();
    c = conn.cursor();
    c.execute("DELETE FROM players");
    c.execute("SELECT count(*) from players");
    conn.commit();
    c.close();
    conn.close();


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect();
    c = conn.cursor();
    c.execute("SELECT count(*) from players")
    result =  c.fetchone()
    conn.commit();
    c.close();
    conn.close();
    return result[0]

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect();
    c = conn.cursor();
    c.execute("INSERT INTO Players VALUES(%s,0,0,0,DEFAULT);",(name,));
    conn.commit();
    c.close();
    conn.close();
    


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor();
    c.execute("SELECT  p_id,name,wins,games from players \
        order by wins desc");
    wList = c.fetchall()
    print wList
    conn.commit();
    c.close();
    conn.close();
    return wList;


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect();
    c = conn.cursor();
    c.execute("INSERT INTO matches VALUES(DEFAULT, %s,%s,false);",(winner,loser,));
    c.execute("UPDATE players SET wins=wins+1, games=games+1 WHERE \
        players.p_id=(%s)",(winner,))
    c.execute("UPDATE players SET losses=losses+1, games=games+1 WHERE \
        players.p_id=(%s)",(loser,))
    conn.commit();
    c.close();
    conn.close();
 
 
def swissPairings():
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
    conn = connect();
    c = conn.cursor();
    c.execute("SELECT * from sPairs");
    swissPairs = c.fetchall();
    conn.commit()
    c.close()
    conn.close()
    return swissPairs;
