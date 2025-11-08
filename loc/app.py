import argparse

from flask import Flask, jsonify, render_template, request
from waitress import serve

app = Flask(__name__)

# Global state storage (simpler approach for single-user demo)
# In production, use proper session management or database
app_state = {"stored_flag": None, "stored_text": None, "counter": 0}


@app.route("/")
def index():
    """
    Main page route
    Reset state when page is loaded (browser refresh)
    """
    global app_state

    # Reset state on page load
    app_state["stored_flag"] = None
    app_state["stored_text"] = None
    app_state["counter"] = 0

    print("DEBUG: Page loaded - state reset")
    print(f"DEBUG: State after page load: {app_state}")

    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    """
    Handle form submission
    """
    global app_state

    data = request.get_json()
    flag = data.get("flag")
    input_text = data.get("input_text", "").strip()
    print(f"{data=}")

    # Get current state
    stored_flag = app_state["stored_flag"]
    stored_text = app_state["stored_text"]
    counter = app_state["counter"]
    print(f"DEBUG: Before processing - {stored_flag=}, {stored_text=}, {counter=}")
    print(f"DEBUG: State contents: {app_state}")

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

    # Store current input
    app_state["stored_flag"] = flag
    app_state["stored_text"] = input_text
    app_state["counter"] = counter

    print(
        f"DEBUG: After storing - stored_flag={app_state['stored_flag']}, stored_text={app_state['stored_text']}, counter={app_state['counter']}"
    )
    print(f"DEBUG: State contents after: {app_state}")

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
    global app_state

    print("DEBUG: Reset called")
    print(f"DEBUG: State before reset: {app_state}")

    app_state["stored_flag"] = None
    app_state["stored_text"] = None
    app_state["counter"] = 0

    print(f"DEBUG: State after reset: {app_state}")

    return jsonify({"success": True, "counter": 0, "stored_flag": None})


@app.route("/state")
def get_state():
    """
    Get current application state
    """
    return jsonify(
        {
            "stored_flag": app_state["stored_flag"],
            "stored_text": app_state["stored_text"],
            "counter": app_state["counter"],
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
