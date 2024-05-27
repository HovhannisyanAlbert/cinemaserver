from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Room, Movie, Seat
import json
from django.shortcuts import get_object_or_404
import base64
from django.core.files.base import ContentFile
from .untill import delete_image, delete_all_images_room
from datetime import datetime


@csrf_exempt
def rooms(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name")
            if not name:
                return JsonResponse({"error": "Room name is required"}, status=400)
            Room.objects.create(name=name)
            return JsonResponse({"message": f"Room {name} created successfully"}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Something wrong"}, status=500)
    elif request.method == "GET":
        try:
            rooms = Room.objects.all().values("id", "name")
            rooms_list = list(rooms)
            return JsonResponse({"data": rooms_list})
        except Exception as e:
            return JsonResponse({"error": "Something wrong"}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def room(request, room_id):

    if request.method == "DELETE":
        try:
            room = Room.objects.get(pk=room_id)

            if room:
                name = room.name
                room.delete()

                delete_image(room_id)
                delete_all_images_room(room_id)
                rooms = Room.objects.all().values('id', 'name',)
                rooms_list = list(rooms)
                return JsonResponse({
                    "message": f"{name} successfully deleted",
                    "data": list(rooms_list)
                }, status=200)

            else:
                return JsonResponse({"error": "Room not found"}, status=404)
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": "Something wrong"}, status=500)
    elif request.method == "PUT":
        try:
            room = get_object_or_404(Room, pk=room_id)
            data = json.loads(request.body)
            name = data.get("name")

            if not name:
                return JsonResponse({"error": "Name field is required"}, status=400)

            room.name = name
            room.save()

            rooms = Room.objects.filter(pk=room_id).values('id', 'name')
            rooms_list = list(rooms)

            return JsonResponse({"message": f"Room {name} successfully edited", "data": rooms_list})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)


@csrf_exempt
def movie(request, room_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image = data.get("image")
            title = data.get("title")
            image_binary_data = base64.b64decode(image)
            image_content = ContentFile(
                image_binary_data, name=f'{room_id}.png')

            start_time_str = data.get("start_time")
            start_month = datetime.fromisoformat(start_time_str).month
            start_time = datetime.fromisoformat(start_time_str).time()
            start_time_day = datetime.fromisoformat(start_time_str).day
            start_time_seconds = start_time.hour * 3600 + \
                start_time.minute * 60 + start_time.second

            room = Room.objects.get(pk=room_id)
            movies = Movie.objects.filter(room=room)
            movies_list_start_time = list(movies.values("start_time"))

            if len(movies_list_start_time) == 0:
                Movie.objects.create(
                    title=title, movie_image=image_content, room=room, start_time=start_time_str)
                return JsonResponse({"e": "succesfully"})
            else:
                for movie in movies_list_start_time:
                    start_time_datetime = str(movie['start_time'])
                    DB_start_month = datetime.fromisoformat(
                        start_time_datetime).month
                    DB_start_time = datetime.fromisoformat(
                        start_time_datetime).time()
                    DB_start_time_day = datetime.fromisoformat(
                        start_time_datetime).day
                    DB_start_time_seconds = DB_start_time.hour * 3600 + \
                        DB_start_time.minute * 60 + DB_start_time.second

                    total_time_difference = abs(start_time_seconds - DB_start_time_seconds) + (
                        86400 * abs(start_time_day - DB_start_time_day))

                    if start_month == DB_start_month and DB_start_time_day == start_time_day and total_time_difference < 3600:
                        return JsonResponse({"error": "You cannot add two movies at the same time"}, status=405)

                Movie.objects.create(
                    title=title, movie_image=image_content, room=room, start_time=start_time_str)

                return JsonResponse({"success": f"{title} is Created"})

        except Exception as e:
            return JsonResponse({"error": str(e)})

    elif request.method == "DELETE":
        try:
            data = json.loads(request.body)
            room = Room.objects.filter(id=room_id).first()
            image_url = data.get("url_image")
            if room:
                movie_id = data.get("movieId")
                movie_candidate = Movie.objects.filter(
                    id=movie_id, room=room).first()

                if movie_candidate:
                    movie_title = movie_candidate.title
                    delete_image(image_url)
                    movie_candidate.delete()

                    room = Room.objects.get(pk=room_id)
                    movies = Movie.objects.filter(room=room)

                    movie_list = list(movies.values())

                    return JsonResponse({"success": f"Movie '{movie_title}' successfully deleted", "data": movie_list})
                else:
                    return JsonResponse({"error": "Movie not found"}, status=404)
            else:
                return JsonResponse({"error": "Room not found"}, status=404)

        except Exception as e:
            return JsonResponse({"error": f"An error occurred:'Something wrong'"}, status=500)
    elif request.method == "PUT":
        try:
            data = json.loads(request.body)
            room_exists = Room.objects.filter(id=room_id).exists()

            if room_exists:
                new_title = data.get("title")
                image = data.get("image")
                movie_id = data.get("movieId")

                try:
                    movie_candidate = Movie.objects.get(pk=movie_id)
                except Movie.DoesNotExist:
                    return JsonResponse({"error": "No Movie matches the given query."}, status=404)

                if new_title:
                    movie_candidate.title = new_title

                if image:
                    movie_candidate.film_poster = f"film_poster/{room_id}.png"

                movie_candidate.save()

                return JsonResponse({"success": "Movie successfully edited"})
            else:
                return JsonResponse({"error": "Room not found"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"An error occurred:'Something wrong'"}, status=500)
    elif request.method == "GET":

        try:

            room = Room.objects.get(pk=room_id)
            movies = Movie.objects.filter(room=room)

            movie_list = list(movies.values())

            return JsonResponse({"data": movie_list})
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room_id not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": "Movie not fount"}, status=500)


def get_seat(request, movie_id):

    if request.method == "GET":
        try:

            movie = get_object_or_404(Movie, pk=movie_id)

            seats = Seat.objects.filter(movie=movie).values(
                "id", "row", "column", "movie_id", "is_booked")
            seat_list = list(seats)

            return JsonResponse({"data": seat_list}, status=200)
        except Movie.DoesNotExist:
            return JsonResponse({"error": "Movie not found"}, status=404)
        except Room.DoesNotExist:
            return JsonResponse({"error": "Room not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def seat(request, movie_id):
    if request.method == "POST":
        data = json.loads(request.body)
        data_list = data.get("data")
        movie = get_object_or_404(Movie, pk=movie_id)
        room = get_object_or_404(Room, pk=movie.room_id)

        for data in data_list:
            seat = Seat.objects.filter(
                row=data["row"], movie=movie, column=data["column"]).first()
            if seat:
                if seat.is_booked:
                    return JsonResponse({"err": "Seat is already booked"}, status=400)
                else:
                    seat.is_booked = True
                    seat.save()

            else:
                new_seat = Seat.objects.create(
                    room=room, movie=movie, column=data["column"], row=data["row"], is_booked=True)

        seats = Seat.objects.filter(movie=movie).values(
            "id", "row", "column", "movie_id", "is_booked")
        seat_list = list(seats)

        return JsonResponse({"success": "Seats booked successfully", "data": seat_list})

    else:
        return JsonResponse({"err": "Invalid request method"}, status=405)
