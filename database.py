import json
import os
from datetime import datetime, timedelta

import mysql.connector
from xid import Xid

# Initialize MySQL connection
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    port="3306",
    user=os.getenv("DB_USER"),
    password=os.getenv('DB_PASSWORD'),
    database="wevo"
)

cursor = db.cursor()


def get_user_info_from_slack(slack_user_id, get_relations=False):
    query = """
        SELECT Users.ID, Users.Name
        FROM SlackUsers
        JOIN Users ON SlackUsers.UserID = Users.ID
        WHERE SlackUsers.ID = %s
    """
    cursor.execute(query, (slack_user_id,))
    result = cursor.fetchone()

    if result:
        user_id, user_name = result[0], result[1]
        relations_info = None
        if get_relations:
            relations_info = get_user_relations(user_id)
        return user_id, user_name, relations_info

    else:
        return None, None, []


def get_user_info(user_id, get_relations=False):
    query = """
        SELECT Users.ID, Users.Name
        FROM Users
        WHERE Users.ID = %s
    """
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if result:
        user_id, user_name = result[0], result[1]
        relations_info = None
        if get_relations:
            relations_info = get_user_relations(user_id)
        return user_id, user_name, relations_info

    else:
        return None, None, []


def get_user_relations(user_id):
    relations_query = """
        (SELECT UserRelations.UserID2 as UserID, Users.Name, UserRelations.Relationship
        FROM UserRelations
        JOIN Users ON UserRelations.UserID2 = Users.ID
        WHERE UserRelations.UserID1 = %s)
        UNION ALL
        (SELECT UserRelations.UserID1 as UserID, Users.Name, UserRelations.Relationship
        FROM UserRelations
        JOIN Users ON UserRelations.UserID1 = Users.ID
        WHERE UserRelations.UserID2 = %s)
    """
    cursor.execute(relations_query, (user_id, user_id))
    relations = cursor.fetchall()

    relations_info = []
    for relation in relations:
        target_user_id, target_user_name, relationship = relation
        relations_info.append({"UserID": target_user_id, "UserName": target_user_name, "Relationship": relationship})

    return relations_info


def insert_user(user_id, name, company_id):
    query = "INSERT INTO Users (ID, Name, CompanyID) VALUES (%s, %s, %s)"
    values = (user_id, name, company_id)
    try:
        cursor.execute(query, values)
        db.commit()
        print(f"User {name} added successfully.")
    except mysql.connector.Error as error:
        print("Failed to insert data into MySQL table {}".format(error))


def assume_user(slack_id, user_id):
    query = """
        INSERT INTO SlackUsers (ID, UserID)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE UserID = %s
    """
    values = (slack_id, user_id, user_id)
    try:
        cursor.execute(query, values)
        db.commit()
        print(f"SlackID {slack_id} associated with UserID {user_id} successfully.")
    except mysql.connector.Error as error:
        print("Failed to insert/update data in MySQL table {}".format(error))


def insert_feedback(user_id, feedback_data):
    gen_id = "fbc" + Xid().string()
    query = "INSERT INTO Feedback (ID, UserID, Timestamp, Data) VALUES (%s, %s, %s, %s)"
    values = (gen_id, user_id, datetime.now(), json.dumps(feedback_data))
    try:
        cursor.execute(query, values)
        db.commit()
        print(f"Feedback added successfully.")
        return gen_id
    except mysql.connector.Error as error:
        print("Failed to insert data into MySQL table {}".format(error))


