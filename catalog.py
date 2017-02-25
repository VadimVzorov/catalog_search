import logging
import argparse
import psycopg2

logging.basicConfig(filename="catalog_log.log", level=logging.DEBUG)
logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="catalog")
logging.debug("Connection to PostgreSQL established")

def put(name, id, description, hide, show):
    """Stores catalog item"""
    logging.info("Storing catalog item with name:{!r}; id:{!r}; description:{!r}".format(name, id, description))

    cursor = connection.cursor()
    try:
        command = "insert into catalog values (%s, %s, %s, %s)"
        cursor.execute(command, (name, id, description, hide))
    except psycopg2.IntegrityError:
        connection.rollback()
        logging.info("Storing item was not successful, trying to update existing item")
        if show:
            command = "update catalog set id=%s, description=%s, hidden=%s where name=%s"
            cursor.execute(command, (id, description, show, name))
        else:
            command = "update catalog set id=%s, description=%s, hidden=%s where name=%s"
            cursor.execute(command, (id, description, hide, name))

    connection.commit()

    logging.info("Catalog item is now stored")
    return name, id, description

def get(name):
    """Gets information about a certain item in the table"""
    logging.info("Getting item with the name:{!r}".format(name))
    cursor = connection.cursor()
    command = "select * from catalog where name={!r} and hidden='FALSE'"
    searchQuery = name
    cursor.execute(command.format(searchQuery))
    # print(row)
    # print(row[0])
    row = cursor.fetchall()
    logging.info("Item %s is retrived from catalog".format(name))
    return row

def search(name):
    """Searches for items with certain name"""
    logging.info("Getting item with the name:{!r}".format(name))
    cursor = connection.cursor()
    command = "select * from catalog where name like '%{}%' and hidden='FALSE'"
    # searchQuery = '%'+name+'%'
    cursor.execute(command.format(name))
    # print(row)
    # print(row[0])
    row = cursor.fetchall()
    if row == []:
        print("There are no items with this name")
    logging.info("Item %s is retrived from catalog".format(name))
    return row

def main():
    """Main function"""
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store catalog items and get catalog items")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    logging.info("Constructing 'put' subparser")
    put_parser = subparsers.add_parser("put", help="Store item in the catalog")
    put_parser.add_argument("name", help="name of the item")
    put_parser.add_argument("id", help="id of the item")
    put_parser.add_argument("description", help="description of the item")
    put_parser.add_argument("--hide",action="store_true", help="hides the item")
    put_parser.add_argument("--show",action="store_true", help="shows the item")

    logging.info("Constructing 'get' subparser")
    get_parser = subparsers.add_parser("get", help="Retrive item with certain name")
    get_parser.add_argument("name", help="name of the item")

    logging.info("Constructing 'search' subparser")
    search_parser = subparsers.add_parser("search", help="Search for item using string")
    search_parser.add_argument("name", help="name of the item")

    arguments = parser.parse_args()
    arguments = vars(arguments)

    #FIXME:Why i might need it?
    command = arguments.pop("command") #FIXME how this works?
    #removes and returns the last item in the list.
    if command == "put":
        name, id, description = put(**arguments)
        print("Stored {!r} information in the table".format(name))
        cursor = connection.cursor()
        cursor.execute("select name, description from catalog")
        print(cursor)
        table = cursor.fetchall()
        print(table)
    elif command == "get":
        name = get(**arguments)
        print("Retrived item: {!r}".format(name))
    elif command == "search":
        name = search(**arguments)
        print(name)

if __name__ == "__main__":
    main()
