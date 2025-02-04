def cut_spaces(name):
    reversed_name = name[::-1]
    for i in range(len(name)):
        if reversed_name[i] != ' ':
            reversed_name = reversed_name[i:]
            return reversed_name[::-1]
    return name
