import oracledb
# import oracledb
import api


def create_connection():
    try:
        conn = oracledb.connect("ebizai/ebizai@localhost:1575/orcl")
        api.logger.info("Connection Establised Succesfully")
        return conn
    except oracledb.Error as e:
        api.logger.error(f"Error connecting to database: {e}")
        return None

def history(module,question,session_id,answer,token,time,user_id,date):
    try:
        connection = create_connection()
        cursor = connection.cursor()
        insert_query = f"""
        INSERT INTO rag_history_{module} (question, session_id, tokens, time_in_secs,user_id,conversation_date,answer)
        VALUES (:question, :session_id, :tokens, :time_in_secs,:user_id,:conversation_date,:answer)
        """
        data = {
            "question": question,
            "session_id": session_id,
            "answer": answer,
            "tokens": token,
            "time_in_secs": time,
            "user_id":user_id,
            "conversation_date":date
        }
        try:
            cursor.execute(insert_query, data)
            connection.commit()
            api.logger.info(f"Data Inserted Succesfully:{data}")
        except oracledb.DatabaseError as e:
            error, = e.args
            print("Error code:", error.code)
            print("Error message:", error.message)
        finally:
            # Close the cursor and connection
            cursor.close()
            connection.close()
    except Exception as e:
        return f"Error While Storing History:{e}"

