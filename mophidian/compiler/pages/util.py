from os import path

def normpath(path_: str) -> str:
    """Normalize the path and make it alwasy have forward slash."""
    return path.normpath(path_).replace("\\", "/")


def create_uri(parent_: str, name_: str) -> str:
    """Takes the parent path and the name of the file and returns the uri.

    Args:
        parent_ (str): The parent path of the file
        name_ (str): The file name

    Returns:
        str: The normalized combination of the parent and the name
    """
    return normpath(path.join(parent_, name_))


def splitall(path: str) -> list[str]:
    path = normpath(path)
    return path.split('/')