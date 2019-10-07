import sqlite3
conn = sqlite3.connect('acts.db')
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()


# Create table

c.execute("drop table if exists acts")
c.execute("drop table if exists categories")

c.execute("create table if not exists categories(category varchar(100) primary key)")
c.execute("create table if not exists acts(actId int primary key, category varchar(100) not null, timestamp timestamp, caption varchar(255), upvotes int default 0, imgB64 mediumtext, username varchar(100), foreign key(category) references categories(category) ON DELETE CASCADE)")
c.execute("CREATE TABLE IF NOT EXISTS categories(name varchar(100) primary key, count int default 0)");



# c.execute("INSERT INTO categories VALUES('People')")
# c.execute("INSERT INTO categories VALUES('Society')")
# c.execute("INSERT INTO categories VALUES('Animals')")
# c.execute("INSERT INTO categories VALUES('Environment')")

#Can't execute this coz chi is not in users table

#c.execute("INSERT INTO acts VALUES (12345,'People',CURRENT_TIMESTAMP,'Munna, jhund me to suar aate hai',12000,'jaimatadijaimatadijaimatadi','chi')")



# Save (commit) the changes

conn.commit()

# We can also close the connection if we are done with it.

# Just be sure any changes have been committed or they will be lost.

conn.close()



conn = sqlite3.connect('acts.db')

c = conn.cursor()


c.execute("SELECT * FROM acts")

l=c.fetchall()

for i in l:

    print(i)

