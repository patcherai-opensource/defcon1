from app import app

import pymssql

def _conn(database=app.config["DB_DATABASE"]):
    return pymssql.connect(
        server=f"{app.config["DB_SERVER"]}:{app.config["DB_PORT"]}",
        user=app.config["DB_USER"],
        password=app.config["DB_PASSWORD"],
        database=database,
        as_dict=True,
    )

def init_db():
    create_db_cmd = """
    IF DB_ID('birdarchive') IS NULL
    BEGIN
        CREATE DATABASE birdarchive;
    END;
    """
    with _conn(database=None) as conn:
        with conn.cursor() as cur:
            cur.execute(create_db_cmd)
        conn.commit()
    
    create_images_table_cmd = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'images')
    BEGIN
        CREATE TABLE images (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            url           NVARCHAR(2048)  NOT NULL,
            filename      NVARCHAR(512)   NOT NULL,
            type          NVARCHAR(128)   NULL,
            width         INT             NULL,
            height        INT             NULL,
            size          BIGINT          NULL,
            time          DATETIME2       NOT NULL DEFAULT SYSUTCDATETIME(),
            is_hidden     BIT             NOT NULL DEFAULT 0
        );
    END;
    """
    
    create_flags_table_cmd = """
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'flags')
    BEGIN
        CREATE TABLE flags (
            id            INT IDENTITY(1,1) PRIMARY KEY,
            flag          NVARCHAR(2048)  NOT NULL,
            is_hidden     BIT             NOT NULL DEFAULT 0
        );
    END;
    """
    tables = [create_images_table_cmd, create_flags_table_cmd]
    for t in tables:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(t)
            conn.commit()
    insert_flag()
            
def insert_flag():
    sql_cmd = """
    INSERT INTO flags
        (flag, is_hidden)
    VALUES
        (%s, %s);
    SELECT SCOPE_IDENTITY() AS id;
    """
    
    with _conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                sql_cmd, (
                    app.config["FLAG"],
                    1
                ))
            row = cursor.fetchone()
        conn.commit()
    return row

def insert_image(url, filename, meta:dict):
    sql_cmd = """
    INSERT INTO images 
        (url, filename, type, width, height, size)
    VALUES
        (%s, %s, %s, %s, %s, %s);
    SELECT SCOPE_IDENTITY() AS id;
    """
    
    print(sql_cmd % (url, filename, meta.get("format", ""), meta.get("width", 0), meta.get("height", 0), meta.get("file_size", 0)))

    with _conn() as conn:
        with conn.cursor() as cursor:
            
            cursor.execute(
                sql_cmd, (
                    url,
                    filename,
                    meta.get("format", ""),
                    meta.get("width", 0),
                    meta.get("height", 0),
                    meta.get("file_size", 0),
                ))
            row = cursor.fetchone()
        conn.commit()
    return row

def get_images():
    sql_cmd = """
        SELECT * FROM images WHERE is_hidden = 0 ORDER BY time DESC;
    """
    with _conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_cmd)
            return cursor.fetchall()

def get_flags():
    sql_cmd = """
        SELECT flag from flags WHERE is_hidden = 0;
    """
    with _conn() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql_cmd)
            return cursor.fetchall()