# standard library
from io import BytesIO

# third-party
import PIL

# Django
from django.contrib.auth.models import User
from django.core.files import File
from django.db import models


# Create your models here.

class Image(
        models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    # Setting dynamic paths for the pictures is also possible
    image = models.ImageField(
        upload_to='users/%Y/%m/%d/', 
        blank=True)

    def __str__(self):
        return self.title

class Post(
        models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    body = models.CharField(max_length=400)

def get_image_filename(
        instance, 
        filename):
    idx = instance.post.id
    # print("[+] instance.post: ", instance.post)
    # print("[+] instance.title: ", instance.post.title)
    # print("[+] instance.images_set: ", instance.post.images_set)
    # print("[+] instance: ", dir(instance.post))
    # print('[+] post_images/%s.jpg'%(idx))
    return "post_images/%s.jpg" % (idx)

class Images(
    models.Model):
    post = models.ForeignKey(
        Post, null=True, 
        default=None,
        on_delete=models.CASCADE)
    # image = models.ImageField(upload_to=get_image_filename,
    #                           blank=True)
    image = models.ImageField(
        upload_to='post_images/%Y/',
        blank=True)

    # def __str__(self):
    #     return self.title
    def save(
            self, convert=0, 
            *args, **kwargs):
        if convert == 1:
            # print('[++] Convert!!!')
            if self.image:
                # print('[+++] Real convert')
                pil_img_obj = PIL.Image.open(self.image)
                im_io = BytesIO()
                pil_img_obj.save(im_io, 'PNG')
                # print('[++ self.image.name: ', self.image.name)
                # print('[++ self.image.name: ', type(self.image.name))
                self.image = File(
                    im_io, 
                    name=''.join([self.image.name.split('.')[0], '.png']))
        super(Images, self).save(*args, **kwargs)
