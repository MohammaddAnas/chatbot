from flask import Flask, render_template, request, session
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("secret_key)

genai.configure(api_key=os.getenv("api_key"))

model = genai.GenerativeModel("gemini-2.5-flash")

with open("prompts.json", "r", encoding="utf-8") as file:
    prompts = json.load(file)


def build_system_prompt():

    system_prompt = ""

    for value in prompts["system_prompt"].values():
        if isinstance(value, list):
            system_prompt += "\n".join(value)
            system_prompt += "\n\n"

    return system_prompt.strip()


SYSTEM_PROMPT = build_system_prompt()


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "GET":
        session.clear()
        session["history"] = []

    if "history" not in session:
        session["history"] = []

    if request.method == "POST":

        user_message = request.form.get("message", "").strip()

        if user_message:

            try:

                chat = model.start_chat(history=[])

                chat.send_message(SYSTEM_PROMPT)

                for chat_item in session["history"]:

                    chat.send_message(chat_item["user"])
                    chat.send_message(chat_item["bot"])

                response = chat.send_message(user_message)

                bot_response = response.text

                history = session["history"]

                history.append(
                    {
                        "user": user_message,
                        "bot": bot_response
                    }
                )

                session["history"] = history

            except Exception as error:

                history = session["history"]

                history.append(
                    {
                        "user": user_message,
                        "bot": f"Error: {error}"
                    }
                )

                session["history"] = history

    return render_template(
        "index.html",
        history=session["history"]
    )


@app.route("/clear")
def clear_chat():

    session.pop("history", None)

    return render_template(
        "index.html",
        history=[]
    )


if __name__ == "__main__":
    app.run()
