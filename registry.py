import sys
import os
import re
import json
import subprocess
import datetime
import argparse

from urllib.request import urlopen
from pathlib import Path


def port_exists(port_name):
    return (Path("ports") / port_name).exists()


def get_latest_commit_info(repo_url):
    api_url = repo_url.replace(
        'github.com', 'api.github.com/repos') + f"/commits/main"
    response = urlopen(api_url)
    data = json.loads(response.read().decode('utf-8'))
    return data


def update_portfile(port_name, latest_sha):
    ref_pattern = re.compile(r'(REF\s+)([\w\d]+)')
    url_pattern = re.compile(r'URL\s+(https://github.com/[\w\-]+/[\w\-]+)')
    portfile_path = f'ports/{port_name}/portfile.cmake'

    with open(portfile_path, 'r') as f:
        content = f.read()
        repo_url = url_pattern.search(content).group(1)
        current_sha = ref_pattern.search(content).group(2)

    if current_sha == latest_sha:
        return None

    content = ref_pattern.sub(f'\\1{latest_sha}', content)

    with open(portfile_path, 'w') as f:
        f.write(content)

    return latest_sha


def get_git_tree_sha(port_name):
    output = subprocess.check_output(
        ['git', 'rev-parse', f'HEAD:ports/{port_name}'])
    return output.decode('utf-8').strip()


def update_versions(port_name, latest_sha, update_vcpkg_json=True):
    short_sha = latest_sha[:7]
    version_date = datetime.date.today().strftime('%Y-%m-%d')
    new_version = f'{version_date}-{short_sha}'
    versions_dir = Path('versions') / \
        port_name[0].lower() / f'{port_name}.json'

    with open(versions_dir, 'r') as f:
        versions_data = json.load(f)

    # Update the versions JSON
    new_entry = {
        "version": new_version,
        "git-tree": get_git_tree_sha(port_name)
    }
    versions_data["versions"].insert(0, new_entry)

    with open(versions_dir, 'w') as f:
        json.dump(versions_data, f, indent=2)

    if update_vcpkg_json:
        vcpkg_json_path = f'ports/{port_name}/vcpkg.json'
        with open(vcpkg_json_path, 'r') as f:
            vcpkg_json_data = json.load(f)
        vcpkg_json_data["version-string"] = new_version
        with open(vcpkg_json_path, 'w') as f:
            json.dump(vcpkg_json_data, f, indent=2)

    return new_version


def update_all_ports():
    ports_dir = Path("ports")
    for port_dir in ports_dir.iterdir():
        if not port_dir.is_dir():
            continue
        port_name = port_dir.name
        portfile_path = port_dir / "portfile.cmake"
        with open(portfile_path, "r") as f:
            content = f.read()
        if "vcpkg_from_git" in content:
            print(f"Updating {port_name}")
            update_port(port_name)
        else:
            print(f"Skipping {port_name}, not using vcpkg_from_git")


def update_port(port_name):
    print(f"Updating {port_name}")

    portfile_path = f'ports/{port_name}/portfile.cmake'
    with open(portfile_path, 'r') as f:
        content = f.read()

    url_pattern = re.compile(r'URL\s+(https://github.com/[\w\-]+/[\w\-]+)')
    repo_url = url_pattern.search(content).group(1)

    commit_info = get_latest_commit_info(repo_url)
    latest_sha = commit_info['sha']
    commit_date = commit_info['commit']['author']['date'][:10]
    commit_author = commit_info['commit']['author']['name']
    commit_message = commit_info['commit']['message']
    print(
        f"Latest commit: {commit_date} - {commit_author}\n> {commit_message}")

    updated_sha = update_portfile(port_name, latest_sha)
    if updated_sha is None:
        print("Already latest commit.")
        return

    subprocess.run(['git', 'add', f'ports/{port_name}/portfile.cmake'])
    subprocess.run(['git', 'commit', '-m', f'Updating {port_name} REF'])

    new_version = update_versions(port_name, latest_sha)
    subprocess.run(['git', 'add', 'versions'])
    subprocess.run(['git', 'commit', '--amend', '--no-edit',
                   '-m', f'{port_name} --> {new_version}'])


def list_ports():
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


def remove_port(port_name):
    subprocess.run(["git", "rm", "-r", f"ports/{port_name}"])
    versions_path = Path("versions") / \
        port_name[0].lower() / f"{port_name}.json"
    subprocess.run(["git", "rm", str(versions_path)])
    with open("versions/baseline.json", "r") as f:
        baseline_data = json.load(f)
    del baseline_data[port_name]
    with open("versions/baseline.json", "w") as f:
        json.dump(baseline_data, f, indent=2)
    subprocess.run(["git", "add", "versions/baseline.json"])
    subprocess.run(["git", "commit", "-m", f"Remove {port_name}"])


def get_github_repo_data(username, repo_name):
    api_url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = urlopen(api_url)
    data = json.loads(response.read().decode("utf-8"))
    return data


def add_port(port_name, github_username, github_repo_name, ref=None, dependencies=""):
    if port_exists(port_name):
        print(f"Port already added: {port_name}")
        return

    # Ensure the ports/ and versions/ directories exist
    ports_dir = Path("ports")
    versions_dir = Path("versions")
    ports_dir.mkdir(exist_ok=True)
    versions_dir.mkdir(exist_ok=True)

    repo_data = get_github_repo_data(github_username, github_repo_name)
    description = repo_data["description"]

    # Get the latest commit info
    commit_info = get_latest_commit_info(
        f"https://github.com/{github_username}/{github_repo_name}")
    commit_date = commit_info["commit"]["committer"]["date"][:10]
    commit_sha = commit_info["sha"]

    version_string = f"{commit_date}-{commit_sha[:7]}"

    # Create port directory
    port_path = Path(f"ports/{port_name}")
    port_path.mkdir(parents=True)

    # Create vcpkg.json
    additional_dependencies = dependencies.split(",") if dependencies else []
    vcpkg_json_data = {
        "name": port_name,
        "version-string": version_string,
        "description": description,
        "supports": ["x86-windows", "x64-windows"],
        "dependencies": [
            {"name": "vcpkg-cmake", "host": True},
            {"name": "vcpkg-cmake-config", "host": True},
            *additional_dependencies
        ]
    }
    with open(port_path / "vcpkg.json", "w") as f:
        json.dump(vcpkg_json_data, f, indent=2)

    # Get the latest commit sha if ref is not provided
    if not ref:
        commit_info = get_latest_commit_info(
            f'https://github.com/{github_username}/{github_repo_name}')
        ref = commit_info['sha']

    # Create the portfile.cmake
    portfile_content = f"""vcpkg_from_git(
    OUT_SOURCE_PATH SOURCE_PATH
    URL https://github.com/{github_username}/{github_repo_name}.git
    REF {ref}
)

vcpkg_cmake_configure(
    SOURCE_PATH {{SOURCE_PATH}}
)

vcpkg_cmake_install()

vcpkg_cmake_config_fixup(CONFIG_PATH lib/cmake/{github_repo_name})
"""
    with open(ports_dir / port_name / "portfile.cmake", "w") as f:
        f.write(portfile_content)

    subprocess.run(["git", "add", f"ports/{port_name}"])
    commit_message = f"Add new port {port_name}"
    subprocess.run(["git", "commit", "-m", commit_message])

    commit_info = get_latest_commit_info(
        f"https://github.com/{github_username}/{github_repo_name}")
    commit_sha = commit_info['sha']
    commit_date = commit_info['commit']['author']['date'][:10]

    git_tree_sha = get_git_tree_sha(port_name)

    # Create the versions/*-/port-name.json file
    version_json = {
        "versions": [
            {
                "version-string": f"{commit_date}-{commit_sha[:7]}",
                "git-tree": git_tree_sha
            }
        ]
    }

    port_versions_path = versions_dir / \
        port_name[0].lower() / f"{port_name}.json"
    port_versions_path.parent.mkdir(parents=True, exist_ok=True)

    with open(port_versions_path, "w") as f:
        json.dump(version_json, f, indent=2)

    # Add the port to versions/baseline.json
    baseline_path = versions_dir / "baseline.json"
    baseline_data = {"default": {}}
    if baseline_path.exists():
        with open(baseline_path, "r") as f:
            baseline_data = json.load(f)

    baseline_data["default"][port_name] = {
        "baseline": f"{commit_date}-{commit_sha[:7]}",
        "port-version": 0
    }

    with open(baseline_path, "w") as f:
        json.dump(baseline_data, f, indent=2)

    subprocess.run(["git", "add", f"versions"])
    subprocess.run(["git", "commit", "--amend", "--no-edit"])


def main():
    if len(sys.argv) == 1:
        sys.argv.append("--help")

    parser = argparse.ArgumentParser(
        description="A simple package registry for vcpkg.")
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommand to run: list, remove, add, or update")

    # list command
    subparsers.add_parser(
        "list", help="List all the available packages in the registry.")

    # remove command
    remove_parser = subparsers.add_parser(
        "remove", help="Remove a package from the registry.")
    remove_parser.add_argument(
        "port_name", help="The name of the package to remove.")

    # add command
    add_parser = subparsers.add_parser(
        "add", help="Add a new package to the registry.")
    add_parser.add_argument(
        "port_name", help="The name of the package to add.")
    add_parser.add_argument(
        "github_path", help="The GitHub path (username/repo) for the package.")
    add_parser.add_argument(
        "--ref", default=None, help="A specific Git ref (branch, tag, or commit) to add.")
    add_parser.add_argument("--dependencies", "--deps",
                            default="", help="Comma-separated list of dependencies.")

    # update command
    update_parser = subparsers.add_parser(
        "update", help="Update an existing package in the registry.")
    update_parser.add_argument(
        "port_name", help="The name of the package to update.")
    update_parser.add_argument(
        "github_path", help="The GitHub path (username/repo) for the package.")
    update_parser.add_argument("ref", nargs="?", default=None,
                               help="A specific Git ref (branch, tag, or commit) to update.")

    args = parser.parse_args()

    if args.command == "list":
        list_ports()
    elif args.command == "remove":
        remove_port(args.port_name)
    elif args.command == "add":
        github_username, github_repo_name = args.github_path.split("/")
        add_port(args.port_name, github_username,
                 github_repo_name, ref=args.ref, dependencies=args.dependencies)
    elif args.command == "update":
        github_username, github_repo_name = args.github_path.split("/")
        update_port(args.port_name, github_username,
                    github_repo_name, ref=args.ref)


if __name__ == "__main__":
    main()