def get_feedback(user_id):
    date_threshold = datetime.now() - timedelta(days=2)

    query = """
        SELECT ID, UserID, TargetUserID, Timestamp, Data, IsCalculated FROM Feedback
        WHERE UserID = %s AND Timestamp >= %s AND IsCalculated = FALSE
        ORDER BY Timestamp DESC
        LIMIT 1
    """

    values = (user_id, date_threshold)

    try:
        cursor.execute(query, values)
        feedback_row = cursor.fetchone()

        if feedback_row:
            feedback = {
                'ID': feedback_row[0],
                'UserID': feedback_row[1],
                'TargetUserID': feedback_row[2],
                'Timestamp': feedback_row[3],
                'Data': json.loads(feedback_row[4]),
                'IsCalculated': feedback_row[5]
            }
            print(f"Feedback found: {feedback}")
            return feedback
        else:
            print("No recent uncalculated feedback found for this user.")
            return None
    except mysql.connector.Error as error:
        print("Failed to fetch data from MySQL table {}".format(error))


def mark_feedback_as_calculated(feedback_id):
    query = """
        UPDATE Feedback
        SET IsCalculated = TRUE
        WHERE ID = %s
    """

    values = (feedback_id,)

    try:
        cursor.execute(query, values)
        db.commit()
        print(f"Feedback ID {feedback_id} has been marked as calculated.")
    except mysql.connector.Error as error:
        print("Failed to update data in MySQL table: {}".format(error))


def get_uncalculated_feedbacks(user_id):
    date_threshold = datetime.now() - timedelta(days=2)

    query = """
        SELECT ID, UserID, TargetUserID, Timestamp, Data, IsCalculated FROM Feedback
        WHERE UserID = %s AND Timestamp >= %s AND IsCalculated = FALSE
        ORDER BY Timestamp DESC
    """

    values = (user_id, date_threshold)

    try:
        cursor.execute(query, values)
        feedback_rows = cursor.fetchall()

        if feedback_rows:
            feedbacks = []
            for row in feedback_rows:
                feedback = {
                    'ID': row[0],
                    'UserID': row[1],
                    'TargetUserID': row[2],
                    'Timestamp': row[3],
                    'Data': json.loads(row[4]),
                    'IsCalculated': row[5]
                }
                feedbacks.append(feedback)

            print(f"Feedbacks found: {feedbacks}")
            return feedbacks
        else:
            print("No recent uncalculated feedbacks found for this user.")
            return None
    except mysql.connector.Error as error:
        print("Failed to fetch data from MySQL table {}".format(error))


def update_feedback_data(user_id, new_feedback_data):
    # First get the feedback we want to update
    feedback = get_feedback(user_id)

    # If no feedback was found, return None
    if feedback is None:
        print("No feedback found for this user.")
        return

    # If a feedback was found, update its text
    query = """
        UPDATE Feedback
        SET Data = %s
        WHERE ID = %s
    """

    values = (json.dumps(new_feedback_data), feedback["ID"])

    try:
        cursor.execute(query, values)
        db.commit()  # Don't forget to commit the changes
        print(f"Feedback ID {feedback['ID']} has been updated.")
        return feedback["ID"]
    except mysql.connector.Error as error:
        print(f"Failed to update feedback in MySQL table: {error}")


