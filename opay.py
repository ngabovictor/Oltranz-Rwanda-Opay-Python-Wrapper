import os
import json
import uuid
import requests


HEADERS = {
    "Accept":"application/json",
    "Content-Type":"application/json,charset=UTF-8"
}

BASE_URL = "https://opay-api.oltranz.com/opay/paymentrequest"

# SETUP OPAY ENVIRONMENT
def setup(ORGANIZATION_ID, CALLBACK_URL=None, **kwargs):

    # VALIDATIONS
    if CALLBACK_URL and not str(CALLBACK_URL).startswith("http"):
        raise Exception("CALLBACK_URL is not valid")
    
    if not ORGANIZATION_ID or len(str(ORGANIZATION_ID)) <= 0:
        raise Exception("ORGANIZATION_ID must be provided")

    # INITIAL SETUP

    if ORGANIZATION_ID is not None:
        os.environ['OPAY_ORGANIZATION_ID'] = str(ORGANIZATION_ID)

    if CALLBACK_URL is not None and str(CALLBACK_URL).startswith("http"):
        os.environ['OPAY_CALLBACK_URL'] = str(ORGANIZATION_ID)

    # LOOKING FOR CHARGE VALUE
    for key, value in kwargs.items():
        if "charge" in str(key).lower():
            try:
                os.environ["OPAY_CHARGES"] = str(float(value))
            except:
                pass

# VERIFY IF ORGANIZATION_ID IS PRESENT
def is_opay_ok():
    ORG = os.getenv("OPAY_ORGANIZATION_ID")

    if ORG is not None:
        return True
    return False

# CALCULATE PAYMENT AMOUNT BASING ON SET CHARGES:
def calculate_amount(amount, CHARGES=None):
    if not CHARGES and not os.getenv("OPAY_CHARGES"):
        CHARGES = 0
    elif not CHARGES and os.getenv("OPAY_CHARGES"):
        try:
            CHARGES = float(os.getenv("OPAY_CHARGES"))
        except:
            CHARGES = 0
    if CHARGES:
        try:
            CHARGES = float(CHARGES)
        except:
            raise Exception("Invalid value for CHARGES")
    
    try:
        amount = float(amount)
    except:
        raise Exception("Invalid value for initial amount")

    value = int(amount + (amount*CHARGES)/100)

    if value < 100:
        raise Exception("The minimum payment amount is {}".format(100))
    
    return value


# GENERATE RANDOM UUID
def generate_uuid():
    return str(uuid.uuid4())


# REQUEST PAYMENT
def request_payment(phone_number, amount, charges=None, transaction_id=None, callback_url=None, description=""):

    if not is_opay_ok():
        raise Exception("You have to call setup with ORGANIZATION_ID first.")

    if not phone_number.startswith("07") or len(phone_number) != 10:
        raise Exception("Invalid phone number")

    if not transaction_id:
        transaction_id = generate_uuid()

    ORG = os.getenv("OPAY_ORGANIZATION_ID")
    CALLBACK_URL = os.getenv("OPAY_CALLBACK_URL")

    if callback_url and not str(callback_url).startswith("http"):
        raise Exception("Invalid callback_url")
    else:
        CALLBACK_URL = callback_url
        
    if charges:
        try:
            charges = float(charges)
        except:
            raise Exception("Invalid value for charges")
    
    try:
        amount = float(amount)
        amount = calculate_amount(amount, CHARGES=charges)
    except:
        raise Exception("Invalid value for amount")
    
    BODY = {
        "organizationId":ORG,
        "telephoneNumber":phone_number,
        "description":description,
        "transactionId":str(transaction_id),
        "amount":str(amount)
    }

    if CALLBACK_URL:
        BODY["callbackUrl"] = CALLBACK_URL


    # INITIATING PAYMENT REQUEST

    response = requests.post(BASE_URL, json=BODY, headers=HEADERS)

    if response.status_code == 200:
        response = response.json()
        return response
    else:
        raise Exception("Something went wrong. The request return the error with status {}".format(response.status_code))