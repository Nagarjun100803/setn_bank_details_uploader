import psycopg2 as pg
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, RealDictRow, execute_values 
from typing import Any
from config import settings


# Connection parameters.
connection_params: dict[str, Any] = {
    # 'database': 'souglobal',
    'database': 'setn',
    'password': 'arju@123',
    'user': 'postgres', 
    'cursor_factory': RealDictCursor   
}

connection_params_: dict = {
    'database': settings.db_name,
    'password': settings.db_password,
    'user': settings.db_username, 
    'cursor_factory': RealDictCursor,
    'host': settings.db_host,
    'port': settings.db_port

}

# Create a database pool to create and store the connections.
db: SimpleConnectionPool = SimpleConnectionPool(
    minconn = 4, maxconn = 12, **connection_params_
)



def execute_sql_select_statement(
        sql: str, vars: dict | list | None = None,
        fetch_all: bool = True
) -> list[RealDictRow] | RealDictRow | None:
    
    # Get a connection from the pool. 
    conn: pg.extensions.connection = db.getconn()
    # Get a cursor object.
    cur: pg.extensions.cursor = conn.cursor()
    cur.execute(sql, vars = vars) # Execute the select statement.

    if fetch_all: 
        result: list[RealDictRow] | None = cur.fetchall() # Fetch all records.
    else:
        result: RealDictRow | None = cur.fetchone() # Fetch single record. 
    
    db.putconn(conn) # Release the connection back to the pool. 
    cur.close()

    return result




def execute_sql_commands(
        sql: str, vars: list | dict | None = None,  
        fetch: bool = False
) -> (RealDictRow | None):
    
    # Get the database connection. 
    conn: pg.extensions.connection = db.getconn()
    # Get the cursor object.
    cur = conn.cursor()
    # Execute the sql command/statemnt.
    cur.execute(sql, vars)
    # Commit the changes.
    conn.commit()
    # Release the connection back to the pool.
    db.putconn(conn)
    # if fetch = True, Need to fetch the record from the cursor.
    record = None
    if fetch:
        record: RealDictRow = cur.fetchone()
    cur.close()
    return record


# database_table: str = """
        
#         create table if not exists beneficiaries(
            
#             full_name varchar not null,
#             aadhar_num varchar(12) not null,
#             status varchar(20) default 'demo',
#             email_id varchar(100) not null unique,
#             phone_num varchar,
#             college_name varchar not null,
#             application_num integer,
#             semester integer,
#             course varchar
#         );


#         create table if not exists bank_details(
            
#             email_id varchar references beneficiaries(email_id) not null, 
#             account_holder varchar(30) not null,
#             name_as_in_passbook varchar not null,
#             account_number varchar not null,
#             ifsc_code varchar not null,
#             bank_name varchar not null,
#             branch varchar not null, 
#             linked_phone_num varchar not null,
#             upi_id varchar,
#             upi_num varchar(12) not null,
#             fee_per_sem integer not null,
#             created_at timestamp not null default now()
#         );

# """

database_table: str = """
    CREATE TABLE IF NOT EXISTS student_bank_details (
        id SERIAL PRIMARY KEY, 
        email_id VARCHAR(255) NOT NULL,
        mobile_number VARCHAR(15) NOT NULL,
        aadhaar_number CHAR(12) NOT NULL,
        full_name TEXT NOT NULL,
        account_holder VARCHAR NOT NULL,
        account_holder_name TEXT NOT NULL,
        account_number VARCHAR(50) NOT NULL,
        ifsc_code CHAR(11) NOT NULL,
        bank_name TEXT NOT NULL,
        bank_branch_address TEXT NOT NULL,
        bank_mobile_number VARCHAR(15) NOT NULL,
        upi_number VARCHAR(15),
        semester_fee NUMERIC(10, 2),
        passbook_scan BYTEA NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
);

"""
def initiate_database_tables(tables_list: str):
    conn =  db.getconn()
    cur = conn.cursor()
    cur.execute(tables_list)
    conn.commit()
    print("All Tables Created")
    cur.close()
    db.putconn(conn)

initiate_database_tables(database_table)