def insert_evaluation(user_id, feedback_id, evaluation):
    query = """
        INSERT INTO Evaluation (
            ID,
            FeedbackID,
            EvaluationTargetType,
            TargetUserName,
            TargetUserID,
            UserID,
            Timestamp,
            Company_Fulfillment,
            Company_FulfillmentWeight,
            Company_Autonomy,
            Company_AutonomyWeight,
            Company_GrowthOpportunities,
            Company_GrowthOpportunitiesWeight,
            Company_Workload,
            Company_WorkloadWeight,
            Company_Stress,
            Company_StressWeight,
            Company_WorkLifeBalance,
            Company_WorkLifeBalanceWeight,
            Person_Recognition,
            Person_RecognitionWeight,
            Person_Sympathy,
            Person_SympathyWeight,
            Person_Trust,
            Person_TrustWeight,
            Person_ProSupport,
            Person_ProSupportWeight,
            Person_GrowthSupport,
            Person_GrowthSupportWeight,
            SentimentData
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
    """

    values = (
        Xid().string(),
        feedback_id,
        evaluation.get('EvaluationTargetType', None),
        evaluation.get('SubjectName', ""),
        evaluation.get('SubjectUserID', ""),
        user_id,
        datetime.now(),
        evaluation.get('Company_Fulfillment', 0),
        evaluation.get('Company_FulfillmentWeight', 0),
        evaluation.get('Company_Autonomy', 0),
        evaluation.get('Company_AutonomyWeight', 0),
        evaluation.get('Company_GrowthOpportunities', 0),
        evaluation.get('Company_GrowthOpportunitiesWeight', 0),
        evaluation.get('Company_Workload', 0),
        evaluation.get('Company_WorkloadWeight', 0),
        evaluation.get('Company_Stress', 0),
        evaluation.get('Company_StressWeight', 0),
        evaluation.get('Company_WorkLifeBalance', 0),
        evaluation.get('Company_WorkLifeBalanceWeight', 0),
        evaluation.get('Person_Recognition', 0),
        evaluation.get('Person_RecognitionWeight', 0),
        evaluation.get('Person_Sympathy', 0),
        evaluation.get('Person_SympathyWeight', 0),
        evaluation.get('Person_Trust', 0),
        evaluation.get('Person_TrustWeight', 0),
        evaluation.get('Person_ProSupport', 0),
        evaluation.get('Person_ProSupportWeight', 0),
        evaluation.get('Person_GrowthSupport', 0),
        evaluation.get('Person_GrowthSupportWeight', 0),
        json.dumps(evaluation.get('SentimentData', []))
    )

    try:
        cursor.execute(query, values)
        db.commit()
    except mysql.connector.Error as error:
        print(f"Failed to insert evaluation into MySQL table: {error}")


def get_evaluation_from_feedback_id(feedback_id):
    query = """
        SELECT
            ID,
            FeedbackID,
            EvaluationTargetType,
            TargetUserName,
            TargetUserID,
            UserID,
            Timestamp,
            Company_Fulfillment,
            Company_FulfillmentWeight,
            Company_Autonomy,
            Company_AutonomyWeight,
            Company_GrowthOpportunities,
            Company_GrowthOpportunitiesWeight,
            Company_Workload,
            Company_WorkloadWeight,
            Company_Stress,
            Company_StressWeight,
            Company_WorkLifeBalance,
            Company_WorkLifeBalanceWeight,
            Person_Recognition,
            Person_RecognitionWeight,
            Person_Sympathy,
            Person_SympathyWeight,
            Person_Trust,
            Person_TrustWeight,
            Person_ProSupport,
            Person_ProSupportWeight,
            Person_GrowthSupport,
            Person_GrowthSupportWeight,
            SentimentData
        FROM Evaluation
        WHERE FeedbackID = %s
    """

    values = (feedback_id,)

    try:
        cursor.execute(query, values)
        evaluation_row = cursor.fetchall()

        if evaluation_row:
            evaluations = []
            for row in evaluation_row:
                evaluation = {
                    'ID': row[0],
                    'FeedbackID': row[1],
                    'EvaluationTargetType': row[2],
                    'TargetUserName': row[3],
                    'TargetUserID': row[4],
                    'UserID': row[5],
                    'Timestamp': row[6],
                    'Company_Fulfillment': row[7],
                    'Company_FulfillmentWeight': row[8],
                    'Company_Autonomy': row[9],
                    'Company_AutonomyWeight': row[10],
                    'Company_GrowthOpportunities': row[11],
                    'Company_GrowthOpportunitiesWeight': row[12],
                    'Company_Workload': row[13],
                    'Company_WorkloadWeight': row[14],
                    'Company_Stress': row[15],
                    'Company_StressWeight': row[16],
                    'Company_WorkLifeBalance': row[17],
                    'Company_WorkLifeBalanceWeight': row[18],
                    'Person_Recognition': row[19],
                    'Person_RecognitionWeight': row[20],
                    'Person_Sympathy': row[21],
                    'Person_SympathyWeight': row[22],
                    'Person_Trust': row[23],
                    'Person_TrustWeight': row[24],
                    'Person_ProSupport': row[25],
                    'Person_ProSupportWeight': row[26],
                    'Person_GrowthSupport': row[27],
                    'Person_GrowthSupportWeight': row[28],
                    'SentimentData': json.loads(row[29]),
                }
                evaluations.append(evaluation)
            return evaluations
        else:
            print("No evaluation found for this feedback ID.")
            return None
    except mysql.connector.Error as error:
        print(f"Failed to fetch evaluation from MySQL table: {error}")


