from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import random
from tagger import predict_and_list_labels

CONFIDENCE=0.6

def index(request):
    return render(request, 'index.html')

@csrf_exempt
def image2tag(request):
    if request.method == 'POST':
        try:
            # Parse JSON data
            data = json.loads(request.body)
            base64_image = data.get('image')
            file_name = data.get('fileName')
            if not base64_image:
                return JsonResponse({'error': 'No image data provided'}, status=400)

            # Tách tiền tố 'data:image/png;base64,' hoặc tương tự
            format, imgstr = base64_image.split(';base64,') 
            ext = format.split('/')[-1]  # Lấy định dạng tệp (jpg, png, ...)
            
            # Chuyển Base64 thành tệp
            image_data = ContentFile(base64.b64decode(imgstr), name=f'uploaded_image.{ext}')

            # Lưu tệp (ví dụ trong media folder)
            from django.core.files.storage import default_storage
            filename = default_storage.save(f'uploaded_images/{file_name}.{ext}', image_data)

            tags=predict_and_list_labels(f'uploaded_images/{file_name}.{ext}', confidence=CONFIDENCE)
            default_storage.delete(f'uploaded_images/{file_name}.{ext}')

            return JsonResponse({'tags': tags}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
