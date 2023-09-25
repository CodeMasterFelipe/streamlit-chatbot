import os

LOCATION = "/Volumes/Extreme Pro/dev/streamlit-chatbot/ai_workspace/"


def create_file(filename: str):
    """
    Create a new file.

    Parameters:
    - filename (str): Name of the file to be created.
    - location (str): Directory where the file should be created. Default is the current directory.

    Returns:
    - str: Message indicating success or failure.
    """
    # Combine the directory path and filename
    file_path = os.path.join(LOCATION, filename)

    # Check if file already exists
    if os.path.exists(file_path):
        return f"File '{filename}' already exists in '{LOCATION}'."

    # Create the file
    with open(file_path, 'w') as file:
        pass

    return f"File '{filename}' has been created in '{LOCATION}'."


def write_to_file(filename: str, content: str, mode: str = "w"):
    """
    Write data to a file.

    Parameters:
    - filename (str): Name of the file to write to.
    - content (str): Content to write to the file.
    - mode (str): Mode in which the file should be opened. Default is 'w' (write). Use 'a' for append.

    Returns:
    - str: Message indicating success or failure.
    """
    # Check if mode is valid
    if mode not in ["w", "a"]:
        return "Invalid mode. Use 'w' for write or 'a' for append."

    # Combine the directory path and filename
    file_path = os.path.join(LOCATION, filename)

    # Write to the file
    try:
        with open(file_path, mode) as file:
            file.write(content)
        return f"Content has been written to '{file_path}'."
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"


def read_file_content(filename):
    """
    Read the content of a file.

    Parameters:
    - filename (str): Name of the file to read.

    Returns:
    - str: Content of the file or an error message.
    """
    file_path = os.path.join(LOCATION, filename)
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return f"File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage:
# content = read_file_content("sample.txt")
# print(content)


# Example usage:
# create_file("sample.txt")
# write_to_file("sample.txt", "Hello, World!")
