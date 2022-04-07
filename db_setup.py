import sqlite3
import os

def setup_db(db_path):
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(''' CREATE TABLE IF NOT EXISTS accounts (address TEXT PRIMARY KEY, matrix_handle TEXT) ''')
    con.commit()
    con.close()

def setup_test(path="society_overrides_test.db"):
    # Nuke the old test db
    setup_db(path)
    # Add some test data
    con = sqlite3.connect(path)
    cur = con.cursor()
    # Add override for nonmember account (no address set)
    cur.execute(''' INSERT OR REPLACE INTO accounts (address, matrix_handle) VALUES (?, ?) ''', ("D6CuPyACRzF5a7vkRX4UF9Vhw1TBneEo81jUmuhBYvCZ27Y", "@testuser1:matrix.org"))
    cur.execute(''' INSERT OR REPLACE INTO accounts (address, matrix_handle) VALUES (?, ?) ''', ("HL8bEp8YicBdrUmJocCAWVLKUaR2dd1y6jnD934pbre3un1", "@testuser2:matrix.org"))
    con.commit();
    con.close()

def setup_main(path="society_overrides.db"):
    setup_db(path)

if __name__ == '__main__':
    setup_main()
