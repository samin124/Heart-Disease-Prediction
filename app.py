import pickle
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import numpy as np

app = Flask(__name__)
app.secret_key = '12345'  # Change this to a random secret key

# Load the model
classifier = pickle.load(open('classifier.pkl', 'rb'))

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user storage for the sake of simplicity
users = {'admin': {'password': 'password123'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    return render_template('home.html')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    data = [float(x) for x in request.form.values()]
    data = np.array(data).reshape(1, -1)
    output = classifier.predict(data)[0]
    if output == 0:
        instruction = "Instructions for a healthy heart: Maintain a balanced diet, exercise regularly, avoid smoking, and monitor your blood pressure and cholesterol levels."
    else:
        instruction = "Instructions if at risk: Consult with a cardiologist, follow prescribed medications, maintain a healthy lifestyle, and undergo regular check-ups."

    return render_template("home.html", prediction_text=f"Prediction result: {output}", instruction=instruction)

@app.route('/predict_api', methods=['POST'])
@login_required
def predict_api():
    data = request.json['data']
    data = np.array(data).reshape(1, -1)
    output = classifier.predict(data)
    return jsonify(output[0])

if __name__ == '__main__':
    app.run(debug=True)
