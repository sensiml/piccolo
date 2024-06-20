import pandas as pd
import os
import argparse
from os.path import basename
import fileinput
from collections import namedtuple
import shutil
from yaml import safe_load
import json


def _get_functions():

    yml_file_path = "/library/fixtures/functions_prod.yml"
    deploy_home = os.getenv("SENSIML_SERVER_DEPLOY_HOME")

    with open(deploy_home + yml_file_path, "r") as f:
        yml = safe_load(f)

    M = []
    for i in yml:
        M.append(i.pop("fields"))

    df = pd.DataFrame(M).fillna(False)

    df["module"] = df.path.apply(lambda x: basename(x)[:-2]) + df.function_in_file

    df["python_file"] = df.path.apply(lambda x: x.replace("/", ".")[:-2])

    return df


def parse_video_cell_ipynb_html(
    sml_docs_dir="_build", files_dir="application-tutorials"
):
    docs_dir = os.path.join(sml_docs_dir, files_dir)
    for f in os.listdir(docs_dir):
        M = []
        if "index" in f:
            continue
        if "edited" in f:
            continue
        if "ipynb" in f:
            continue

        with open(os.path.join(docs_dir, f), "r") as fid:
            input_cell_container = []
            div_counter = 0
            nbinput = False
            show_video = False

            for line in fid.readlines():

                if "INFO:tensorflow:Assets" in line:
                    continue

                if "nbinput docutils container" in line:
                    input_cell_container = []
                    div_counter = 0
                    nbinput = True

                if "show_video" in line:
                    show_video = True

                if nbinput and line.count("<div"):
                    div_counter += line.count("<div")
                if nbinput and line.count("</div"):
                    div_counter -= line.count("</div")

                if not nbinput:
                    M.append(line)

                if nbinput:
                    input_cell_container.append(line)
                    if div_counter == 0:
                        nbinput = False
                        if not show_video:
                            M.extend(input_cell_container)
                        else:
                            pass
                        show_video = False

        with open(os.path.join(docs_dir, f), "w") as out:
            for line in M:
                out.write(line)


def parse_notebook_files():

    build_directory = "_build"

    application_tutorials_directory = "application-tutorials"
    docs_dir = os.path.join(build_directory, application_tutorials_directory)
    for file_name in os.listdir(docs_dir):
        file_path = os.path.join(docs_dir, file_name)
        remove_empty_divs(file_path)

    notebooks_json = open("notebooks.json")
    notebooks = json.load(notebooks_json)

    for notebook in notebooks:
        notebook_repo_path = os.path.join(build_directory, notebook["notebook_path"])
        notebook_repo_path = notebook_repo_path.replace("ipynb", "html")
        remove_empty_divs(notebook_repo_path)


def remove_empty_divs(file_path):
    M = []
    remove_div = False

    with open(file_path, "r") as fid:
        for line in fid.readlines():
            if "prompt empty docutils container" in line:
                remove_div = True
                continue
            if remove_div and "</div>" in line:
                remove_div = False
                continue
            M.append(line)

        with open(file_path, "w") as out:
            for line in M:
                out.write(line)


def parse_html(docs_dir="_build/pipeline-functions"):
    func_df = _get_functions()
    print(func_df)

    for f in os.listdir(docs_dir):
        M = []
        if "index.rst" in docs_dir:
            continue
        with open(os.path.join(docs_dir, f), "r") as fid:
            for line in fid.readlines():
                if "library.core_functions" in line and "module-library" not in line:
                    for index, _ in enumerate(func_df.python_file.values):
                        if (
                            "library." + func_df.python_file.iloc[index] + "<" in line
                            and ">" + func_df.function_in_file.iloc[index] + "<" in line
                        ):
                            print("python_file", func_df.python_file.iloc[index])
                            print("func in file", func_df.function_in_file.iloc[index])
                            print("original", line, "\n")
                            line = '<code class="descclassname"></code><code class="descname">{0}</code></span><a class="headerlink" href="#{0}" ></a></dt>'.format(
                                func_df.name.iloc[index]
                            )
                            print("new", line, "\n")
                            continue

                M.append(line)

        with open(os.path.join(docs_dir, f), "w") as out:
            for line in M:
                out.write(line)


def find_and_replace(filename, word, replacement):
    with fileinput.FileInput(filename, inplace=True) as fid:
        for line in fid:
            print(line.replace(word, replacement), end="")

    # os.remove(filename+'.bak')


def convert_to_php(docs_dir="_build"):

    for f in os.listdir(docs_dir):
        if f[-4:] == "html":
            find_and_replace(
                os.path.join(docs_dir, f), 'href="genindex.html"', 'href="genindex.php"'
            )
            find_and_replace(
                os.path.join(docs_dir, f), 'href="index.html"', 'href="index.php"'
            )
            find_and_replace(
                os.path.join(docs_dir, f), 'href="search.html"', 'href="search.php"'
            )
            find_and_replace(
                os.path.join(docs_dir, f),
                'href="py-modindex.html"',
                'href="py-modindex.php"',
            )

            os.rename(os.path.join(docs_dir, f), os.path.join(docs_dir, f[:-4] + "php"))

    import time

    time.sleep(1)
    for root, _, files in os.walk(docs_dir):
        for f in files:
            if f[-4:] != "html" and f[-3:] != "php":
                continue
            find_and_replace(os.path.join(root, f), "../index.html", "../index.php")
            find_and_replace(os.path.join(root, f), "../search.html", "../search.php")
            find_and_replace(
                os.path.join(root, f), "../genindex.html", "../genindex.php"
            )
            find_and_replace(
                os.path.join(root, f), "../py-modindex.html", "../py-modindex.php"
            )

    find_and_replace(os.path.join(docs_dir, "index.php"), "search.html", "search.php")


def update_search_javascript(docs_dir="_build"):
    output = []
    with open(os.path.join(docs_dir, "search.html"), "r") as fid:
        for line in fid.readlines():
            output.append(line)
            if "<title>Search &mdash;" in line:
                output.append(
                    "<script>if (typeof module === 'object') {window.module = module; module = undefined;}</script>"
                )
            if '<script type="text/javascript" src="_static/js/theme.js">' in line:
                output.append(
                    "<script>if (window.module) module = window.module;</script>"
                )

    with open(os.path.join(docs_dir, "search.html"), "w") as out:
        out.writelines(output)


def main():
    parser = argparse.ArgumentParser(
        description="Parse sphinx output files to replace server names"
    )

    parser.add_argument("-p, --php", dest="php", help="Convert to PHP format.")

    input_args = parser.parse_args()

    update_search_javascript()

    parse_html()
    parse_video_cell_ipynb_html()
    parse_notebook_files()
    shutil.rmtree("_build/_sources")

    if input_args.php:
        convert_to_php()


if __name__ == "__main__":
    main()
