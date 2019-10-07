import sqlite3
conn = sqlite3.connect('users.db')
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()


# Create table
c.execute("drop table if exists users")

c.execute("create table if not exists users(username varchar(100) primary key, password varchar(40) not null)")

#c.execute("INSERT INTO users VALUES('chitti','3d725109c7e7c0bfb9d709836735b56d943d263f')")
#c.execute("INSERT INTO users VALUES('rasya', '3d725109c7e7c0bfb9d709836735b56d943d263f')")
#c.execute("INSERT INTO users VALUES('jkprerana','3d725109c7e7c0bfb9d709836735b56d943d263f')")
#c.execute("INSERT INTO users VALUES('pragnya','3d725109c7e7c0bfb9d709836735b56d943d263f')")

# Save (commit) the changes

conn.commit()

# We can also close the connection if we are done with it.

# Just be sure any changes have been committed or they will be lost.

conn.close()



conn = sqlite3.connect('users.db')

c = conn.cursor()

c.execute("SELECT * FROM users")

l=c.fetchall()

for i in l:

    print(i)
