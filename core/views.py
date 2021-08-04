# Django
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages import get_messages
from django.core.mail import send_mail
from django.forms import modelformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.template import RequestContext
from django.urls import reverse
from django.views.generic.edit import FormView

# local Django
from .forms import (
    FileFieldForm,
    ImageForm, ImageFrameForm, 
    ImageRemoveBackgroundForm, ImageTrimForm, 
    NewUserForm, PostForm, 
    UpdateProfile, UploadFileForm,
)
from .image_processing_methods import (
    compress, trim,
    frame, convert_jpg_to_png, 
    remove_background
)
from .models import Images
from .utility import handle_uploaded_file


# Create your views here.
def homepage(
        request):
    return render(
        request, 
        'core/header.html', 
        {'title': 'header'})

@login_required
def update_profile_success(
        request):
    return render(
        request, 
        'core/update_profile_success.html', 
        {'title': 'update_profile_success'})

def register_request(
        request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        # print(form.is_valid())
        if form.is_valid():
            user = form.save(1)
            login(request, user)
            print("[+] user, type(user): {0}, {1}".format(user, type(user)))
            print("[+] dir(user): {0}".format(dir(user)))
            print("[+] user.EMAIL_FIELD: {0}".format(user.EMAIL_FIELD))
            print("[+] user.email: {0}".format(user.email))
            print("[+] user.email_user: {0}".format(user.email_user))
            send_mail(
                'Image Processing Web Registration Success', 
                'You have successfully registered!', 
                'huyvo.drive.1@gmail.com', 
                [user.email], 
                fail_silently=True)
            messages.success(
                request, 
                "Registration successful.")
            return redirect("core:homepage")
        messages.error(
            request, 
            "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(
        request=request, 
        template_name="core/register.html", 
        context={"register_form":form})

def login_request(
        request):
    if request.method == "POST":
        form = AuthenticationForm(
            request, 
            data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(
                username=username, 
                password=password)
            if user is not None:
                login(
                    request, 
                    user)
                messages.success(
                    request, 
                    f"You are now logged in as {username}.")
                ## Print messages
                # storage = get_messages(request)
                # for message in storage:
                #     print('[++] message: ', message)
                return redirect("core:homepage")
            else:
                messages.error(
                    request, 
                    "Invalid username or password.")
        else:
            messages.error(
                request, 
                "Invalid username or password.")

    form = AuthenticationForm()
    return render(
        request=request, 
        template_name="core/login.html", 
        context={"login_form":form})

@login_required
def logout_request(
        request):
    logout(request)
    messages.info(
        request, 
        "You have successfully logged out.")
    return redirect("core:homepage")

@login_required
def update_profile(
        request):
    args = {}

    if request.method == 'POST':
        print('[+] request.user: {0}'.format(request.user))
        form = UpdateProfile(
            request.POST, 
            instance=request.user, 
            user=request.user)
        print('[+] request.user: {0}'.format(request.user))
        form.actual_user = request.user
        print('[+] request.user: '.format(request.user))
        print('[+] form: '.format(form))
        if form.is_valid():
            form.save(1)
            return HttpResponseRedirect(
                reverse('core:update_profile_success'))
    else:
        form = UpdateProfile(
            instance=request.user, 
            user=request.user)

    args['form'] = form
    return render(
        request, 
        'core/update_profile.html', 
        context={"update_form":form})

@login_required
def image_upload_view(
        request):
    if request.method == 'POST':
        form = ImageForm(
            request.POST, 
            request.FILES)
        if form.is_valid():
            form.save()
            # Get the current instance object to display in the template
            img_obj = form.instance
            return render(
                request, 
                'core/index.html', 
                {'form': form, 'img_obj': img_obj})

    else:
        form = ImageForm()
    return render(
        request, 
        'core/index.html', 
        {'form': form})

@login_required
def post(
        request):
    ImageFormSet = modelformset_factory(Images,
                                        form=ImageForm,
                                        extra=3)
    print("[###] ImageFormSet, type(ImageFormSet): {0}, {1}".format(ImageFormSet, type(ImageFormSet)))
    
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        formset = ImageFormSet(
            request.POST, 
            request.FILES,
            queryset=Images.objects.none())
        for f in formset:
            form = f

        if (postForm.is_valid() and 
            formset.is_valid()):
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            # print('[+] formset: ', dir(formset))
            # print('[+] formset.data: ', formset.data)
            # print('[+] formset.files: ', formset.files)
            # print('[+] formset.cleaned_data: ', formset.cleaned_data)
            # images = formset.save(commit=False)
            # print('[+] images formset.save: ', images)

            # for form in formset.cleaned_data:
            #     print('[+] form: ', form)
            #     image = form['image']
            #     print('[++] image: ', image)
            #     # photo = Images(post=post_form, image=image)
            #     # photo.save()
            #     print('[+] request.FILES: ', request.FILES)
            #     files = request.FILES.getlist('image')
            #     print('[+] files', files)
            #     for f in files:
            #         photo = Images(post=post_form, image=f)
            #         photo.save()

            photos = [] 
            for key in formset.files:
                images = formset.files.getlist(key)
                for img in images:
                    print("[+] type(img): {0}".format(type(img)))
                    photo = Images(post=post_form, image=img)
                    print("[+] type(photo): {0}".format(type(photo)))
                    photos.append(photo)
                    photo.save()
            
            messages.success(request, "Posted!")
            #return HttpResponseRedirect("/")
            return render(
                request, 
                'core/index.html',
                {'postForm': postForm, 'formset': formset, 'img_obj': photos})
        else:
            print("[+] {0}, {1}".format(postForm.errors, formset.errors))
    else:
        postForm = PostForm()
        formset = ImageFormSet(queryset=Images.objects.none())

        return render(
            request, 
            'core/index.html',
            {'postForm': postForm, 'formset': formset})

@login_required
def remove_background_image(
        request):
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        form = ImageRemoveBackgroundForm(
            request.POST, 
            request.FILES)
        if (postForm.is_valid() and 
            form.is_valid()):
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()

            form.save(1)
            blur = form.cleaned_data['blur']
            canny_thresh_1 = form.cleaned_data['canny_thresh_1']
            canny_thresh_2 = form.cleaned_data['canny_thresh_2']
            mask_dilate_iter = form.cleaned_data['mask_dilate_iter']
            mask_erode_iter = form.cleaned_data['mask_erode_iter']
            mask_color_b = form.cleaned_data['mask_color_b']
            mask_color_g = form.cleaned_data['mask_color_g']
            mask_color_r = form.cleaned_data['mask_color_r']

            img_obj = form.instance
            img_obj.save()
            ori_img = img_obj.image
            new_img = remove_background(
                ori_img, blur, 
                canny_thresh_1, canny_thresh_2, 
                mask_dilate_iter, mask_erode_iter, 
                (mask_color_b, mask_color_g, mask_color_r))
            new_img_obj = Images(
                post=post_form, 
                image=new_img)
            new_img_obj.save()

            return render(
                request, 
                'core/preprocess_image.html', 
                {'postForm': postForm, 'form': form, 'img_obj': new_img_obj})
    else:
        postForm = PostForm(request.POST)
        form = ImageRemoveBackgroundForm()
    return render(
        request, 
        'core/preprocess_image.html', 
        {'postForm': postForm, 'form': form})