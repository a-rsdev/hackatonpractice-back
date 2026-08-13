from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from config import DATABASE_PATH
from models.entities import Base, Question, Resource, Roadmap, Unit


DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)
SessionFactory = sessionmaker(bind=engine, expire_on_commit=False)


ROADMAPS = [
    {
        "id": "programming-basics",
        "title": "Programming Basics",
        "units": [
            {
                "id": "variables",
                "title": "Variables and types",
                "resources": [
                    ("https://docs.python.org/3/tutorial/introduction.html", "Python Tutorial: An Informal Introduction"),
                    ("https://docs.python.org/3/library/stdtypes.html", "Built-in Types"),
                ],
                "questions": [
                    ("Which keyword is used to declare a variable in Python?",
                     ["var", "let", "No keyword needed, just assign a value", "dim"], 2),
                    ("What is the data type of 3.14 in Python?",
                     ["int", "float", "str", "bool"], 1),
                    ("Which of these is a valid Python variable name?",
                     ["2value", "class", "my-value", "my_value"], 3),
                    ("What does the built-in type() function return?",
                     ["The type of an object", "The value of a variable", "The memory address", "The length of a string"], 0),
                ],
            },
            {
                "id": "conditions",
                "title": "Conditions",
                "resources": [
                    ("https://docs.python.org/3/tutorial/controlflow.html", "Control Flow Tools"),
                ],
                "questions": [
                    ("Which keyword starts a conditional block in Python?",
                     ["if", "when", "switch", "check"], 0),
                    ("What does 'elif' stand for?",
                     ["else list", "else if", "exit if", "end if"], 1),
                    ("Which operator checks for equality?",
                     ["===", "eq", "==", "="], 2),
                    ("What happens with `if 0:`?",
                     ["It always executes", "It never executes because 0 is falsy", "Syntax error", "It executes once"], 1),
                ],
            },
            {
                "id": "loops",
                "title": "Loops",
                "resources": [
                    ("https://docs.python.org/3/tutorial/controlflow.html#for-statements", "For Statements"),
                    ("https://docs.python.org/3/reference/compound_stmts.html#the-while-statement", "The while statement"),
                ],
                "questions": [
                    ("Which loop is used to iterate over a sequence in Python?",
                     ["do-while", "for", "repeat", "until"], 1),
                    ("What does the `break` statement do?",
                     ["Skips current iteration", "Restarts the loop", "Exits the loop entirely", "Pauses execution"], 2),
                    ("What does `continue` do inside a loop?",
                     ["Ends the loop", "Skips to the next iteration", "Restarts the program", "Does nothing"], 1),
                ],
            },
            {
                "id": "functions",
                "title": "Functions",
                "resources": [
                    ("https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "Defining Functions"),
                    ("https://docs.python.org/3/reference/compound_stmts.html#function-definitions", "Function definitions"),
                    ("https://realpython.com/defining-your-own-python-function/", "Defining Your Own Python Function"),
                ],
                "questions": [
                    ("Which keyword defines a function in Python?",
                     ["func", "def", "function", "lambda"], 1),
                    ("What is used to define an anonymous function?",
                     ["def", "anon", "lambda", "func"], 2),
                    ("What does a `return` statement do?",
                     ["Prints a value", "Ends the function and sends back a value", "Deletes the function", "Loops back to start"], 1),
                    ("Which of these correctly calls a function named greet?",
                     ["greet[]", "call greet", "greet()", "greet;"], 2),
                    ("What is a parameter in a function?",
                     ["A value returned by the function", "A variable used inside a function body", "A placeholder for input to a function", "A type of loop"], 2),
                ],
            },
            {
                "id": "collections",
                "title": "Collections",
                "resources": [
                    ("https://docs.python.org/3/tutorial/datastructures.html", "Data Structures"),
                    ("https://docs.python.org/3/library/stdtypes.html#dict", "Dictionaries"),
                ],
                "questions": [
                    ("Which data type stores key-value pairs in Python?",
                     ["list", "tuple", "dict", "set"], 2),
                    ("Which collection type is immutable?",
                     ["list", "tuple", "dict", "set"], 1),
                    ("Which method adds an item to the end of a list?",
                     ["append()", "add()", "insert()", "push()"], 0),
                    ("Which collection type does not allow duplicate values?",
                     ["list", "tuple", "dict", "set"], 3),
                ],
            },
            {
                "id": "errors",
                "title": "Error handling",
                "resources": [
                    ("https://docs.python.org/3/tutorial/errors.html", "Errors and Exceptions"),
                ],
                "questions": [
                    ("Which block is used to catch exceptions in Python?",
                     ["try/except", "catch/throw", "error/handle", "try/catch"], 0),
                    ("What does the `finally` block do?",
                     ["Runs only if an error occurs", "Runs only if no error occurs", "Always runs, regardless of an error", "Skips the rest of the code"], 2),
                    ("Which exception is raised when dividing by zero?",
                     ["ValueError", "ZeroDivisionError", "TypeError", "IndexError"], 1),
                ],
            },
        ],
    },
    {
        "id": "web-development-basics",
        "title": "Web Development Basics",
        "units": [
            {
                "id": "html",
                "title": "HTML",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/HTML", "HTML: HyperText Markup Language"),
                    ("https://developer.mozilla.org/en-US/docs/Learn/HTML", "Learn HTML"),
                ],
                "questions": [
                    ("What does HTML stand for?",
                     ["HyperText Markup Language", "HighText Machine Language", "HyperTransfer Markup Language", "HomeTool Markup Language"], 0),
                    ("Which tag is used to create a hyperlink?",
                     ["<link>", "<a>", "<href>", "<url>"], 1),
                    ("Which tag defines the largest heading?",
                     ["<h6>", "<heading>", "<h1>", "<head>"], 2),
                    ("Which attribute specifies alternate text for an image?",
                     ["alt", "src", "title", "desc"], 0),
                ],
            },
            {
                "id": "css",
                "title": "CSS",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/CSS", "CSS: Cascading Style Sheets"),
                ],
                "questions": [
                    ("What does CSS stand for?",
                     ["Cascading Style Sheets", "Creative Style System", "Computer Style Sheets", "Colorful Style Sheets"], 0),
                    ("Which property changes text color?",
                     ["font-color", "text-color", "color", "background-color"], 2),
                    ("Which selector targets an element by its class?",
                     ["#class", ".class", "*class", "@class"], 1),
                ],
            },
            {
                "id": "javascript",
                "title": "JavaScript",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/JavaScript", "JavaScript"),
                    ("https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "JavaScript Guide"),
                    ("https://javascript.info/", "The Modern JavaScript Tutorial"),
                ],
                "questions": [
                    ("Which keyword declares a constant variable in JavaScript?",
                     ["var", "let", "const", "static"], 2),
                    ("What does '===' check in JavaScript?",
                     ["Value only", "Value and type", "Type only", "Reference only"], 1),
                    ("Which method converts a string to an integer?",
                     ["parseInt()", "toInt()", "Number.string()", "str2int()"], 0),
                    ("Which of these is a valid way to write a function?",
                     ["function = myFunc() {}", "function myFunc() {}", "func myFunc() {}", "def myFunc() {}"], 1),
                    ("Which array method adds an element to the end?",
                     ["push()", "pop()", "shift()", "unshift()"], 0),
                ],
            },
            {
                "id": "dom",
                "title": "DOM",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model", "Document Object Model (DOM)"),
                    ("https://developer.mozilla.org/en-US/docs/Web/API/Document", "Document"),
                ],
                "questions": [
                    ("What does DOM stand for?",
                     ["Document Object Model", "Data Object Management", "Display Output Module", "Document Order Map"], 0),
                    ("Which method selects an element by its id?",
                     ["getElementByClass()", "getElementById()", "querySelectorId()", "selectId()"], 1),
                    ("Which event fires when a page finishes loading?",
                     ["onclick", "onchange", "load", "onready"], 2),
                    ("Which method creates a new HTML element?",
                     ["document.createElement()", "document.newElement()", "document.addElement()", "document.makeElement()"], 0),
                ],
            },
            {
                "id": "http",
                "title": "HTTP",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/HTTP", "HTTP"),
                ],
                "questions": [
                    ("What does HTTP stand for?",
                     ["HyperText Transfer Protocol", "High Transfer Text Protocol", "HyperText Transmission Process", "Home Transfer Text Protocol"], 0),
                    ("Which HTTP method is used to retrieve data?",
                     ["POST", "GET", "DELETE", "PUT"], 1),
                    ("Which status code means 'Not Found'?",
                     ["200", "301", "404", "500"], 2),
                ],
            },
            {
                "id": "apis",
                "title": "APIs",
                "resources": [
                    ("https://developer.mozilla.org/en-US/docs/Web/API", "Web APIs"),
                    ("https://developer.mozilla.org/en-US/docs/Glossary/REST", "REST"),
                ],
                "questions": [
                    ("What does API stand for?",
                     ["Application Programming Interface", "Automated Program Integration", "Application Process Interface", "Advanced Programming Instruction"], 0),
                    ("Which format is most commonly used for API responses today?",
                     ["XML", "JSON", "CSV", "YAML"], 1),
                    ("Which HTTP header specifies the format of the request body?",
                     ["Accept", "Content-Type", "Authorization", "Host"], 1),
                    ("What is a RESTful API primarily based on?",
                     ["SOAP protocol", "HTTP methods and resources", "FTP transfer", "WebSocket connections"], 1),
                ],
            },
        ],
    },
    {
        "id": "databases-basics",
        "title": "Databases Basics",
        "units": [
            {
                "id": "db-fundamentals",
                "title": "Database Fundamentals",
                "resources": [
                    ("https://en.wikipedia.org/wiki/Database", "Database (overview)"),
                    ("https://www.postgresql.org/docs/current/tutorial-concepts.html", "PostgreSQL Tutorial: Concepts"),
                ],
                "questions": [
                    ("What does DBMS stand for?",
                     ["Database Management System", "Data Backup Management Service", "Database Monitoring Service", "Data Block Management System"], 0),
                    ("Which of these is an example of a relational database?",
                     ["MongoDB", "Redis", "PostgreSQL", "Cassandra"], 2),
                    ("What is a 'schema' in a database?",
                     ["A backup of the database", "The structure that defines tables, columns, and relationships", "A query language", "A type of index"], 1),
                    ("What is the primary purpose of a database?",
                     ["To store and organize data for efficient access", "To run application code", "To render web pages", "To compile programs"], 0),
                ],
            },
            {
                "id": "sql-basics",
                "title": "SQL Basics",
                "resources": [
                    ("https://www.w3schools.com/sql/", "W3Schools SQL Tutorial"),
                    ("https://www.postgresql.org/docs/current/sql.html", "PostgreSQL: SQL Commands"),
                ],
                "questions": [
                    ("Which SQL statement is used to retrieve data from a table?",
                     ["FETCH", "SELECT", "GET", "PULL"], 1),
                    ("Which clause is used to filter rows in a SQL query?",
                     ["FILTER", "HAVING", "WHERE", "LIMIT"], 2),
                    ("Which keyword is used to sort the result set?",
                     ["SORT BY", "ORDER BY", "GROUP BY", "ARRANGE BY"], 1),
                    ("Which statement is used to add a new row to a table?",
                     ["ADD", "INSERT INTO", "CREATE", "APPEND"], 1),
                    ("Which statement removes a table entirely from a database?",
                     ["DELETE TABLE", "REMOVE TABLE", "DROP TABLE", "CLEAR TABLE"], 2),
                ],
            },
            {
                "id": "keys-relationships",
                "title": "Keys and Relationships",
                "resources": [
                    ("https://www.postgresql.org/docs/current/ddl-constraints.html", "PostgreSQL: Constraints"),
                    ("https://en.wikipedia.org/wiki/Foreign_key", "Foreign key"),
                ],
                "questions": [
                    ("What is a primary key used for?",
                     ["Uniquely identifying a row in a table", "Encrypting table data", "Sorting query results", "Storing backups"], 0),
                    ("What does a foreign key represent?",
                     ["A key from another database", "A reference to a primary key in another table", "An encrypted column", "A key that can be duplicated freely"], 1),
                    ("Which relationship type allows many rows in one table to relate to many rows in another?",
                     ["One-to-one", "One-to-many", "Many-to-many", "Zero-to-one"], 2),
                    ("What happens when a foreign key constraint is violated?",
                     ["The database ignores it", "The operation is rejected by the database", "The table is automatically dropped", "The row is duplicated"], 1),
                ],
            },
            {
                "id": "joins",
                "title": "Joins",
                "resources": [
                    ("https://www.postgresql.org/docs/current/tutorial-join.html", "PostgreSQL Tutorial: Joins"),
                    ("https://www.w3schools.com/sql/sql_join.asp", "W3Schools: SQL Joins"),
                    ("https://en.wikipedia.org/wiki/Join_(SQL)", "Join (SQL)"),
                ],
                "questions": [
                    ("Which join returns only rows that match in both tables?",
                     ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL JOIN"], 2),
                    ("Which join returns all rows from the left table, with NULLs for unmatched right rows?",
                     ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "CROSS JOIN"], 1),
                    ("What does a CROSS JOIN produce?",
                     ["The intersection of two tables", "A random sample of rows", "The Cartesian product of two tables", "Only matching rows"], 2),
                    ("Which join type combines LEFT and RIGHT joins, keeping unmatched rows from both sides?",
                     ["INNER JOIN", "FULL OUTER JOIN", "SELF JOIN", "NATURAL JOIN"], 1),
                ],
            },
            {
                "id": "indexing",
                "title": "Indexing and Performance",
                "resources": [
                    ("https://www.postgresql.org/docs/current/indexes.html", "PostgreSQL: Indexes"),
                    ("https://use-the-index-luke.com/", "Use The Index, Luke"),
                ],
                "questions": [
                    ("What is the main purpose of a database index?",
                     ["To enforce foreign keys", "To speed up data retrieval", "To store backups", "To encrypt sensitive columns"], 1),
                    ("What is a potential downside of adding too many indexes?",
                     ["Slower SELECT queries only", "Slower writes (INSERT/UPDATE/DELETE) and more storage use", "Loss of data integrity", "Indexes have no downsides"], 1),
                    ("Which command is commonly used to analyze a query's execution plan in PostgreSQL?",
                     ["ANALYZE PLAN", "EXPLAIN", "DESCRIBE", "SHOW PLAN"], 1),
                    ("What is a composite index?",
                     ["An index on a single column", "An index built on multiple columns together", "An index that is automatically deleted", "A backup index"], 1),
                ],
            },
            {
                "id": "transactions",
                "title": "Transactions",
                "resources": [
                    ("https://www.postgresql.org/docs/current/tutorial-transactions.html", "PostgreSQL Tutorial: Transactions"),
                    ("https://en.wikipedia.org/wiki/ACID", "ACID"),
                ],
                "questions": [
                    ("What does the 'A' in ACID stand for?",
                     ["Availability", "Atomicity", "Aggregation", "Authentication"], 1),
                    ("Which SQL command permanently saves the changes made in a transaction?",
                     ["SAVE", "COMMIT", "FINALIZE", "APPLY"], 1),
                    ("Which SQL command undoes changes made in the current transaction?",
                     ["UNDO", "REVERT", "ROLLBACK", "CANCEL"], 2),
                    ("What does the 'Isolation' property in ACID ensure?",
                     ["Transactions never fail", "Concurrent transactions don't interfere with each other's intermediate state", "Data is always backed up", "Transactions run faster"], 1),
                ],
            },
        ],
    },
]


def initialize_database() -> None:
    Base.metadata.create_all(engine)
    with SessionFactory.begin() as session:
        if session.scalar(select(Roadmap.id).limit(1)) is not None:
            return

        for roadmap_data in ROADMAPS:
            roadmap = Roadmap(id=roadmap_data["id"], title=roadmap_data["title"])
            session.add(roadmap)

            for order, unit_data in enumerate(roadmap_data["units"], 1):
                unit_id = unit_data["id"]
                session.add(Unit(
                    id=unit_id, roadmap_id=roadmap.id,
                    title=unit_data["title"], order=order,
                ))

                for res_index, (url, res_title) in enumerate(unit_data["resources"], 1):
                    session.add(Resource(
                        id=f"res-{unit_id}-{res_index}", unit_id=unit_id,
                        url=url, title=res_title,
                    ))

                for q_index, (text, options, correct_index) in enumerate(unit_data["questions"], 1):
                    session.add(Question(
                        id=f"q-{unit_id}-{q_index}", unit_id=unit_id,
                        text=text, options=options, correct_option_index=correct_index,
                    ))