# WEATHER FORECASTING APPLICATION WITH AUTHENTICATION USING PYTHON, FLASK AND FIREBASE
from flask import Flask, render_template, url_for, request, flash, redirect, session
from werkzeug.utils import secure_filename
import auth_essentials
from dotenv import load_dotenv
import os, requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(10)
app.upload_folder = "static\weather_icon"

@app.route("/")
def mainpage():
    cloud_svg = url_for("static", filename="icons/cloudy.svg")
    python_svg = url_for("static", filename="icons/python.svg")
    flask_svg = url_for("static", filename="icons/flask.svg")
    firebase_svg = url_for("static", filename="icons/firebase.svg")

    return render_template("mainpage.html", 
        cloud_svg = cloud_svg,
        python_svg = python_svg,
        flask_svg = flask_svg,
        firebase_svg = firebase_svg
    )

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        
        if password1 != password2:
            flash("Both passwords should be same", category="danger")
        else:
            message, category = auth_essentials.signup(email, password1)
            if category != "success":
                flash(message, category=category)
            else:
                return redirect("/signin")        

    return render_template("sign_up.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if "user" in session:
        return redirect("/home")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        message, category = auth_essentials.signin(email, password)
        # message = auth_essentials.signin(email, password)
        print("*"*10)
        print(message)
        print("*"*10)
        if category in ["success", "warning"]:
            session["user"] = email
            flash(message, category=category)
            return redirect("/home")
        flash(message, category=category)

    return render_template("sign_in.html")

def signout():
    session.pop("user")

@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" in session:
        if request.method == "POST":
            if "city" in request.form:
                base_url = "http://api.openweathermap.org/data/2.5/weather?"
                icon_url = "http://openweathermap.org/img/wn/{}@2x.png"

                city = request.form["city"]
                
                api_key = os.getenv("API_KEY")
                complete_url = f"{base_url}appid={api_key}&q={city}"
                res = requests.get(complete_url)
                data = res.json()

                if data["cod"] == "404":
                    message, category = data["message"].title(), "danger"
                    flash(message, category=category)
                    return redirect("/home")
                else:
                    icon_id = data["weather"][0]["icon"]
                    icon = icon_url.format(icon_id)
                    place = data["name"]
                    print(place)
                    country = data["sys"]["country"]
                    description = data["weather"][0]["description"]
                    temp = round(data["main"]["temp"] - 273.15)  # converting the temperature which is in kelvin to celcius
                    temp_max = round(data["main"]["temp_max"] - 273.15)  # converting the temperature which is in kelvin to celcius
                    temp_min = round(data["main"]["temp_min"] - 273.15)  # converting the temperature which is in kelvin to celcius
                    feels_like = round(data["main"]["feels_like"] - 273.15) # converting the temperature which is in kelvin to celcius
                    humidity = data["main"]["humidity"]
                    
                    # Getting weather icon
                    r = requests.get(icon)
                    content = r.content
                    # Saving the icon in static/weather_icon folder with PNG format
                    path = os.path.join(
                        os.path.abspath(os.path.dirname(__file__)),
                        app.upload_folder,
                        secure_filename("icon.png")
                    )
                    print(path)
                    with open(path, "wb") as file:
                        file.write(content)

                    icon_path = url_for("static", filename="weather_icon/icon.png")

                    weather_report = (temp, icon_path, description, feels_like, temp_max, temp_min, humidity, place, country)

                    return render_template("home.html", city=city, report=weather_report)

                return render_template("home.html", city=city)
            else:
                signout()
                return redirect("/")
        return render_template("home.html")
    else:
        return redirect("/signin")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)