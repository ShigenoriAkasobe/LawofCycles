import argparse
import os
import secrets
from datetime import timedelta

from flask import Flask, jsonify, render_template, request, session
from flask_session import Session
from waitress import serve

app = Flask(__name__)

# Configure Flask-Session for server-side sessions
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(32))
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_FILE_DIR"] = "/tmp/flask_session"
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# Automatically detect production environment (Render sets RENDER env var)
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("RENDER") is not None
app.config["SESSION_COOKIE_HTTPONLY"] = True

# Initialize Flask-Session
Session(app)


@app.route("/")
def index():
    """
    Main page route
    Reset state when page is loaded (browser refresh)
    """
    # Reset state on page load
    session["stored_flag"] = None
    session["stored_text"] = None
    session["counter"] = 0

    print("DEBUG: Page loaded - state reset")
    print(f"DEBUG: State after page load: {dict(session)}")

    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """
    Handle form submission
    """
    data = request.get_json()
    flag = data.get("flag")
    input_text = data.get("input_text", "").strip()
    print(f"{data=}")

    # Get current state from session
    stored_flag = session.get("stored_flag")
    stored_text = session.get("stored_text")
    counter = session.get("counter", 0)
    print(f"DEBUG: Before processing - {stored_flag=}, {stored_text=}, {counter=}")
    print(f"DEBUG: State contents: {dict(session)}")

    # Validation: check if input is empty
    if not input_text:
        return jsonify({"success": False, "error": "Input text cannot be empty."})

    # Validation: check if same flag is being used consecutively
    # stored_flag is not None means we have stored data
    if stored_flag is not None and stored_flag == flag:
        return jsonify(
            {
                "success": False,
                "error": f"Flag {flag} is already stored. Please use the opposite flag.",
            }
        )

    # Get bonus symbol (default to star emoji)
    bonus_symbol = data.get("bonus_symbol", "🌟")

    # Determine output
    output_text = ""
    if stored_flag is not None and stored_flag != flag:
        # Output the previously stored text only when flags are different
        output_text = stored_text

        # Increment counter when transitioning from B to A
        if flag == "A" and stored_flag == "B":
            counter += 1

            # Add bonus symbol every 3 cycles
            if counter > 0 and counter % 3 == 0:
                output_text = f"{bonus_symbol*3} {output_text} {bonus_symbol*3}"

    # Store current input in session
    session["stored_flag"] = flag
    session["stored_text"] = input_text
    session["counter"] = counter

    print(
        f"DEBUG: After storing - stored_flag={session.get('stored_flag')}, stored_text={session.get('stored_text')}, counter={session.get('counter')}"
    )
    print(f"DEBUG: State contents after: {dict(session)}")

    return jsonify(
        {
            "success": True,
            "output_text": output_text,
            "stored_flag": flag,
            "stored_text": input_text,
            "counter": counter,
        }
    )


@app.route("/reset", methods=["POST"])
def reset():
    """
    Reset the application state
    """
    print("DEBUG: Reset called")
    print(f"DEBUG: State before reset: {dict(session)}")

    session["stored_flag"] = None
    session["stored_text"] = None
    session["counter"] = 0

    print(f"DEBUG: State after reset: {dict(session)}")

    return jsonify({"success": True, "counter": 0, "stored_flag": None})


@app.route("/state")
def get_state():
    """
    Get current application state
    """
    return jsonify(
        {
            "stored_flag": session.get("stored_flag"),
            "stored_text": session.get("stored_text"),
            "counter": session.get("counter", 0),
        }
    )


def get_args():
    parser = argparse.ArgumentParser(description="GPU Performance Benchmark WebApp")
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Run the app in debug mode (default: False)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    host_num = "0.0.0.0"
    port_num = 5001

    print("Starting the application...")
    print(f"Please access http://localhost:{port_num} in your browser")

    args = get_args()
    if args.debug is True:
        app.run(debug=True, host=host_num, port=port_num)
    else:
        serve(app, host=host_num, port=port_num)
