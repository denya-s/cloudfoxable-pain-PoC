from flask import Flask, request

# Initialize the Flask application
app = Flask(__name__)

# Define a route to handle POST requests.
@app.route('/', methods=['POST'])

def receive_post():

    # Get the data from the POST request
    # This gets the raw body of the request
  
    form_data = request.form

    print(f"Received Form Data: {form_data}")  # Prints form data.

    # Return a response (you can customize this as needed)
    return "Data received successfully", 200

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # listen on all interfaces
