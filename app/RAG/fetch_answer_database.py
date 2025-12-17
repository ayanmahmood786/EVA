from fuzzywuzzy import fuzz
from RAG.rag_history import create_connection
import oracledb

def find_similarity(given_name):
    names_list=fetch_unique_questions()
    matches = []
    for name in names_list:
        similarity_score = fuzz.ratio(given_name, name)
        if similarity_score>=90:
            matches.append((name, similarity_score))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

def fetch_unique_questions():
    # Define the Oracle connection parameters
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT DISTINCT question FROM rag_history"
    cursor.execute(query)
    unique_questions = cursor.fetchall()
    questions_list = [row[0] for row in unique_questions]
    return questions_list


def fetch_answer_for_question(question):
    conn = create_connection()
    cursor = conn.cursor()

    # Define the SQL query with a placeholder for the question
    query = "SELECT answer FROM rag_history WHERE question = :question"

    # Execute the query with the question parameter
    cursor.execute(query, {"question": question})

    # Fetch the result
    result = cursor.fetchone()

    if result:
        return result


def fetch_frequent(session_id,module):
    query = f"""
        WITH ranked_questions AS (
            SELECT
                session_id,
                question,
                COUNT(question) AS frequency,
                RANK() OVER (PARTITION BY session_id ORDER BY COUNT(question) DESC) AS rank
            FROM
                rag_history_{module}
            WHERE
                session_id = :session_id
            GROUP BY
                session_id, question
        ),
        random_answers AS (
            SELECT
                session_id,
                question,
                answer,
                ROW_NUMBER() OVER (PARTITION BY session_id, question ORDER BY DBMS_RANDOM.VALUE) AS rn
            FROM
                rag_history_{module}
            WHERE
                session_id = :session_id
        )
        SELECT
            rq.session_id,
            rq.question,
            ra.answer,
            rq.frequency
        FROM
            ranked_questions rq
        JOIN
            random_answers ra
        ON
            rq.session_id = ra.session_id AND rq.question = ra.question
        WHERE
            rq.rank <= 3 AND ra.rn = 1
        ORDER BY
            rq.rank, rq.frequency DESC
    """
    try:
        conn = create_connection()
        cursor = conn.cursor()
        print("Connection Established")

        cursor.execute(query, session_id=session_id)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        print("Query executed successfully",result)
        if result:
            return result
    except oracledb.DatabaseError as e:
        error, = e.args
        print(f"Error fetching frequent questions: {error.message}")
        return None