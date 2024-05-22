import os
import random

import aiofiles
from werkzeug.utils import secure_filename


async def save_photo(is_created, form, model, folder, field_photo=None, folder_dop=None):
    if not field_photo or not form.get(field_photo):
        return None

    file_data = form.get(field_photo)
    if not file_data or not file_data.filename:
        return None

    filename = secure_filename(file_data.filename)
    random_folder = str(random.randint(99999, 999999))
    directory = os.path.join('static', 'img', folder, random_folder, folder_dop or '')

    if not os.path.exists(directory):
        os.makedirs(directory)

    if is_created:
        print('is_created:', is_created)
        file_path = os.path.join(directory, filename)
    elif model.id:
        current_photo_path = getattr(model, field_photo, None)
        if current_photo_path:
            last_slash_index = current_photo_path.rfind('/')
            file_path = os.path.join(current_photo_path[:last_slash_index + 1], filename)
        else:
            file_path = os.path.join(directory, filename)
    else:
        file_path = os.path.join(directory, filename)

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file_data.read()
        await f.write(content)

    setattr(model, field_photo, file_path)
    form[field_photo] = file_path
    return file_path
