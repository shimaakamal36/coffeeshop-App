import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink,db
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)
@app.after_request
def after_request(response):
        response.headers.add('Access_Control_Allow_Headers','Content_type')
        response.headers.add('Access_Control_Allow_Methods','GET,POST,DELETE,PATCH,OPTIONS')
        return response

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks=Drink.query.all()
        if drinks == []:
            abort(404)
        drinks_recipe=[]
        for drink in drinks:
            drinks_recipe.append(drink.short())
        return jsonify({
                "success": True, 
                "drinks": drinks_recipe
                  })  
    except:
        abort(404)
    finally:
        db.session.close()
    
        


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    try:
        drinks=Drink.query.all()
        if drinks ==[]:
            abort(404)
        drinks_detail=[]
        for drink in drinks:
            drinks_detail.append(drink.long())
        return jsonify({
                "success": True, 
                "drinks": drinks_detail
                  })  
    except:
        abort(404)
    finally:
         db.session.close()
    

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks' , methods=['POST'])
@requires_auth('post:drinks')
def add_new_drinks():
    try:
        title=request.get_json()['title']
        recipe=request.get_json()['recipe']
        new_drink=Drink(title=title,recipe=json.dumps(recipe))
        new_drink.insert()
        drink=[]
        drink_detail=new_drink.long()
        drink.append(drink_detail)
        return jsonify({"success": True,
                        "drinks": drink})
    except:
        abort(422)
    finally:
         db.session.close()
'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>',methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(id):
    drink=Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        updated_drink=request.get_json()
        if "title" in updated_drink:
            drink.title=updated_drink['title']
        if "recipe" in updated_drink:
            drink.recipe=json.dumps(updated_drink['recipe'])
        drink.update()
        updated_drink=[]
        updated_drink.append(drink.long())
        return jsonify({"success": True,
                        "drinks": updated_drink})
    except:
        abort(422)
    finally:
        db.session.close()
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>' , methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    drink=Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        drink.delete()
        return jsonify({"success": True, 
                        "delete": id})
    except:
        abort(422)
    finally:
        db.session.close()
## Error Handling
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
@app.errorhandler(404)
def Not_Found(error):
    return jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "Drink is not Found"
                    }), 404
@app.errorhandler(405)
def Method_Not_allowed(error):
    return jsonify({
                    "success": False, 
                    "error": 405,
                    "message": "Method not allowed"
                    }), 405


@app.errorhandler(400)
def Bad_request(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "Bad request"
                    }), 400
@app.errorhandler(401)
def unauthenicated(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "user is not authenicated"
                    }), 401
@app.errorhandler(403)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "user is not authorized to perform that action"
                    }), 403



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
                    "success": False, 
                    "error": error.status_code,
                    "message": error.error['description']
                    }), error.status_code

   