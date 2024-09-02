from fastapi import FastAPI
import pyodbc
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (you can restrict this to specific domains)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Configure the Azure SQL Database connection
server = 'tcp:sparcpglobaltasksuitserver.database.windows.net'
database = 'SPARCPGLOBALTASKSUITDB'
username = 'globaltasksuite'
password = 'Spar@123'
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@app.get('/user')
def get_user():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()    
        cursor.execute("""
            SELECT UserID, UserName, Password
            FROM [dbo].[User]
        """)
        rows = cursor.fetchall()

        users = []
        for row in rows:
            users.append({
                "UserID": row.UserID,
                "UserName": row.UserName,
                "Password": row.Password
            })

        return users
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.get('/getTask/{task_id}')
def get_task(task_id: int):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Task WHERE TaskID = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            task = {
                'TaskID': row.TaskID,
                'TaskName': row.TaskName,
                'TaskDesc': row.TaskDesc,
                'DueDate': str(row.DueDate) if row.DueDate else None,
                'CreatedDate': str(row.CreatedDate),
                'CreatedBy': row.CreatedBy,
                'AssignedTo': row.AssignedTo,
                'Status': row.Status
            }
            return task
        else:
            return {"message": "Task not found"}

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.get('/tasks')
def get_tasks():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Task')
        rows = cursor.fetchall()

        tasks = []
        for row in rows:
            task = {
                'TaskID': row.TaskID,
                'TaskName': row.TaskName,
                'TaskDesc': row.TaskDesc,
                'DueDate': row.DueDate.isoformat() if row.DueDate else None,
                'CreatedDate': row.CreatedDate.isoformat(),
                'CreatedBy': row.CreatedBy,
                'AssignedTo': row.AssignedTo,
                'Status': row.Status
            }
            tasks.append(task)

        return tasks

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.post('/createTask')
def create_task(data: dict):
    assigned_to = data.get('AssignedTo')
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Check if the AssignedTo user exists
        cursor.execute("SELECT COUNT(1) FROM dbo.[User] WHERE UserName = ?", (assigned_to,))
        user_exists = cursor.fetchone()[0]

        if not user_exists:
            return {"error": "AssignedTo user does not exist."}

        # Insert the task if the user exists
        cursor.execute("""
            INSERT INTO dbo.Task (TaskName, TaskDesc, DueDate, CreatedDate, CreatedBy, AssignedTo, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('TaskName'),
            data.get('TaskDesc'),
            data.get('DueDate'),
            data.get('CreatedDate'),
            data.get('CreatedBy'),
            assigned_to,  # AssignedTo is a string, so use it as is
            data.get('Status')
        ))
        
        conn.commit()
        to = assigned_to
        subject = 'A Task' + data.get('TaskName') + 'has been assigned to you'
        body = 'A Task' + data.get('TaskName') + 'has been assigned to you'
        def callLogic(to, subject, body):
            pass
        return {"message": "Task created successfully."}

    except pyodbc.IntegrityError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    # Run the application without the 'reload' option
    #uvicorn.run(app, host="127.0.0.1", port=8000)
    uvicorn.run(app) 		
