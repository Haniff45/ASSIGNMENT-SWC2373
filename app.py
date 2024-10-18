from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages
WEBEX_API_BASE = 'https://webexapis.com/v1'

# Helper functions
def get_user_info(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/people/me', headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_rooms(access_token, max_rooms=5):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f'{WEBEX_API_BASE}/rooms', headers=headers)
    if response.status_code == 200:
        return response.json().get('items', [])[:max_rooms]
    return None

def send_message(access_token, room_id, message):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {'roomId': room_id, 'text': message}
    response = requests.post(f'{WEBEX_API_BASE}/messages', headers=headers, json=data)
    return response.status_code == 200

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        user_info = get_user_info(access_token)
        if user_info:
            return redirect(url_for('menu', access_token=access_token))
        flash("Invalid access token. Please try again.")
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/menu/<access_token>', methods=['GET'])
def menu(access_token):
    return render_template('menu.html', access_token=access_token)

@app.route('/test_connection/<access_token>', methods=['GET'])
def test_connection(access_token):
    """Test connection to the Webex server."""
    user_info = get_user_info(access_token)
    if user_info:
        flash("Connection to Webex server was successful.")
    else:
        flash("Failed to connect to Webex server. Please check your access token.")
    return redirect(url_for('menu', access_token=access_token))

@app.route('/view_user_info/<access_token>', methods=['GET'])
def view_user_info(access_token):
    """View user information."""
    user_info = get_user_info(access_token)
    if user_info:
        return render_template('user_info.html', user_info=user_info, access_token=access_token)
    flash("Failed to retrieve user information.")
    return redirect(url_for('menu', access_token=access_token))

@app.route('/list_rooms/<access_token>', methods=['GET'])
def list_rooms(access_token):
    """List rooms in Webex."""
    rooms = get_rooms(access_token)
    if rooms is not None:
        return render_template('rooms.html', rooms=rooms, access_token=access_token)
    flash("Failed to retrieve rooms. Please check your access token or network connection.")
    return redirect(url_for('menu', access_token=access_token))

@app.route('/send_message/<access_token>', methods=['GET', 'POST'])
def send_message_route(access_token):
    """Send a message to a Webex room."""
    if request.method == 'POST':
        room_id = request.form.get('room_id')
        message = request.form.get('message')
        if send_message(access_token, room_id, message):
            flash("Message sent successfully.")
        else:
            flash("Failed to send message.")
        return redirect(url_for('menu', access_token=access_token))
    
    # Use 'GET' to render the send message form
    rooms = get_rooms(access_token)
    if rooms is not None:
        return render_template('send_message.html', rooms=rooms, access_token=access_token)
    flash("Failed to retrieve rooms.")
    return redirect(url_for('menu', access_token=access_token))

if __name__ == '__main__':
    app.run(debug=True)
