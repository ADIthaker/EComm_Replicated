
def replicated(func):
    #features of a single group member
    
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper