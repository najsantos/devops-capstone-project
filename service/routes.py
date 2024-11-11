"""
Account Service

This microservice handles the lifecycle of Accounts
"""
# pylint: disable=unused-import
from flask import jsonify, request, make_response, abort, url_for   # noqa; F401
from service.models import Account
from service.common import status  # HTTP Status Codes
from . import app  # Import Flask application


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Account REST API Service",
            version="1.0",
            # paths=url_for("list_accounts", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A NEW ACCOUNT
######################################################################
@app.route("/accounts", methods=["POST"])
def create_accounts():
    """
    Creates an Account
    This endpoint will create an Account based the data in the body that is posted
    """
    app.logger.info("Request to create an Account")
    check_content_type("application/json")
    account = Account()
    account.deserialize(request.get_json())
    account.create()
    message = account.serialize()
    # Uncomment once get_accounts has been implemented
    # location_url = url_for("get_accounts", account_id=account.id, _external=True)
    location_url = "/"  # Remove once get_accounts has been implemented
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# LIST ALL ACCOUNTS
######################################################################

# ... place you code here to LIST accounts ...


######################################################################
# READ AN ACCOUNT
######################################################################

# Create a Flask route that responds to the GET method for the endpoint /accounts/<id>.
@app.route("/accounts/<int:id>", methods=["GET"])
# Create a function called read_account(id) to hold the implementation.
def read_account(id):
    """
    Reads an Account
    This endpoint will read an Account based on its ID
    """

    # Call the Account.find(), which will return an account by id.
    account = Account.find(id)

    # Abort with a return code HTTP_404_NOT_FOUND if the account was not found.
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{id}' was not found.")

    # Call the serialize() method on an account to serialize it to a Python dictionary.
    account_dict = account.serialize()

    # Send the serialized data and a return code of HTTP_200_OK back to the caller.
    return account_dict, status.HTTP_200_OK


######################################################################
# UPDATE AN EXISTING ACCOUNT
######################################################################

@app.route("/accounts/<int:id>", methods=["PUT"])
def update_products(id):
    """
    Update an Account
    This endpoint will update an Account based on the body that is posted
    """

    # Check request is provided in JSON format
    check_content_type("application/json")

    # Call the Account.find(), which will return an account by id.
    account = Account.find(id)
    if not account:
        abort(status.HTTP_404_NOT_FOUND, f"Account with id '{id}' was not found.")

    # Retrive request content and update account accordingly
    account.deserialize(request.get_json())
    account.id = id
    account.update()

    # Send the serialized data and a return code of HTTP_200_OK back to the caller.
    return account.serialize(), status.HTTP_200_OK


######################################################################
# DELETE AN ACCOUNT
######################################################################

# ... place you code here to DELETE an account ...


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
