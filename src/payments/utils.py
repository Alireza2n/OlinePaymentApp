import datetime


def generate_a_random_string() -> str:
    """
    Generates a pseudo-random string
    """
    almost_random_number = datetime.datetime.now().strftime('%Y%d%S%Z')
    return f'ORDER-{almost_random_number}'
