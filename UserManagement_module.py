from flask import Flask, jsonify, request
import mysql.connector
from flask_cors import CORS,cross_origin
import bcrypt
from flask_bcrypt import bcrypt
from connection import *
from queries import user_add,user_assign,user_show
import smtplib
import random
import logging
from datetime import datetime
from flask_bcrypt import Bcrypt
import re
mydb=connect_db()
cursor=mydb.cursor()

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
cors = CORS(app)
CORS(app, origins='*')
bcrypt = Bcrypt(app)

###########################################################################################################
                        #to add new user(authority of  alpha user)
###########################################################################################################

#import re
#to check valid name
def is_valid_name(name):
    pattern = r'^[a-zA-Z][a-zA-Z0-9]*$'
    return re.match(pattern, name) is not None and not name.isdigit()

#to check valid email
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

#To check valid phone_no.
def is_valid_phone_number(phone_number):
    # Remove any non-digit characters from the phone number
    cleaned_number = re.sub(r'\D', '', phone_number)

    # Check if the cleaned number matches the desired format
    pattern = r'^\d{10}$'  # Assumes a 10-digit phone number
    return re.match(pattern, cleaned_number) is not None

#to add new user
def adduser():
    try:
        now = datetime.now()
        dt_string = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        logging.debug(dt_string + " Inside add usder API.....")
        data = request.get_json()
        
        logging.debug(dt_string + " Taking Some inputs.....")
        
        if "name" not in data:
            return jsonify({"error": "Missing 'name' in request data"}), 400
        if "email_id" not in data:
            return jsonify({"error": "Missing 'email_id' in request data"}), 400
        if "contact" not in data:
            return jsonify({"error": "Missing 'contact' in request data"}), 400
        """ if "role" not in data:
            return jsonify({"error": "Missing 'role' in request data"}), 400"""

        name = data['name']
        
        email_id = data['email_id']
        
        contact = data['contact']

        #role = data['role']
        
        if  not is_valid_name(name):
            return jsonify({"error":"Invalid Name....Name can't start from Number,Can be a alphanumeric,special characters are not allowed"}),400
        if  not is_valid_email(email_id):
            return jsonify({"error":"Invalid Email"}),400
        if  not is_valid_phone_number(contact):
            return jsonify({"error":"Invalid Contact Number."}),400
        

        query="select 1 from users where email_id=%s;"
        values=(email_id,)
        cursor.execute(query,values)
        id=cursor.fetchone()
        if id:
               return jsonify({"error":"email already exists."}),400



        logging.debug("11111111")
        def send_otp_email(receiver_email, otp):
            
            logging.debug(dt_string + " Entered send_otp_email function....")
            
            sender_email = "pratik@infobellit.com"  # Replace with your email address
            
            password = "mzygirleuqcwzwtk"  # Replace with your email password

            message = f"Subject: login credentials for Project Management Tool\n\n Your Username is your email.\nYour password is: {otp}"
            
            logging.debug(dt_string + " Sending email....")
            
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
            
                server.login(sender_email, password)
                
                server.sendmail(sender_email, receiver_email, message)
            

        def generate_otp(length=6):
            
            logging.debug(dt_string + " Entered into generate_otp function....")
            
            digits = "0123456789abcdefghijklmnopqrstuvwxyz"
            
            otp = ""
            
            for _ in range(length):
            
                otp += random.choice(digits)
            
            logging.debug(dt_string + " OTP generated sucessfully....")
            
            return otp

        # Example usage
        email = email_id  # Replace with the recipient's email address
        
        logging.debug(dt_string + " calling generate_otp function...")
        
        otp = generate_otp()
        
        logging.debug(dt_string + " calling send_otp_email function....")
        
        send_otp_email(email, otp)
        
        print("OTP sent successfully!")


        # Hash the password
        logging.debug(dt_string + " Encrypting the generated password....")
       
        hashed_password = bcrypt.generate_password_hash(otp).decode('utf-8')

        logging.debug(dt_string + " calling user_add function to update the database....")

        return user_add(name, email_id,hashed_password, contact)  #add role 

    except KeyError as e:
        # Handle missing key in the request data
        #print(dt_string + " Missing key in request data: " + str(e))
        
        return jsonify({"error": str(e)}), 400

    except mysql.connector.Error as err:
        # Handle MySQL database-related errors
        print(" Database error: " + str(err))
        
        return jsonify({"error": "Database error: " + str(err)}), 500

    except Exception as e:
        # Handle any other unexpected exceptions
        print(" An error occurred: " + str(e))
        
        return jsonify({"error": "An error occurred: " + str(e)}), 500


############################################################################################################
                            # API to Assign a user to a particular project    
############################################################################################################



#to assign a user to new project
def assignuser():
    try:
        now = datetime.now()
        dt_string = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        logging.debug(dt_string + " Inside assign user api...")
        data = request.get_json()
        
        logging.debug(dt_string + " Accepting some values....")

        if "project_id" not in data:
            return jsonify({"error": "Missing 'project_id' in request data"}), 400
        if "user_ID" not in data:
            return jsonify({"error": "Missing 'user_id' in request data"}), 400
        if "role_in_project" not in data:
            return jsonify({"error": "Missing 'role_in_project' in request data"}), 400
        

        project_id=data['project_id']
        
        user_ID =data["user_ID"]
        
        role_in_project = data["role_in_project"]
        

        if(type(project_id) is not int):
            return jsonify({"error":"project_id must be integer"}),400
        if(type(user_ID) is not int):
            return jsonify({"error":"user_id must be integer"}),400
        

        logging.debug(dt_string + " checking if the project manager role already existing or not since tere can be only one project manager per project....")
        
        if(role_in_project=='Project manager'):
            
            return jsonify({"error":"Their can only be one Project manager per project"}),400
        
        else:
            
            logging.debug(dt_string + " calling user_assign function to update the databse....")
            
            return user_assign(project_id,user_ID,role_in_project)

    except KeyError as e:
        # Handle missing key in the request data
        
        #print("Missing key in request data: " + str(e))
        
        return jsonify({"error": str(e)}), 400

    except mysql.connector.Error as err:
        # Handle MySQL database-related errors
        
        print("Database error: " + str(err))
        
        return jsonify({"error": "Database error: " + str(err)}), 500

    except Exception as e:
        # Handle any other unexpected exceptions
        
        print("An error occurred: " + str(e))
        
        return jsonify({"error": "An error occurred: " + str(e)}), 500
    

############################################################################################################
                            # API to show all users to added     
############################################################################################################




def showuser():
    try:
        now = datetime.now()
        dt_string = str(now.strftime("%d/%m/%Y %H:%M:%S"))
        logging.debug(dt_string + " Inside show user api...")
       
        return user_show()

    except KeyError as e:
        # Handle missing key in the request data
        
        #print("Missing key in request data: " + str(e))
        
        return jsonify({"error": str(e)}), 400

    except mysql.connector.Error as err:
        # Handle MySQL database-related errors
        
        print("Database error: " + str(err))
        
        return jsonify({"error": "Database error: " + str(err)}), 500

    except Exception as e:
        # Handle any other unexpected exceptions
        
        print("An error occurred: " + str(e))
        
        return jsonify({"error": "An error occurred: " + str(e)}), 500
    


    
    



    

