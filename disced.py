#!/usr/bin/python3

import argparse
import os
import shutil
import subprocess

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description='disced -m <markdown_filename> -sdn -v <version_number> -p <base_path>')
    parser.add_argument('-m', dest='markdown_filename', help='markdown filename with extension')
    parser.add_argument('-s', action='store_true', dest='rescue_staged', help='use the last staged version of the document')
    parser.add_argument('-d', action='store_false', dest='do_edit', help="don't edit the document")
    parser.add_argument('-n', action='store_true', dest='dont_publish', help="don't publish the document")
    parser.add_argument('-v', dest='version_number', help='MAAS version to publish (using tabs), e.g., 3.4 (default current)')
    parser.add_argument('-p', dest='base_path', help='base markdown repo path (defaults to ~/src/mod/maas-offline-docs)')
    args = parser.parse_args()

    # Presets
    rescue_staged = args.rescue_staged
    dont_publish = args.dont_publish
    do_edit = args.do_edit
    version_number = args.version_number or "3.3"
    base_path = args.base_path or "/home/stormrider/src/maas-doc"
    bench = "/tmp/bench"
    stage = "/tmp/staging"
    galley = "4917"
    log = f"{stage}/log/tab2html.log"

    # Markdown filename
    git_md_basename = args.markdown_filename

    # Compute absolute path to markdown file
    git_md_abspath = os.path.join(base_path, version_number, "src", git_md_basename)

    if rescue_staged:
        print("substituting previously staged file for git original")
        git_md_abspath = os.path.join(stage, git_md_basename)

    # Compute paths
    git_md_dir = os.path.dirname(git_md_abspath)
    git_repo_root = os.path.join(git_md_dir, "..")

    # Pull the topic from disc to bench
    subprocess.run(["dpull", "-n", galley], stdout=open(f"{bench}/{git_md_basename}.discmd", "w"))

    # Copy the master from git to bench
    shutil.copy(git_md_abspath, bench)

    if rescue_staged:
        shutil.copy(os.path.join(stage, "markdown", git_md_basename), bench)

    if do_edit:
        # Copy the current discourse version into the git repo
        shutil.copy(os.path.join(bench, f"{git_md_basename}.discmd"), os.path.join(git_repo_root, "src", git_md_basename))

        # Change to the root of the git repo
        os.chdir(git_repo_root)

        # Stage everything
        subprocess.run(["git", "add", "."])

        # Commit the changes
        subprocess.run(["git", "commit", "-m", f"Updated {git_md_basename} to current discourse version"])

        # Push the changes upstream
        subprocess.run(["git", "push"])

        # Store the diff in a findable file
        subprocess.run(["diff", os.path.join(bench, git_md_basename), os.path.join(bench, f"{git_md_basename}.discmd")], stdout=open(f"{bench}/md-diff", "w"))

        # Open the text editor with the files
        subprocess.run(["emacs", "-q", "-l", "/home/stormrider/.emacs2", os.path.join(bench, f"{git_md_basename}.discmd"), os.path.join(bench, git_md_basename), os.path.join(bench, "md-diff")])

        # Ask whether to stage the changes
        answer = input("Stage changes for review? [Y/n] ")
        if answer.lower() in ["n", "no"]:
            exit()

        # Create the staging directory
        os.makedirs(f"{stage}/log", exist_ok=True)
        os.makedirs(f"{stage}/markdown", exist_ok=True)
        os.makedirs(f"{stage}/production-html-deb/cli/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-deb/ui/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-deb/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-deb/images", exist_ok=True)
        os.makedirs(f"{stage}/production-html-snap/cli/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-snap/ui/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-snap/css", exist_ok=True)
        os.makedirs(f"{stage}/production-html-snap/images", exist_ok=True)

        # Capture the markdown and push to galley
        subprocess.run(["cat", os.path.join(bench, git_md_basename)], stdout=subprocess.PIPE)
        subprocess.run(["dpush", "-n", galley], stdin=subprocess.PIPE, text=True)

    if do_edit:
        # Run the snap ui version of the html
        tab2html_command("v{0} Snap".format(version_number), "UI", TITLE, git_md_abspath, stage, "template.html")

        # Run the deb ui version of the html
        tab2html_command("v{0} Packages".format(version_number), "UI", TITLE, git_md_abspath, stage, "template.html")

        # Run the snap cli version of the html
        tab2html_command("v{0} Snap".format(version_number), "CLI", TITLE, git_md_abspath, stage, "template.html")

        # Run the deb cli version of the html
        tab2html_command("v{0} Packages".format(version_number), "CLI", TITLE, git_md_abspath, stage, "template.html")

        # Copy images to production HTML root
        shutil.copytree("/tmp/images", os.path.join(git_repo_root, "production-html-snap/images"))
        shutil.copytree("/tmp/images", os.path.join(git_repo_root, "production-html-deb/images"))

    if do_edit:
        # Ask whether to automatically update the git repo
        answer = input("Stage all changes and commit/push git repo? [Y/n] ")

        # If no, just exit
        if answer.lower() in ["n", "no"]:
            exit()

        # Change to the root of the git repo
        os.chdir(git_repo_root)

        # Stage everything
        subprocess.run(["git", "add", "."])

        # Get a specific commit message for this change
        commit_message = input("Specific commit message (1 line)? ")

        # Commit the changes
        subprocess.run(["git", "commit", "-m", "[{0}] {1}".format(HTMLNAME, commit_message)])

        # Push the changes upstream
        subprocess.run(["git", "push"])


def tab2html_command(version, mode, title, git_md_abspath, stage, template_file):
    htmlname = generate_htmlname(git_md_abspath)
    template_path = os.path.join(git_repo_root, "html-support/templates", version, mode, template_file)
    output_path = os.path.join(stage, "production-html-{0}/{1}/{2}".format(version.lower(), mode.lower(), htmlname))
    sedcmd = "s/zork/{0}/g".format(htmlname)

    subprocess.run(["tab2html", version, mode, title, "-i", git_md_abspath, "-l", "-L", log, "-o", output_path, "-t", template_path])
    subprocess.run(["sed", "-i", "-e", sedcmd, output_path])


def generate_htmlname(git_md_abspath):
    name = os.path.splitext(os.path.basename(git_md_abspath))[0]
    if name == "maas-documentation":
        return "maas-documentation-25.html"
    return "{0}.html".format(name)


if __name__ == "__main__":
    main()
