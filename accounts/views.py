# accounts/views.py
import json
from django.shortcuts import render, HttpResponse
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view

import pymongo
from pymongo import MongoClient
from firebase_admin import auth


# Update the MongoDB URI to point to your MongoDB server
uri = 'localhost'
# Create a new client and connect to the server
client = MongoClient(uri)


# @csrf_exempt
# @api_view(['POST'])
def register(request):
    if request.method == 'POST':
        # Use request.POST to access POST parameters
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']

        # Check if any of the required parameters are missing
        if not (email and password):
            return JsonResponse({'error': 'Email and password are required.'})

        if len(password) < 8:
            return JsonResponse({'error': 'The password is too short. It must contain at least 8 characters.'})


        # Save user data to MongoDB
        # Select the database where you want to store user data
        db = client['root']
        # db.connect()

        # Choose or create a collection for user data
        collection = db['root']

        #if user already exist
        user = collection.find_one({'username': username})
        em = collection.find({'email': email})

        if user and em:
            return JsonResponse({'error': 'User Already Exist'})

        # Create a document with user data
        user_document = {
            'username': username,
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name
        }

        # Insert the user data into the collection
        x=collection.insert_one(user_document)

        # Redirect to the home page or any other page you want
        request.session['username'] = username
        request.session['email'] = email
        request.session['first_name'] = first_name
        request.session['last_name'] = last_name
        
        try:
            # Create a user in Firebase Authentication
            user = auth.create_user(
                email=email,
                password=password,
            )

            # Generate a custom Firebase token for the newly created user
            custom_token = auth.create_custom_token(user.uid)

            return HttpResponseRedirect('/accounts/profile/view')
        except auth.AuthError as e:
            return JsonResponse({'error': str(e)}, status=400)



def login(request):
    if request.method == 'POST':
        # Use request.POST to access POST parameters
        username = request.POST['username']
        password = request.POST['password']

        # Check if username and password are provided
        if not (username and password):
            return JsonResponse({'error': 'Username and password are required.'})

        try:
            # Verify the Firebase custom token (sent by the client)
            decoded_token = auth.verify_id_token(password)
            uid = decoded_token['uid']

            if uid == username:
                # Redirect to the profile view with the username as a parameter
                return HttpResponseRedirect('/accounts/profile/view?username={}'.format(username))
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)
        except auth.AuthError as e:
            return JsonResponse({'error': str(e)}, status=400)
        
    else:
        return render(request, 'template/login.html')


def profile(request):
    # Retrieve user data from the session
    if not request.session.get('username'):
        return JsonResponse({'error': 'Unauthorized'})

    username = request.session.get('username')
    email = request.session.get('email')
    first_name = request.session.get('first_name')
    last_name = request.session.get('last_name')

    # Pass the user data to the profile template
    context = {
        'username': username,
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
    }

    return render(request, 'template/profile.html', context)

def edit(request):
    if not request.session.get('username'):
        return JsonResponse({'error': 'Unauthorized'})

    if request.method == 'POST':
        # Get the current user's username from the session
        username = request.session.get('username')

        # Get the form data from the request
        new_username = request.POST.get('new_username')
        new_first_name = request.POST.get('new_first_name')
        new_last_name = request.POST.get('new_last_name')
        
        # Connect to the MongoDB database where user data is stored
        db = client['root']
        collection = db['root']

        # Find the user by username in the MongoDB collection
        user = collection.find_one({'username': username})

        if user:
            # Update the user's information
            user['username'] = new_username
            user['first_name'] = new_first_name
            user['last_name'] = new_last_name

            # Update the document in the collection
            collection.update({'_id': user['_id']}, user)

            # Update the user's data in the session
            request.session['username'] = new_username
            request.session['first_name'] = new_first_name
            request.session['last_name'] = new_last_name

            return HttpResponseRedirect('/accounts/profile/view')
        else:
            return JsonResponse({'error': 'User not found.'})
    else:
        # Render the edit form template
        return render(request, 'template/edit.html')
