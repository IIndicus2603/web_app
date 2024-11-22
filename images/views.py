import json
import os
import time
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from .models import Image
from .forms import ImageForm
from django.db import connections
import logging
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


logger = logging.getLogger(__name__)

@csrf_exempt
def wait_and_notify(request):
    # Check for AJAX request using X-Requested-With header
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Immediately notify the client that the loading process has started
        response = {'loading': True}
        
        # Simulate the wait (5 seconds in your original code)
        time.sleep(5)
        
        # Return response after "waiting"
        response = {'loading': False}
        return JsonResponse(response)
    
    # If it's not an AJAX request, return a default response
    return JsonResponse({'loading': False})

@csrf_exempt
def image_upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        form = ImageForm(request.POST, request.FILES)
        wait_and_notify(request)  # Notify loading status

        if form.is_valid():
            image_instance = form.save(commit=False)
            # Get the file name
            file_name = os.path.basename(image_instance.image.name)
            with default_storage.open(file_name, 'wb') as f:
                f.write(image_instance.image.read())
            # Load the tag.json file
            tag_file_path = os.path.join(settings.BASE_DIR, 'tag.json')
            tags = []
            try:
                with open(tag_file_path, 'r') as f:
                    tag_data = json.load(f)
                    tags = tag_data.get(file_name, [])
            except (FileNotFoundError, json.JSONDecodeError):
                pass  # Optionally log an error message

            # Assign tags using set_tags method
            image_instance.set_tags(tags)

            # Save the instance
            image_instance.save()

            # Return JSON response
            return JsonResponse({'image_url': image_instance.image.url, 'tags': image_instance.get_tags()})

    # Initialize empty form and fetch all images
    form = ImageForm()
    images = Image.objects.all()
    return render(request, 'images/index.html', {'form': form, 'images': images})

