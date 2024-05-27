from os import path, remove
import glob


def delete_image(image_url):
    directory_path = path.abspath('./media/movie_image')
    file_name = f"{image_url}.png"
    file_path = path.join(directory_path, file_name)
    if path.exists(file_path):
        remove(file_path)
    else:
        print(f"File '{file_name}' does not exist in the directory.")


def delete_all_images_room(room_id):
    directory_path = path.abspath('./media/movie_image')

    pattern = path.join(directory_path, f'{room_id}*')

    files_to_delete = glob.glob(pattern)

    for file_path in files_to_delete:
        try:
            remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: Something wrong")
