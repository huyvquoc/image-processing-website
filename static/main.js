console.log('hello world')
console.log('hello')

/*
To make the update code to work in web page, use Ctrl+F5 (this will bypass the cache).
If not, the page will load javascript file from the browser cache.

https://stackoverflow.com/questions/52682812/django-css-not-updating
*/

const alertBox = document.getElementById('alert-box')
const imageBox = document.getElementById('image-box')
const imageForm = document.getElementById('image-form')
console.log(imageForm)
const confirmBtn = document.getElementById('confirm-btn')
const input = document.getElementById('id_image') // Need to change id_file to id_image (due to the different name field in Images model)
console.log(input)
const csrf = document.getElementsByName('csrfmiddlewaretoken')

if(input){
  input.addEventListener('change', ()=>{
    console.log('changed')
    alertBox.innerHTML = ""
    confirmBtn.classList.remove('not-visible')

    const img_data = input.files[0]
    const url = URL.createObjectURL(img_data)
    imageBox.innerHTML = `<img src="${url}" id="image" width="300px">`

    /* Bring this code inside the addEventListener to see the cropper when uploading an image */
    const image = document.getElementById('image')
    var $image = $('#image');

    console.log('js', image)
    console.log('jquery', $image)

    $image.cropper({
      aspectRatio: 16 / 9, // can play around with this aspect ratio
      crop: function(event) {
        console.log(event.detail.x);
        console.log(event.detail.y);
        console.log(event.detail.width);
        console.log(event.detail.height);
        console.log(event.detail.rotate);
        console.log(event.detail.scaleX);
        console.log(event.detail.scaleY);
      }
    });

    // Get the Cropper.js instance after initialized
    var cropper = $image.data('cropper');

    confirmBtn.addEventListener('click', ()=>{
      cropper.getCroppedCanvas().toBlob((blob)=>{
        const fd = new FormData()
        fd.append('csrfmiddlewaretoken', csrf[0].value)
        fd.append('image', blob, 'my-image.png') // 'image' is the field name of the model Images 

        $.ajax({
          type: 'POST',
          url: imageForm.action,
          enctype: 'multipart/form-data',
          data: fd,
          success: function(response){
            console.log(response)
            alertBox.innerHTML = `<div class="alert alert-success" role="alert">
                                    Succesfully saved and cropped the selected image
                                  </div>`
          },
          error: function(error){
            console.log(error)
            alertBox.innerHTML = `<div class="alert alert-danger" role="alert">
                                    Oops ... something went wrong
                                  </div>`
          },
          cache: false,
          contentType: false,
          processData: false,
        })

      })
    })
  })
}
