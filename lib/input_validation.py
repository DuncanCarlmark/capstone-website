import pandas as pd

def check_for_empty_fields(age, artist, genre_input):
    if not age or not artist or (len(genre_input[0]) + len(genre_input[1]) + len(genre_input[2]) == 0):
        return True
    else:
        return False

def define_genre_input(genre_input, genres_list):
    valid_genres = []
    invalid_genres = []
    # Check each genre entry
    for i in range(len(genre_input)):
        
        if len(genre_input[i]) > 0 and any(genres_list.isin([genre_input[i]])):
            valid_genres.append(genre_input[i])
        else:
            if len(genre_input[i]) > 0:
                invalid_genres.append("Genre " + str(i + 1))
    return valid_genres, invalid_genres

def check_age_is_int(age):
    try:
        int(age)
        return True
    except:
        return False