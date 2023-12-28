import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


from .models import User,Posts,Likes,Followers,Followings


def like(request, id):
    post = Posts.objects.get(pk=id)
    user = User.objects.get(pk=request.user.id)
    checker = None
    if Likes.objects.filter(liked_post=post, user=request.user).exists():
        post.likes.remove(request.user)
        checker = 0
        Likes.objects.get(liked_post=post, user=request.user).delete()
    else:
        post.likes.add(request.user)
        checker = 1
        new_like = Likes(
            liked_post=post,
            user=user
        )
        new_like.save()
    post.save()
    
    
    likesAll = post.likes.count()
    data = {
        "check": checker,
        "likes_count": likesAll
    }
    return JsonResponse(data)

def index(request):
    posts = Posts.objects.all().order_by('id').reverse()

    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    likesId = []
    if(request.user != None):
        likes = Likes.objects.all()
        for like in likes:
            if like.user.id == request.user.id:
                likesId.append(like.liked_post.id)
    

    return render(request, "network/index.html", {
        "posts": posts,
        "page_obj": page_obj,
        "likes": likesId
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def post(request):
    if request.method == "POST":
        content = request.POST["post-body"]
        user = request.user
        new_post = Posts(
            user=user,
            content=content
        )
        new_post.save()
        return HttpResponseRedirect(reverse("index"))

def profile(request, user_id):
    targeted_user = User.objects.get(pk=user_id)
    posts = Posts.objects.filter(user=targeted_user)
    current_user = request.user

    users_posts = posts.order_by('id').reverse()
    isFollowing = None
    if request.user.is_authenticated:
        isFollowing = None
        if Followings.objects.filter(user=current_user).exists():
            if targeted_user in Followings.objects.get(user=current_user).followings.all():
                isFollowing = True
            else:
                isFollowing = False
        else:
            isFollowing = False

    #counting followings

    if Followings.objects.filter(user=targeted_user).exists():
        count_of_followings = Followings.objects.get(user=targeted_user).followings.count()
    else:
        count_of_followings = 0

    # counting-followers
    if Followers.objects.filter(user=targeted_user).exists():
        count_of_followers = Followers.objects.get(user=targeted_user).followers.count()
    else:
        count_of_followers = 0
    
    #liked posts
    likesId = []
    if(request.user != None):
        likes = Likes.objects.all()
        for like in likes:
            if like.user.id == request.user.id:
                likesId.append(like.liked_post.id)
    
    # paginator
    paginator = Paginator(users_posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "followers_count": count_of_followers,
        "followings_count": count_of_followings,
        "posts": users_posts,
        "likes": likesId,
        "page_obj": page_obj,
        "user": targeted_user,
        "isFollowing": isFollowing,
        "current_user": current_user
    })

def follow(request, user_id):
    targeted_user = User.objects.get(pk=user_id)
    current_user = request.user
    posts = Posts.objects.filter(user=targeted_user)

    users_posts = posts.order_by('id').reverse()

    #to follow 

    if Followings.objects.filter(user=current_user).exists():
        Followings.objects.get(user=current_user).followings.add(targeted_user)
    else:
        new_following = Followings(user=current_user)
        new_following.save()
        Followings.objects.get(user=current_user).followings.add(targeted_user)
    
    if Followers.objects.filter(user=targeted_user).exists():
        Followers.objects.get(user=targeted_user).followers.add(current_user)
    else:
        new_followers = Followers(user=targeted_user)
        new_followers.save()
        Followers.objects.get(user=targeted_user).followers.add(current_user)

    # isFollowing
    isFollowing = None

    if Followings.objects.filter(user=current_user).exists():
        if targeted_user in Followings.objects.get(user=current_user).followings.all():
            isFollowing = True
        else:
            isFollowing = False
    else:
        isFollowing = False
    #counting followings
    if Followings.objects.filter(user=targeted_user).exists():
        count_of_followings = Followings.objects.get(user=targeted_user).followings.count()
    else:
        count_of_followings = 0

    # counting-followers
    if Followers.objects.filter(user=targeted_user).exists():
        count_of_followers = Followers.objects.get(user=targeted_user).followers.count()
    else:
        count_of_followers = 0
    
    #liked posts
    likesId = []
    if(request.user != None):
        likes = Likes.objects.all()
        for like in likes:
            if like.user.id == request.user.id:
                likesId.append(like.liked_post.id)
    
    # paginator
    paginator = Paginator(users_posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "followers_count": count_of_followers,
        "followings_count": count_of_followings,
        "posts": users_posts,
        "likes": likesId,
        "page_obj": page_obj,
        "user": targeted_user,
        "isFollowing": isFollowing,
        "current_user": current_user
    })

def unfollow(request, user_id):
    targeted_user = User.objects.get(pk=user_id)
    current_user = request.user
    posts = Posts.objects.filter(user=targeted_user)

    users_posts = posts.order_by('id').reverse()

    #to unfollow logic 
    
    Followings.objects.get(user=current_user).followings.remove(targeted_user)
    
    Followers.objects.get(user=targeted_user).followers.remove(current_user)

    # isFollowing
    isFollowing = None

    if Followings.objects.filter(user=current_user).exists():
        if targeted_user in Followings.objects.get(user=current_user).followings.all():
            isFollowing = True
        else:
            isFollowing = False
    else:
        isFollowing = False
    #counting followings
    if Followings.objects.filter(user=targeted_user).exists():
        count_of_followings = Followings.objects.get(user=targeted_user).followings.count()
    else:
        count_of_followings = 0

    # counting-followers
    if Followers.objects.filter(user=targeted_user).exists():
        count_of_followers = Followers.objects.get(user=targeted_user).followers.count()
    else:
        count_of_followers = 0
    
    #liked posts
    likesId = []
    if(request.user != None):
        likes = Likes.objects.all()
        for like in likes:
            if like.user.id == request.user.id:
                likesId.append(like.liked_post.id)
    
    # paginator
    paginator = Paginator(users_posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/profile.html", {
        "followers_count": count_of_followers,
        "followings_count": count_of_followings,
        "posts": users_posts,
        "likes": likesId,
        "page_obj": page_obj,
        "user": targeted_user,
        "isFollowing": isFollowing,
        "current_user": current_user
    })

@csrf_exempt
def edit(request, post_id):
    post = Posts.objects.get(pk=post_id)
    data = json.loads(request.body)
    if post.user == request.user and request.method == "PUT":
        post.content = data["content"]
        post.save()
        return HttpResponse(status=204)
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)

def following(request):
    all_posts = Posts.objects.all().order_by('id').reverse()
    current_user = request.user
    followings = Followings.objects.get(user=current_user).followings.all()
    posts = []
    for post in all_posts:
        for person in followings:
            if post.user == person:
                posts.append(post)


    paginator = Paginator(posts, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    likesId = []
    if(request.user != None):
        likes = Likes.objects.all()
        for like in likes:
            if like.user.id == request.user.id:
                likesId.append(like.liked_post.id)
    

    return render(request, "network/following.html", {
        "current_user": current_user,
        "page_obj": page_obj,
        "likes": likesId
    })