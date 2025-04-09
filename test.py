class films:
    name = 'The Godfather'
    year = 1972
    director = 'Francis Ford Coppola'
    genre = 'Crime'
    rating = 9.2

class actors:
    name = 'Marlon Brando'
    age = 80


query = {
    'films':{
        'name','year','director','genre','rating'
    },
    'actors':{
        'name','age'
    }

}