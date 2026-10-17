
def cateofies(request):
    categories = [
        "Technology",
        "Science",
        "Health",
        "Travel",
        "Food",
    ]
    return {'categories': categories}