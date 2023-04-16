import argparse
import subprocess
import sys
import json
import re
from pathlib import Path
from urllib.request import urlopen
from typing import List


def port_exists(port_name: str) -> bool:
    return (Path("ports") / port_name).exists()


def check_port_name_validity(port_name: str) -> bool:
    return re.compile("^[a-z0-9]+(-[a-z0-9]+)*$").match(port_name)


def git(args: List, working_dir: str = None) -> str:
    print(f"git {' '.join(args)}")
    return subprocess.run(
        ["git"] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=working_dir,
    ).stdout


def get_git_tree_sha(port_name):
    return git(['rev-parse', f'HEAD:ports/{port_name}']).strip()


def get_github_repo_info(username: str, repo_name: str) -> dict:
    api_url = f"https://api.github.com/repos/{username}/{repo_name}"
    print(f"GET {api_url}")
    response = urlopen(api_url)
    return json.loads(response.read().decode("utf-8"))


def get_github_latest_commit_info(github_user: str, github_repo: str, ref: str) -> dict:
    repo_url = f"https://github.com/{github_user}/{github_repo}"
    api_url = repo_url.replace(
        'github.com', 'api.github.com/repos') + f"/commits/{ref or 'main'}"
    print(f"GET {api_url}")
    response = urlopen(api_url)
    return json.loads(response.read().decode('utf-8'))


def create_portfile_contents_vcpkg_from_git(port_name: str, library_name: str, github_user: str, github_repo: str, ref: str) -> str:
    return f"""vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/{github_user}/{github_repo}.git
    REF {ref}
)

vcpkg_cmake_configure(
    SOURCE_PATH ${{SOURCE_PATH}}
)

vcpkg_cmake_install()

file(INSTALL ${{SOURCE_PATH}}/LICENSE DESTINATION ${{CURRENT_PACKAGES_DIR}}/share/${{PORT}} RENAME copyright)

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/{library_name})
"""


def create_portfile_contents_download_latest(port_name: str, library_name: str, github_user: str, github_repo: str, ref: str) -> str:
    return f"""file(DOWNLOAD "https://api.github.com/repos/{github_user}/{github_repo}/tarball/{ref or 'main'}" ${{DOWNLOADS}}/archive.tar.gz
    SHOW_PROGRESS
)

vcpkg_extract_source_archive(
    SOURCE_PATH
    ARCHIVE ${{DOWNLOADS}}/archive.tar.gz
)

vcpkg_cmake_configure(
    SOURCE_PATH ${{SOURCE_PATH}}
)

vcpkg_cmake_install()

file(INSTALL ${{SOURCE_PATH}}/LICENSE DESTINATION ${{CURRENT_PACKAGES_DIR}}/share/${{PORT}} RENAME copyright)

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/{library_name})
"""


def create_portfile_contents(port_name: str, library_name: str, github_user: str, github_repo: str, latest: bool, ref: str) -> str:
    if latest:
        return create_portfile_contents_download_latest(port_name, library_name, github_user, github_repo, ref)
    else:
        return create_portfile_contents_vcpkg_from_git(port_name, library_name, github_user, github_repo, ref)


def create_vcpkg_json_dict(port_name: str, port_description: str, github_user: str, github_repo: str, version_string: str, dependencies: List) -> dict:
    vcpkg_json = {
        "name": port_name,
        "version-string": version_string,
        "description": port_description,
        "dependencies": [
            {"name": "vcpkg-cmake", "host": True},
            {"name": "vcpkg-cmake-config", "host": True},
        ]
    }
    return vcpkg_json


def add_port(port_name: str, library_name: str, github_user: str, github_repo: str, latest: bool, ref: str, dependencies: List) -> None:
    if port_exists(port_name):
        print(f"Port {port_name} already exists.")
        sys.exit(1)

    if not check_port_name_validity(port_name):
        print(f"Invalid port name: {port_name}")
        sys.exit(1)

    print(f"Adding port '{port_name}'")

    if not library_name:
        # Helpful convention:
        # if port_name ends with -latest, make the library_name the port_name without -latest
        if latest and port_name.endswith("-latest"):
            library_name = port_name[:-7]
        else:
            library_name = port_name

    # Get repository information
    repo_info = get_github_repo_info(github_user, github_repo)
    repo_description = repo_info["description"]

    # Get commit info from either the ref or the latest commit
    latest_commit_info = get_github_latest_commit_info(
        github_user, github_repo, ref)
    latest_commit_date = latest_commit_info["commit"]["committer"]["date"][:10]
    latest_commit_sha = latest_commit_info["sha"]

    if not latest and not ref:
        ref = latest_commit_sha

    # Create the port directory
    ports_dir = Path("ports")
    port_dir = ports_dir / port_name
    port_dir.mkdir(exist_ok=True, parents=True)

    # Create the version directory
    versions_dir = Path("versions")
    version_dir = versions_dir / f"{port_name[0].lower()}-"
    version_dir.mkdir(exist_ok=True, parents=True)

    # Create the portfile.cmake
    portfile_contents = create_portfile_contents(
        port_name, library_name, github_user, github_repo, latest, ref)
    with open(port_dir / "portfile.cmake", "w") as f:
        f.write(portfile_contents)

    # Create the vcpkg.json
    version_string = f"{latest_commit_date}-{latest_commit_sha[:7]}"
    vcpkg_json_dict = create_vcpkg_json_dict(
        port_name, repo_description, github_user, github_repo, version_string, dependencies)
    vcpkg_json_path = port_dir / "vcpkg.json"
    print(f"Writing {vcpkg_json_path}")
    with open(vcpkg_json_path, "w") as f:
        json.dump(vcpkg_json_dict, f, indent=2)

    # Add the port to git
    git(["add", "ports"])
    git(["commit", "-m", f"Add new port {port_name}"])
    git_tree_sha = get_git_tree_sha(port_name)

    # Create the versions/*-/port-name.json file
    version_json = {
        "versions": [
            {
                "version-string": version_string,
                "git-tree": git_tree_sha
            }
        ]
    }
    version_file_path = version_dir / f"{port_name}.json"
    print(f"Writing {version_file_path}")
    with open(version_file_path, "w") as f:
        json.dump(version_json, f, indent=2)

    # Add the port to the baseline versions
    baseline_path = versions_dir / "baseline.json"
    baseline_data = {"default": {}}
    if baseline_path.exists():
        with open(baseline_path, "r") as f:
            baseline_data = json.load(f)
    baseline_data["default"][port_name] = {
        "baseline": version_string,
        "port-version": 0
    }
    print(f"Writing {baseline_path}")
    with open(baseline_path, "w") as f:
        json.dump(baseline_data, f, indent=2)

    # Add and commit all the things
    git(["add", "versions"])
    git(["commit", "--amend", "--no-edit"])

    print(f"Successfully added port '{port_name}'")


def list_ports() -> None:
    ports_path = Path("ports")
    if not ports_path.exists():
        print("No ports found.")
        return
    for port_dir in ports_path.iterdir():
        if port_dir.is_dir():
            port_name = port_dir.name
            vcpkg_json_path = port_dir / "vcpkg.json"
            with open(vcpkg_json_path, "r") as f:
                vcpkg_json_data = json.load(f)
            version_string = vcpkg_json_data["version-string"]
            print(f"{port_name} ({version_string})")


def remove_port(port_name: str) -> None:
    git(["rm", "-r", f"ports/{port_name}"])
    versions_path = Path("versions") / \
        port_name[0].lower() / f"{port_name}.json"
    git(["rm", str(versions_path)])
    with open("versions/baseline.json", "r") as f:
        baseline_data = json.load(f)
    del baseline_data[port_name]
    with open("versions/baseline.json", "w") as f:
        json.dump(baseline_data, f, indent=2)
    git(["add", "versions/baseline.json"])
    git(["commit", "-m", f"Remove {port_name}"])
    print(f"Port {port_name} removed.")


