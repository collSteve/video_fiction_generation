def fic_exists_by_url(url, file_name):
    with open(file_name, 'r') as file:
        for line in file:
            if url in line:
                return True
    return False
