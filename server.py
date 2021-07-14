"""Server for bread journal app."""

from flask import Flask, render_template, request, redirect, flash, session
from model import connect_to_db
import crud
import os

from jinja2 import StrictUndefined

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') # autogenerated and in secrets.sh
app.jinja_env.undefined = StrictUndefined

@app.route('/')
@app.route('/home')
def view_home():
    """View home."""
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    """Process users login form."""
    # login page is not rendered, only redirects either 
    # back to home page or to user page- is slower but 
    # is cleaner; speed is negligible

    email = request.form['email']
    password = request.form['password']

    user = crud.get_user_by_email(email)
    if user and user.password == password: 
        session["user_id"] = user.id
        return redirect('/user')
    else:
        flash('There was an error logging in! Please try again or make an account.')
        return redirect('/')


@app.route('/user')
def user_page():
    
    user = crud.get_user_by_id(session["user_id"])
    recipes = crud.get_recipes_by_user(session["user_id"])

    return render_template('user.html', username=user.username, recipes=recipes)

@app.route('/experiment/<recipe_id>')
def display_recipe_details(recipe_id):

    # get recipe by id
    recipe = crud.get_recipe_by_id(recipe_id)
    amounts = crud.get_amounts_by_recipe(recipe_id)

    # get ingredients

    return render_template('recipe_details.html', recipe=recipe, amounts=amounts) # pass in ingredients

@app.route('/new-user')
def new_user():
    """View form to register new user."""

    return render_template('new_user.html')

@app.route('/register-user', methods=['POST'])
def register_new_user():
    """Process form from new user."""

    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # check if user already exists, flash message + redirect to top
    # how to handle unique fields
    new_user = crud.create_user(username, email, password)

    flash('Success! Account made. Please log in.')

    return redirect('/home')
    

@app.route('/test-recipe')
def design_recipe():
    """View form for user to input new recipe details."""

    return render_template('recipe_form.html')

# one route to show form, one route to process form

@app.route('/create-recipe', methods=['POST']) # just post??
def create_new_recipe():
    """Process form from new recipe form, add to database."""

    # get user id from session
    user_id = session["user_id"]

    # get recipe attributes from form
        # conditional attributes? if they exist, set them
    date = request.form['date'] 
    instructions = request.form['instructions'] 
    name = request.form['name'] or None
    observations = request.form['observations'] or None
    baking_time = request.form['baking-time'] or None
    baking_temp = request.form['baking-temp'] or None

    # how would dynamic ingredients list be returned?
    # while loop get ingredient id from ingredient table
        # using user id and ingredient id, add amount to RecipeIngredient table

    # new_ingredients = create crud join query that given a user id and/or recipe id, return joined ingredient name and amount

    # is ingredients table solid state?? Users click on options available
    # in db columns to add, otherwise have to character match
    # how to do custom inputs?? standardize string format, check if in db, if not, create column

    flash("Recipe successfully created!")

    new_recipe = crud.create_recipe(user_id, date, instructions, name, observations, baking_time, baking_temp)
    print(new_recipe)

    return redirect('/user')

@app.route('/feed-starter')
def feed_starter():
    """View form for user to input starter feeding details."""

    return render_template('feeding-form.html')

@app.route('/create-feeding', methods=['POST'])
def create_new_feeding():
    """Process form from new starter feeding form, add to database."""

    user_id = session["user_id"]

    date = request.form['date']
    instructions = request.form['instructions']
    name = request.form['name']
    observations = request.form['observations']
    baking_time = request.form['baking-time']
    baking_temp = request.form['baking-temp']

    if name == "":
        name = None

    if observations == "":
        observations = None
    
    if baking_time == "":
        baking_time = None

    if baking_temp == "":
        baking_temp = None

    flash(f"Starter successfully fed!")

    new_feeding = crud.create_starter_feeding(user_id, date, instructions, name, observations, baking_time, baking_temp)
    print(new_feeding)

    return redirect('/user')


if __name__ == '__main__':
    connect_to_db(app)
    app.run(host='0.0.0.0', debug=True)