def update_port(port_name: str) -> None:
    if not port_exists(port_name):
        print(f"Port {port_name} does not exist.")
        sys.exit(1)

    print(f"Updating port '{port_name}'")

    ports_dir = Path("ports")
    port_dir = ports_dir / port_name
    versions_dir = Path("versions")
    version_dir = versions_dir / f"{port_name[0].lower()}-" / port_name

    # Read the current portfile
    with open(port_dir / "portfile.cmake", "r") as f:
        portfile_contents = f.read()

    # Is the current portfile using vcpkg_from_git or file(DOWNLOAD)?
    if not "vcpkg_from_git" in portfile_contents:
        print(f"portfile for port {port_name} does not use vcpkg_from_git")
        print("Cannot update port that was created using --latest")
        sys.exit(1)

    # Get the github user and repo from the portfile
    url_pattern = re.compile(r'URL\s+(https://github.com/[\w\-]+/[\w\-]+)')
    repo_url = url_pattern.search(portfile_contents).group(1)
    github_user, github_repo = repo_url.split("/")[-2:]

    # Get the REF from the portfile
    ref_pattern = re.compile(r'REF\s+([\w\-]+)')
    ref = ref_pattern.search(portfile_contents).group(1)

    # Get the latest commit info
    latest_commit_info = get_github_latest_commit_info(
        github_user, github_repo, ref)
    latest_commit_date = latest_commit_info["commit"]["committer"]["date"][:10]
    latest_commit_sha = latest_commit_info["sha"]
    latest_commit_message = latest_commit_info["commit"]["message"]

    print(f"GitHub repository URL: {repo_url}")
    print(f"Latest commit: {latest_commit_sha}")
    print(f"> {latest_commit_message}")

    if latest_commit_sha == ref:
        print(f"Port {port_name} is already up to date.")
        sys.exit(0)

    # Create the new portfile with the updated REF
    new_portfile_contents = portfile_contents.replace(
        f"REF {ref}", f"REF {latest_commit_sha}")
    with open(port_dir / "portfile.cmake", "w") as f:
        f.write(new_portfile_contents)

    # Create the new vcpkg.json with the updated version-string
    with open(port_dir / "vcpkg.json", "r") as f:
        vcpkg_json_data = json.load(f)
    version_string = f"{latest_commit_date}-{latest_commit_sha[:7]}"
    vcpkg_json_data["version-string"] = version_string
    with open(port_dir / "vcpkg.json", "w") as f:
        json.dump(vcpkg_json_data, f, indent=2)

    # Create the new version.json with the updated version-string
    with open(version_dir / f"{port_name}.json", "r") as f:
        version_json_data = json.load(f)
    version_json_data["versions"].append({
        "version-string": version_string,
        "git-tree": get_git_tree_sha(port_name)
    })
    with open(version_dir / f"{port_name}.json", "w") as f:
        json.dump(version_json_data, f, indent=2)

    # Add and commit all the things
    git(["add", "ports"])
    git(["add", "versions"])
    git(["commit", "-m", f"Update port {port_name} to {version_string}"])

    print(f"Succesfully updated port '{port_name}'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage a vcpkg registry.")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser(
        "add", help="Add a new port to the registry.")
    add_parser.add_argument("port_name", help="The name of the port to add.")
    add_parser.add_argument(
        "github_repo", help="The GitHub repository in the format 'user/repo'.")
    add_parser.add_argument("--latest", action="store_true",
                            help="Use the latest version from the GitHub repository.")
    add_parser.add_argument(
        "--ref", help="The specific git commit or branch to use for the port.")
    add_parser.add_argument("--dependencies", "--deps",
                            default="", help="Comma-separated list of dependencies.")
    add_parser.add_argument(
        "--library", "--lib", help="CMake library name (defaults to provided port name)")

    subparsers.add_parser(
        "list", help="List all ports in the registry.")

    remove_parser = subparsers.add_parser(
        "remove", help="Remove a port from the registry.")
    remove_parser.add_argument(
        "port_name", help="The name of the port to remove.")

    update_parser = subparsers.add_parser(
        "update", help="Update a port in the registry.")
    update_parser.add_argument(
        "port_name", help="The name of the port to update.")
    update_parser.add_argument(
        "--ref", help="The specific git commit to update the port to use.")

    args = parser.parse_args()

    if args.command == "add":
        dependencies = []
        if args.dependencies:
            dependencies = args.dependencies.split(",")
        github_user, github_repo = args.github_repo.split("/")
        add_port(args.port_name, args.library, github_user, github_repo, args.latest,
                 args.ref, dependencies)
    elif args.command == "list":
        list_ports()
    elif args.command == "remove":
        remove_port(args.port_name)
    elif args.command == "update":
        update_port(args.port_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
