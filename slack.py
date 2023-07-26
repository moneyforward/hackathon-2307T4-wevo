import json
import os
import threading

import tornado
# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from xid import Xid
from database import get_user_info_from_slack, insert_user, assume_user, get_user_info, get_evaluation_from_feedback_id, \
    register_relation
from service import initiate_feedback, continue_feedback, evaluate_feedback, evaluation_for_user_id, \
    evaluation_for_company

# Initializes your app with your bot token and signing secret
app = App(
    token=os.getenv('SLACK_TOKEN'),
    signing_secret=os.getenv('SLACK_SECRET')
)

CMD_CREATE_USER = "!create-user"
CMD_WHO_AM_I = "!who-am-i"
CMD_ASSUME_USER = "!assume-user"
CMD_MANUAL_START = "!manual-start"
CMD_MANUAL_CALCULATE = "!manual-evaluate"
CMD_GET_CURRENT_FEEDBACK_ID = "!get-current-feedback-id"
CMD_GET_EVALUATION = "!get-evaluation"
CMD_SET_RELATION = "!set-relation"
CMD_HELP = "!help"

MANUAL = """```
1. !create-user
This command allows you to create a new user. You can use it by simply typing `!create-user your_user_name`. The server will generate a unique user ID and associate it with the given user name.

2. !who-am-i
This command gives you information about your user. When you send `!who-am-i`, it will return your user ID, name, and all your relations.

3. !assume-user
This command lets you assume the identity of a user you've previously created. Use `!assume-user your_user_id`. The server will associate your Slack account with the ID of the user you've entered.

4. !set-relation
This command enables you to register a relationship between two users. Use `!set-relation user_id relation_type`. The server will establish a relation of 'relation_type' between 'current_user' and 'user_id'.

5. !manual-start
The `!manual-start` command starts a feedback session. The feedback session allows you to give feedback for other users you're related to. Before using this command, make sure you've created and assumed a user.

6. !manual-evaluate
This command calculates evaluations based on the feedback provided. Use `!manual-evaluate` to execute the evaluation.

7. !get-current-feedback-id
NOT YET IMPLEMENTED

8. !get-evaluation
The `!get-evaluation` command allows you to retrieve evaluations. You can use it in four ways:
- `!get-evaluation company` to get an evaluation of the entire company (summarized).
- `!get-evaluation user user_id` to get an evaluation for a specific user (summarized).
- `!get-evaluation feedback feedback_id` to get an evaluation of a specific feedback.
- `!get-evaluation` to get an evaluation for the current user.
Each command will return a structured JSON response with the corresponding evaluations.
```"""


@app.message(CMD_HELP)
def user_status_handler(message, say):
    say(MANUAL)


@app.message(CMD_WHO_AM_I)
def user_status_handler(message, say):
    user_id, user_name, relations = get_user_info_from_slack(message['user'], get_relations=True)
    if not user_id:
        say("You are nothin but a bunch of atoms.", thread_ts=message['ts'])
    else:
        say(f"""You are:
```
ID    : {user_id}
NAME  : {user_name}
RELATIONS : 
{json.dumps(relations, indent=1)}```""", thread_ts=message['ts'])


@app.message(CMD_CREATE_USER)
def create_user_handler(message, say):
    content = message["text"][len(CMD_CREATE_USER) + 1:]
    gen_id = Xid().string()
    insert_user(gen_id, content, 0)
    say(f"""A new user has been added!
```
ID      : {gen_id}
NAME    : {content}```""", thread_ts=message['ts'])


@app.message(CMD_ASSUME_USER)
def assume_user_handler(message, say):
    content = message["text"][len(CMD_ASSUME_USER) + 1:]

    user_id, _, _ = get_user_info(content)
    if not user_id:
        say("""Failed to assume user:
```user not found.```""", thread_ts=message['ts'])
        return

    assume_user(message['user'], user_id)

    say(f"""Successfully assumed user as:
```ID   : {user_id}```""", thread_ts=message['ts'])


@app.message(CMD_SET_RELATION)
def set_relation_handler(message, say):
    content = message["text"][len(CMD_SET_RELATION) + 1:]

    user_id, _, _ = get_user_info_from_slack(message['user'])
    if not user_id:
        say("""Failed to initiate:
```user not found.```""", thread_ts=message['ts'])
        return

    args = content.split(" ")
    if len(args) > 1:
        if user_id == args[0]:
            say(f"You can not add yourself as a relation.", thread_ts=message['ts'])
            return

        user_id_2, _, _ = get_user_info(args[0])
        if not user_id:
            say("""Target user not found.""", thread_ts=message['ts'])

        register_relation(user_id, user_id_2, args[1])

        say(f"""Successfully added relation.""", thread_ts=message['ts'])
    else:
        say(f"""Invalid arguments.""", thread_ts=message['ts'])


