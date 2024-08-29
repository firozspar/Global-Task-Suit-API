from flask import Flask, jsonify, request
import pyodbc

app = Flask(__name__)

# Configure the Azure SQL Database connection
server = 'tcp:sparcpglobaltasksuitserver.database.windows.net'
database = 'SPARCPGLOBALTASKSUITDB'
username = 'globaltasksuite'
password = 'Spar@123'
driver = '{ODBC Driver 17 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@app.route('/user', methods=['GET'])
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

        return jsonify(users)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.route('/getTask/<int:task_id>', methods=['GET'])
def get_task(task_id):
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
            return jsonify(task)
        else:
            return jsonify({"message": "Task not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.route('/tasks', methods=['GET'])
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

        return jsonify(tasks)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

@app.route('/createTask', methods=['POST'])
def create_task():
    data = request.json
    assigned_to = data.get('AssignedTo')
    
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Check if the AssignedTo user exists
        cursor.execute("SELECT COUNT(1) FROM dbo.[User] WHERE UserName = ?", (assigned_to,))
        user_exists = cursor.fetchone()[0]

        if not user_exists:
            return jsonify({"error": "AssignedTo user does not exist."}), 400

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
        return jsonify({"message": "Task created successfully."}), 201

    except pyodbc.IntegrityError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