def get_evaluations_from_target_user_id_or_target_type(target_user_id=None, target_type=None):
    query = """
        SELECT
            ID,
            FeedbackID,
            EvaluationTargetType,
            TargetUserName,
            TargetUserID,
            UserID,
            Timestamp,
            Company_Fulfillment,
            Company_FulfillmentWeight,
            Company_Autonomy,
            Company_AutonomyWeight,
            Company_GrowthOpportunities,
            Company_GrowthOpportunitiesWeight,
            Company_Workload,
            Company_WorkloadWeight,
            Company_Stress,
            Company_StressWeight,
            Company_WorkLifeBalance,
            Company_WorkLifeBalanceWeight,
            Person_Recognition,
            Person_RecognitionWeight,
            Person_Sympathy,
            Person_SympathyWeight,
            Person_Trust,
            Person_TrustWeight,
            Person_ProSupport,
            Person_ProSupportWeight,
            Person_GrowthSupport,
            Person_GrowthSupportWeight,
            SentimentData
        FROM Evaluation
    """

    if target_user_id is not None:
        query += " WHERE TargetUserID = %s"
        values = (target_user_id,)
    elif target_type is not None:
        query += " WHERE EvaluationTargetType = %s"
        values = (target_type,)
    else:
        return None

    try:
        cursor.execute(query, values)
        rows = cursor.fetchall()
        evaluations = []

        for row in rows:
            evaluation = {
                'ID': row[0],
                'FeedbackID': row[1],
                'EvaluationTargetType': row[2],
                'TargetUserName': row[3],
                'TargetUserID': row[4],
                'UserID': row[5],
                'Timestamp': row[6],
                'Company_Fulfillment': row[7],
                'Company_FulfillmentWeight': row[8],
                'Company_Autonomy': row[9],
                'Company_AutonomyWeight': row[10],
                'Company_GrowthOpportunities': row[11],
                'Company_GrowthOpportunitiesWeight': row[12],
                'Company_Workload': row[13],
                'Company_WorkloadWeight': row[14],
                'Company_Stress': row[15],
                'Company_StressWeight': row[16],
                'Company_WorkLifeBalance': row[17],
                'Company_WorkLifeBalanceWeight': row[18],
                'Person_Recognition': row[19],
                'Person_RecognitionWeight': row[20],
                'Person_Sympathy': row[21],
                'Person_SympathyWeight': row[22],
                'Person_Trust': row[23],
                'Person_TrustWeight': row[24],
                'Person_ProSupport': row[25],
                'Person_ProSupportWeight': row[26],
                'Person_GrowthSupport': row[27],
                'Person_GrowthSupportWeight': row[28],
                'SentimentData': json.loads(row[29]),
            }
            evaluations.append(evaluation)

        return evaluations
    except mysql.connector.Error as error:
        print(f"Failed to fetch evaluations from MySQL table: {error}")


def register_relation(user_id1, user_id2, relationship):
    new_id = str(Xid())

    query = """
        INSERT INTO UserRelations (ID, UserID1, UserID2, Relationship)
        VALUES (%s, %s, %s, %s)
    """

    values = (new_id, user_id1, user_id2, relationship)

    try:
        cursor.execute(query, values)
        db.commit()
        print(f"New relation '{relationship}' between users '{user_id1}' and '{user_id2}' has been added with ID: {new_id}")
    except mysql.connector.Error as error:
        print(f"Failed to insert into MySQL table. Error: {error}")