@app.message(CMD_MANUAL_START)
def manual_start_handler(message, say):
    user_id, user_name, relations = get_user_info_from_slack(message['user'], get_relations=True)
    if not user_id:
        say(f"""Failed to initiate:
```
make sure to create a user:
{CMD_CREATE_USER} $user_name

and assume your account as the created user:
{CMD_ASSUME_USER} $user_id
```
""", thread_ts=message['ts'])
        return

    response_msg, feedback_id = initiate_feedback(user_id, user_name, "Anything Forward", relations)
    say(f"\n```debug: feedback_id: {feedback_id}.```", thread_ts=message['ts'])
    say(response_msg)


@app.message(CMD_MANUAL_CALCULATE)
def manual_calculate_handler(message, say):
    user_id, _, _ = get_user_info_from_slack(message['user'])
    if not user_id:
        say(f"""Failed to initiate:
```
make sure to create a user:
{CMD_CREATE_USER} $user_name

and assume your account as the created user:
{CMD_ASSUME_USER} $user_id
```
""", thread_ts=message['ts'])
        return

    response_msg = evaluate_feedback(user_id)
    say(response_msg, thread_ts=message['ts'])


@app.message(CMD_GET_EVALUATION)
def get_evaluation_handler(message, say):
    content = message["text"][len(CMD_GET_EVALUATION) + 1:]
    args = content.split(" ")

    if len(args) > 0:
        if args[0] == "company":
            result = evaluation_for_company()
            say(
                text=f"""```{json.dumps(result, indent=1, default=str)}```""",
                thread_ts=message['ts']  # This replies in the thread
            )
        elif args[0] == "feedback" and len(args) > 1:
            evaluations = get_evaluation_from_feedback_id(args[1])
            if not evaluations or len(evaluations) < 1:
                say("Either feedback or evaluation not found. Run `!manual-evaluate` to evaluate feedbacks.",
                    thread_ts=message['ts'])
                return




            say(
                text=f"""```{json.dumps(evaluations, indent=1, default=str)}```""",
                thread_ts=message['ts']  # This replies in the thread
            )
            return
        elif args[0] == "user" and len(args) > 1:
            user_id, _, _ = get_user_info(args[1])
            if not user_id:
                say(f"""Failed to initiate chat:
            ```
            make sure to create a user:
            {CMD_CREATE_USER} $user_name

            and assume your account as the created user:
            {CMD_ASSUME_USER} $user_id
            ```""")
                return

            result = evaluation_for_user_id(user_id)
            say(
                text=f"""```{json.dumps(result, indent=1, default=str)}```""",
                thread_ts=message['ts']  # This replies in the thread
            )
        else:
            say("Invalid command.", thread_ts=message['ts'])
    else:
        user_id, _, _ = get_user_info_from_slack(message['user'])
        if not user_id:
            say(f"""Failed to initiate chat:
        ```
        make sure to create a user:
        {CMD_CREATE_USER} $user_name

        and assume your account as the created user:
        {CMD_ASSUME_USER} $user_id
        ```""")
            return

        result = evaluation_for_user_id(user_id)
        say(
            text=f"""```{json.dumps(result, indent=1, default=str)}```""",
            thread_ts=message['ts']  # This replies in the thread
        )


@app.message()
def default_handler(message, say):
    user_id, _, _ = get_user_info_from_slack(message['user'])
    if not user_id:
        say(f"""Failed to initiate chat:
```
make sure to create a user:
{CMD_CREATE_USER} $user_name

and assume your account as the created user:
{CMD_ASSUME_USER} $user_id
```""")
        return

    response_msg = continue_feedback(user_id, message["text"])
    if not response_msg:
        say(f"Your feedback session has been closed or has expired. "
            f"Run `{CMD_MANUAL_START}` to re-initiate a new session.")
    else:
        say(response_msg)


class HealthCheckHandler(tornado.web.RequestHandler):
    def get(self):
        self.write({"status": "OK"})


def make_app():
    return tornado.web.Application([
        (r"/health", HealthCheckHandler),
    ])


def run_tornado_server():
    tornado_app = make_app()
    tornado_app.listen(8080)
    tornado.ioloop.IOLoop.current().start()


# Start your app
if __name__ == "__main__":
    # Run the Tornado server in a new thread
    server_thread = threading.Thread(target=run_tornado_server)
    server_thread.start()

    SocketModeHandler(
        app,
        os.getenv('SLACK_APP_TOKEN')).start()
