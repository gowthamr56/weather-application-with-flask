# FIREBASE AUTHENTICATION ESSENTIALS
import pyrebase
import json

config = json.load(open("firebase_config.json", "r"))

pb = pyrebase.initialize_app(config)
auth = pb.auth()

def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        auth.send_email_verification(user["idToken"])
    except Exception as e:
        if "EMAIL_EXISTS" in e.strerror:
            return "E-mail already exists", "danger"
        elif "WEAK_PASSWORD" in e.strerror:
            return "Password should be atleast 6 characters", "danger"
        else:
            return e.strerror, "danger"
    else:
        return "Successfully signed up", "success"

def signin(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        isVerified = auth.get_account_info(user["idToken"])["users"][0]["emailVerified"]
        
        # if isVerified:
        return ("Successfully logged in", "success") if isVerified else ("Email not verified, check your inbox", "warning")
        # elif not isVerified:
        #     auth.send_email_verification(user["idToken"])
        #     return ("Email not verified, check your inbox", "warning")
    
    except Exception as e:
        if "INVALID_PASSWORD" in e.strerror:
            return "Incorrect password", "danger"
        elif "EMAIL_NOT_FOUND" in e.strerror:
            return "Incorrect e-mail", "danger"