import os
import shutil
from pathlib import Path
from zipfile import ZipFile
import json


def main():

    DATA_DIRECTORY = "data"
    IMAGE_DIRECTORY = "img"
    current_directory = os.path.dirname(__file__)
    source_directory = os.path.join(os.path.dirname(__file__), "source")
    build_path = os.path.join(current_directory, "_build", "_static", "file")

    renamed_notebooks = []
    data_files = []
    image_files = []

    try:
        notebooks_json = open("notebooks.json")
        data = json.load(notebooks_json)

        for notebook in data:
            notebook_repo_path = os.path.join(
                source_directory, notebook["notebook_path"]
            )
            path = Path(notebook_repo_path)

            zip_notebook_path = os.path.join(build_path, path.stem + ".zip")
            with ZipFile(zip_notebook_path, "w") as zipfile:
                print("Zipping Notebook: " + path.name)

                ## Rename the notebook file to the JSON name
                new_notebook_name = notebook["name"]
                new_path = os.path.join(build_path, new_notebook_name)
                shutil.copy(notebook_repo_path, new_path)

                zipfile.write(new_path, arcname=new_path.split(build_path)[1])
                renamed_notebooks.append(new_path)

                if "data_files" in notebook:
                    for data_path in notebook["data_files"]:
                        data_repo_path = os.path.join(source_directory, data_path)
                        relocate_zip_file(
                            DATA_DIRECTORY, build_path, data_repo_path, zipfile
                        )
                        data_files.append(data_repo_path)

                if "image_files" in notebook:
                    for image_path in notebook["image_files"]:
                        image_repo_path = os.path.join(source_directory, image_path)
                        relocate_zip_file(
                            IMAGE_DIRECTORY, build_path, image_repo_path, zipfile
                        )
                        image_files.append(image_repo_path)

        zip_all_notebooks_path = os.path.join(build_path, "notebook-tutorials.zip")
        with ZipFile(zip_all_notebooks_path, "w") as zipfile:
            for notebook_path in renamed_notebooks:
                zipfile.write(notebook_path, arcname=notebook_path.split(build_path)[1])
            for data_repo_path in data_files:
                relocate_zip_file(DATA_DIRECTORY, build_path, data_repo_path, zipfile)
            for image_repo_path in image_files:
                relocate_zip_file(IMAGE_DIRECTORY, build_path, image_repo_path, zipfile)

    except Exception as e:
        print("----------------------------")
        print(e)
        print("----------------------------")
        print("Could not zip notebook files")
        print("----------------------------")
        raise (e)
    finally:
        ##Cleanup all renamed notebooks
        for notebook_file_path in renamed_notebooks:
            os.remove(notebook_file_path)


def relocate_zip_file(directory, build_path, repo_path, zipfile):
    path = Path(repo_path)
    new_path = os.path.join(build_path, directory, path.name)
    zipfile.write(path, arcname=new_path.split(build_path)[1])


if __name__ == "__main__":
    main()
