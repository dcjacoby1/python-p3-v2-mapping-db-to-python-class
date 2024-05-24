from __init__ import CURSOR, CONN


class Department:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, name, location, id=None):
        self.id = id
        self.name = name
        self.location = location

    def __repr__(self):
        return f"<Department {self.id}: {self.name}, {self.location}>"

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Department instances """
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY,
            name TEXT,
            location TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Department instances """
        sql = """
            DROP TABLE IF EXISTS departments;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ Insert a new row with the name and location values of the current Department instance.
        Update object id attribute using the primary key value of new row.
        """
        sql = """
            INSERT INTO departments (name, location)
            VALUES (?, ?)
        """

        CURSOR.execute(sql, (self.name, self.location))
        CONN.commit()

        #once the row is inserted into the DB, this line retrieves the primary key id
        #adds primary key id to self.id
        self.id = CURSOR.lastrowid
        #type(self) returns class of current instance - Department
        #allows us to keep track of all insatances that have been saved to DB using the ...
        #id as the key and the values are object (self)
        #example retrieval: department = Department.all[1]
        #output example: <Department 1: Human Resources, New York>
        type(self).all[self.id] = self

    @classmethod
    def create(cls, name, location):
        """ Initialize a new Department instance and save the object to the database """
        department = cls(name, location)
        department.save()
        return department

    def update(self):
        """Update the table row corresponding to the current Department instance."""
        sql = """
            UPDATE departments
            SET name = ?, location = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.location, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Department instance,
        delete the dictionary entry, and reassign id attribute"""


        sql = """
            DELETE FROM departments
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # Delete the dictionary entry using id as the key
        del type(self).all[self.id]

        # Set the id to None
        self.id = None
    
    
    #checks if the all object has a matching primary key id to the one from DB
    # if it does, it updates the .name and .location to match DB entry
    #if not, creates a new object based on DB entry 

    #example query: row = CURSOR.execute("select * from departments").fetchone() , where fetchone grabs one entry
    #row is now equal to: (1, 'Payroll', 'Building A, 5th Floor')
    #department = Department.instance_from_db(row)
    #now department object in all = <Department 1: Payroll, Building A, 5th Floor>
    #essentially pulls from DB and places in all {}

    @classmethod
    def instance_from_db(cls, row):
        """Return a Department object having the attribute values from the table row."""

        # Check the dictionary for an existing instance using the row's primary key
        department = cls.all.get(row[0])
        if department:
            # ensure attributes match row values in case local object was modified
            department.name = row[1]
            department.location = row[2]
        else:
            # not in dictionary, create new instance and add to dictionary
            department = cls(row[1], row[2])
            department.id = row[0]
            cls.all[department.id] = department
        return department
    
    #returns a list of every row in table, read sql = to understand

    #example query: departments = Department.get_all()
    #[<Department 1: Payroll, Building A, 5th Floor>, <Department 2: Human Resources, Building C, East Wing>, <Department 3: Accounting, Building B, 1st Floor>]
    # now we can interact with departments: departments[0] => <Department 1: Payroll, Building A, 5th Floor>
    @classmethod
    def get_all(cls):
        """Return a list containing a Department object per row in the table"""
        sql = """
            SELECT *
            FROM departments
        """

        rows = CURSOR.execute(sql).fetchall()

        return [cls.instance_from_db(row) for row in rows]
    
    
    #same as get_all() , but only retrieves the specific id

    #example query: department = Department.find_by_id(1)
    #department is <Department 1: Payroll, Building A, 5th Floor>

    @classmethod
    def find_by_id(cls, id):
        """Return a Department object corresponding to the table row matching the specified primary key"""
        sql = """
            SELECT *
            FROM departments
            WHERE id = ?
        """

        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
    
    #same as find_by_id() but for name
    @classmethod
    def find_by_name(cls, name):
        """Return a Department object corresponding to first table row matching specified name"""
        sql = """
            SELECT *
            FROM departments
            WHERE name is ?
        """

        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.instance_from_db(row) if row else None