@csrf_exempt
def get_image_tags(request):
    if request.method == "GET":
        image_name = request.GET.get("image_name", "")
        try:
            # Lấy ảnh theo tên file
            image = Image.objects.filter(image__icontains=image_name).first()
            if image:
                return JsonResponse({"tags": image.get_tags()}, status=200)
            else:
                return JsonResponse({"tags": []}, status=404)
        except Exception as e:
            return JsonResponse({"tags": [], "error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def image_slider(request):
    # Fetch images and their associated tags from the database
    images = Image.objects.all()  # Adjust according to your model
    return render(request, 'index.html', {'images': images})

@csrf_exempt
def image_check_duplicate(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        
        # Check if file already exists in the database
        exists = Image.objects.filter(image__icontains=file_name).exists()
        
        return JsonResponse({'exists': exists})

@csrf_exempt
def update_tag(request):
    if request.method == 'POST':
        tag_file_path = os.path.join(settings.BASE_DIR, 'tag.json')

        image_path = request.POST.get('image_name')  # Image name
        old_tag = request.POST.get('old_tag')        # Old tag
        new_tag = request.POST.get('new_tag')        # New tag
        image_name = os.path.basename(image_path)
        image_instance = Image.objects.filter(image__icontains=image_name).first()

        if not (image_name and old_tag and new_tag):
            return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)

        # Read the tag.json file
        try:
            with open(tag_file_path, 'r', encoding='utf-8') as file:
                tags = json.load(file)
        except FileNotFoundError:
            return JsonResponse({'success': False, 'error': 'tag.json file not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in tag.json'}, status=500)

        # Check if the image exists in the tag data
        if image_name not in tags:
            return JsonResponse({'success': False, 'error': 'No tags found for this image in tag.json'}, status=400)

        # Check if old_tag exists in the image's tags
        if old_tag in tags[image_name] and new_tag not in tags[image_name] or new_tag == old_tag:
            tags[image_name] = [new_tag if tag == old_tag else tag for tag in tags[image_name]]
            image_instance.set_tags(tags[image_name])  # Update the tags field
            image_instance.save()
            # Save the updated tags to tag.json
            try:
                with open(tag_file_path, 'w', encoding='utf-8') as file:
                    json.dump(tags, file, ensure_ascii=False, indent=4)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

            return JsonResponse({'success': True, 'tags': tags[image_name]})
        else:
            return JsonResponse({'success': False, 'error': 'Tag already exists'}, status=400)

    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def add_tag(request):
    if request.method == 'POST':
        image_name = request.POST.get('image_name')  # Tên ảnh
        new_tag = request.POST.get('new_tag')       # Tag mới
        if not image_name or not new_tag:
            return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)
        image_name = os.path.basename(image_name)
        image_instance = Image.objects.filter(image__icontains=image_name).first()     

        # Đường dẫn tới file tag.json
        tag_file_path = os.path.join(settings.BASE_DIR, 'tag.json')

        try:
            # Đọc tag.json
            with open(tag_file_path, 'r', encoding='utf-8') as f:
                tags = json.load(f)
        except FileNotFoundError:
            return JsonResponse({'success': False, 'error': 'tag.json not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in tag.json'}, status=500)

        # Lấy tên file ảnh (chỉ lấy phần tên file, không lấy đường dẫn)

        # Thêm tag mới vào danh sách tag của ảnh
        if image_name not in tags:
            tags[image_name] = []
        if new_tag not in tags[image_name]:
            tags[image_name].append(new_tag)
            image_instance.set_tags(tags[image_name])  # Update the tags field
            image_instance.save()

            # Ghi lại file tag.json
            try:
                with open(tag_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags, f, ensure_ascii=False, indent=4)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

            return JsonResponse({'success': True, 'tags': tags[image_name]})

        return JsonResponse({'success': False, 'error': 'Tag already exists'}, status=400)

    return JsonResponse({'success': False}, status=400)

@csrf_exempt
def delete_tag(request):
    if request.method == 'POST':
        image_name = request.POST.get('image_name')  # Tên ảnh
        current_tag = request.POST.get('current_tag')  # Tag cần xóa
        if not image_name or not current_tag:
            return JsonResponse({'success': False, 'error': 'Missing data'}, status=400)

        # Đường dẫn tới file tag.json
        tag_file_path = os.path.join(settings.BASE_DIR, 'tag.json')

        try:
            # Đọc tag.json
            with open(tag_file_path, 'r', encoding='utf-8') as f:
                tags = json.load(f)
        except FileNotFoundError:
            return JsonResponse({'success': False, 'error': 'tag.json not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in tag.json'}, status=500)

        # Lấy tên file ảnh (chỉ lấy phần tên file, không lấy đường dẫn)
        image_name = os.path.basename(image_name)
        image_instance = Image.objects.filter(image__icontains=image_name).first()
        # Kiểm tra và xóa tag khỏi danh sách tag của ảnh
        if image_name in tags and current_tag in tags[image_name]:
            tags[image_name].remove(current_tag)
            image_instance.set_tags(tags[image_name])  # Update the tags field
            image_instance.save()
            # Nếu danh sách tag rỗng, có thể xóa luôn mục ảnh (nếu cần)
            if not tags[image_name]:
                del tags[image_name]

            # Ghi lại file tag.json
            try:
                with open(tag_file_path, 'w', encoding='utf-8') as f:
                    json.dump(tags, f, ensure_ascii=False, indent=4)
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=500)

            return JsonResponse({'success': True, 'tags': tags.get(image_name, [])})

        return JsonResponse({'success': False, 'error': 'Tag not found or image not found'}, status=400)

    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def cleanup(request):
    # Kiểm tra phương thức
    if request.method == 'POST':
        logger.debug("Cleanup started")
    
    # Close all database connections to avoid locking issues
        logger.debug("Closing all database connections")
        # Xóa các file trong thư mục images
        images_dir = os.path.join(settings.BASE_DIR, 'media', 'images')
        for file_name in os.listdir(images_dir):
            file_path = os.path.join(images_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        connections.close_all()

    # Connect to the SQLite database
        db_file = os.path.join(settings.BASE_DIR,'db.sqlite3')

        with connections['default'].cursor() as cursor:
            # Clear all data from all tables in the database
            cursor.execute("PRAGMA foreign_keys=off;")  # Disable foreign key checks temporarily
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Loop through each table and delete all records
            for table in tables:
                table_name = table[0]
                logger.debug(f"Clearing data from table: {table_name}")
                cursor.execute(f"DELETE FROM {table_name};")

            cursor.execute("PRAGMA foreign_keys=on;")  # Enable foreign key checks again

    return JsonResponse({'message': 'Cleanup completed'}, status=200)


# upload nhiều ảnh, sửa giao diện, 
