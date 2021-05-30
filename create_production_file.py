import getopt
import os
import subprocess
import sys
from pathlib import Path
import patoolib
import shutil


def read_production_config_file():
    name = "production.config"

    with open(name, "r") as file:
        lines = file.readlines()

    parameters = {}
    origin_destination_pairs = []
    for line in lines:
        if line == "\n":
            continue

        if line[0] == "#":
            continue

        try:
            parameter, value = line.strip().split("=")
            parameters[parameter] = value.strip('"')
            continue
        except ValueError:
            pass

        splits = line.split(" TO ")
        origin = splits[0].strip()
        if len(splits) == 1:
            destination_directory = ""
        else:
            destination_directory = splits[1].strip()

        origin_destination_pairs.append(
            dict(origin=origin, destination=destination_directory)
        )

    return origin_destination_pairs, parameters


def build_production_folder(production_folder, origin_destination_pairs):
    remove_production_folder()

    os.mkdir(production_folder)

    project_directory = os.getcwd()
    for pair in origin_destination_pairs:
        origin = os.path.join(project_directory, pair["origin"])
        destination_directory = f"{project_directory}/{production_folder}/{pair['destination']}"

        if not os.path.isdir(destination_directory):
            os.makedirs(destination_directory)

        if os.path.isdir(origin):
            print(f'Copy directory {pair["origin"]} to {production_folder}/{pair["destination"]}/{Path(origin).stem}')
            shutil.copytree(origin, f"{destination_directory}/{Path(origin).stem}")
        elif os.path.isfile(origin):
            print(f'Copy file {pair["origin"]} to {production_folder}/{pair["destination"]}/')
            shutil.copy(origin, destination_directory)


def add_to_compressed_file(production_folder="production_folder", file_name="production_file"):
    file_name = Path(file_name)
    if file_name.suffix == "":
        file_name = file_name.with_suffix(".rar")

    if os.path.isfile(file_name):
        os.remove(file_name)

    print(f"patoolib.create_archive({file_name}, ({production_folder},))")
    patoolib.create_archive(str(file_name), (production_folder,))


def remove_production_folder(production_folder="production_folder"):
    if os.path.isdir(production_folder):
        shutil.rmtree(production_folder)


def export_requirements():
    bashCommand = "poetry export -f requirements.txt --output requirements.txt"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def get_console_arguments(argv):
    try:
        opts, args = getopt.getopt(argv, "", ["folder=", "file="])
    except getopt.GetoptError:
        print("create_production_file --folder=production_folder --file=production_file")
        sys.exit(2)

    production_folder = None
    production_file = None
    for opt, arg in opts:
        if opt == '--folder':
            production_folder = arg
        elif opt == "--file":
            production_file = arg

    return production_folder, production_file


def main(argv):
    production_folder, production_file = get_console_arguments(argv)

    origin_destination_pairs, parameters = read_production_config_file()

    if production_folder is None:
        if "FOLDER" in parameters:
            production_folder = parameters["FOLDER"]
        else:
            production_folder = "production_folder"

    if production_file is None:
        if "FILE" in parameters:
            production_file = parameters["FILE"]
        else:
            production_file = "production_file"

    export_requirements()

    build_production_folder(production_folder=production_folder, origin_destination_pairs=origin_destination_pairs)
    add_to_compressed_file(production_folder=production_folder, file_name=production_file)
    remove_production_folder(production_folder=production_folder)


if __name__ == '__main__':
    main(sys.argv[1:])
