import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code indicating
    reason for failure
'''


@app.route('/drinks', methods=['GET'])
def retrieve_drinks():
    """
    This is the API to retrieve short form of drinks.
    ---
    responses:
        422:
            description: error retrieving data from database
        200:
            description: success
            schema:
                success:
                    type: bool
                    description: success code
                    default: True
                drinks:
                    type: list
                    description: the list of drinks
                    items:
                        type: dict
    """
    try:
        drinks = Drink.query.all()
        print("drinks: ", drinks)
        drinks_short = [drink.short() for drink in drinks]
    except Exception as e:
        print('error retrieving drinks.')
        print(e)
        abort(422)
    return jsonify({
        "success": True,
        "drinks": drinks_short
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks or appropriate status code
    indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def retrieve_drinks_detail(payload):
    """
    This is the API to retrieve long form of drinks.
    ---
    responses:
        422:
            description: error retrieving data from database
        401:
            description: authentication error
        200:
            description: success
            schema:
                success:
                    type: bool
                    description: success code
                    default: True
                drinks:
                    type: list
                    description: the list of drinks
                    items:
                        type: dict
    """
    try:
        drinks = Drink.query.all()
        drinks_long = [drink.long() for drink in drinks]
    except Exception as e:
        print('error retrieving drink details.')
        print(e)
        abort(422)
    return jsonify({
        "success": True,
        "drinks": drinks_long
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(payload):
    """
    This is the API to post a new drink.
    ---
    parameters:
        - name: title
            in: body
            type: string
            required: true
            description: the title of a drink
        - name: recipe
            in: body
            type: string
            required: true
            description: the recipe of the drink
    responses:
        401:
            description: authentication error
        422:
            description: error saving data into the database
        200:
            description: success
            schema:
                success:
                    type: bool
                    description: success code
                    default: True
                drinks:
                    type: list
                    description: the list of drinks
                    items:
                        type: dict
    """
    try:
        body = request.get_json()
        title = body.get("title", None)
        recipe = body.get("recipe", None)
        drink = Drink(
            title=title,
            recipe=json.dumps(recipe)
        )
        drink.insert()
        drink_rep = drink.long()
    except Exception as e:
        print('error adding new drink.')
        print(e)
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return jsonify({
        "success": True,
        "drinks": [drink_rep]
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):
    """
    This is the API to edit an existing drink.
    ---
    parameters:
        - name: drink_id
            in: path
            type: integer
            required: true
            description: the id of an existing drink
        - name: title
            in: body
            type: string
            required: true
            description: the title of a drink
        - name: recipe
            in: body
            type: string
            required: true
            description: the recipe of the drink
    responses:
        401:
            description: authentication error
        422:
            description: error saving data into the database
        200:
            description: success
            schema:
                success:
                    type: bool
                    description: success code
                    default: True
                drinks:
                    type: list
                    description: the list of drinks
                    items:
                        type: dict
    """
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        body = request.get_json()
        title = body.get('title', 'default')
        recipe = body.get('recipe', '')
        drink.title = title
        drink.recipe = recipe
        drink_rep = drink.long()
        db.session.commit()
    except Exception as e:
        print('error patching existing drink.')
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return jsonify({
        'success': True,
        'drinks': [drink_rep]
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
    or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
    This is the API to delete an existing drink.
    ---
    parameters:
        - name: drink_id
            in: path
            type: integer
            required: true
            description: the id of an existing drink
    responses:
        401:
            description: authentication error
        422:
            description: error saving data into the database
        200:
            description: success
            schema:
                success:
                    type: bool
                    description: success code
                    default: True
                delete:
                    type: integer
                    description: the deleted drink id
    """
    try:
        drink = Drink.query.get(drink_id)
        if drink is None:
            abort(404)
        db.session.delete(drink)
        db.session.commit()
    except Exception as e:
        print('error deleting existing drink.')
        db.session.rollback()
        abort(422)
    finally:
        db.session.close()
    return jsonify({
        'success': True,
        'delete': drink_id
    })


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Authorization header must be bearer token."
    }), 400


@app.errorhandler(401)
def unauthorized_client_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "Unauthorized client error."
    }), 401


@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "forbidden"
    }), 403


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(e: AuthError):
    return jsonify({
        "success": False,
        "error": e.status_code,
        "message": e.error
    })
