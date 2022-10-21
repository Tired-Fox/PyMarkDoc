import contextlib
from json import load
from pathlib import Path
from shutil import which
import subprocess
import sys
from livereload import Server
from subprocess import Popen, PIPE

# Mophidian code
from .observe import WatchFiles
from compiler.build import Build
from moph_logger import Log, LL, FColor
from ppm import PPM


def check_installed(package: str, logger: Log, package_manager: PPM):
    logger.Custom(
        f"{package_manager.ppm.name()} v{subprocess.check_output([str(which(package_manager.ppm.name())), '--version']).decode()}",
        clr=FColor.YELLOW,
        label="Version",
    )
    logger.Custom(
        f"You can change your preferred package manager (PPM) in \
{Log.path('moph.json', 'integrations', 'package_manager', spr=' ► ')}",
        clr=FColor.MAGENTA,
        label="Note",
    )

    if Path("package.json").exists():
        with open("package.json", "r", encoding="utf-8") as package_json:
            pkg_json = load(package_json)

        if "devDependencies" in pkg_json:
            if package in pkg_json["devDependencies"]:
                # Package exists
                return

        if "dependencies" in pkg_json:
            if package in pkg_json["dependencies"]:
                # Package exists
                return

        # Install package with preferred package manager (PPM)
        logger.Info(f"Package {package} was not found.")
        package_manager.ppm.install(package, "-D")
    else:
        # Init with PPM
        logger.Info(f"package.json was not found. Using preferred package managers init.")
        package_manager.ppm.init()

        # Install package with PPM
        package_manager.ppm.install(package, "-D")
        pass


def serve(
    open: bool, debug: bool, port: int = 3000, entry_file: str = "index.html", open_delay: int = 2
):
    """Automatically reload browser tab upon file modification."""

    # Start by moving all static files to the site directory
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    log_level = LL.INFO

    if debug:
        log_level = LL.DEBUG

    logger = Log(output=old_stdout, level=log_level)

    build = Build(logger=logger)
    build.full()

    logger.Debug("serve arguments")
    logger.Debug(
        f"open={open}, debug={debug}, port={port}, entry_file={entry_file}, open_delay={open_delay}"
    )
    with contextlib.redirect_stdout(None):
        with contextlib.redirect_stderr(None):
            logger.Info("Setting up server")
            server = Server()
            logger.Debug(f"build.config.build.refresh_delay: {build.config.build.refresh_delay}")
            server.watch("./site/**/*", delay=build.config.build.refresh_delay)

            logger.Debug(
                f"build.config.integration.package_manager: {build.config.integration.package_manager}"
            )

            package_manager = PPM(build.config.integration.package_manager)

            if build.config.integration.tailwind or build.config.integration.sass:
                # Check for node.js
                if which("node") is not None:
                    logger.Custom(
                        f"Node {subprocess.check_output(['node', '--version']).decode()}",
                        clr=FColor.YELLOW,
                        label="Version",
                    )
                else:
                    logger.Error(
                        "Node.js was not found. Install it and try again or disable all integrations."
                    )
                    exit(3)

            tailwind_thread = None
            logger.Debug(f"build.config.integration.tailwind: {build.config.integration.tailwind}")
            if build.config.integration.tailwind:
                check_installed("tailwindcss", logger, package_manager)
                logger.Info("Starting tailwindcss")
                cmd = package_manager.ppm.run_command("tailwind:watch")
                tailwind_thread = Popen(cmd, stdout=PIPE, stderr=PIPE)

            sass_thread = None
            logger.Debug(f"build.config.integration.sass: {build.config.integration.sass}")
            if build.config.integration.sass:
                check_installed("sass", logger, package_manager)
                logger.Info("Starting sass")
                cmd = package_manager.ppm.run_command("css:watch")
                sass_thread = Popen(cmd, stdout=PIPE, stderr=PIPE)

            # Use watchdog as to have an incremental build system
            logger.Info("Attaching to filesystem for updates")
            watch_files = WatchFiles(build=build, logger=logger)
            watch_files.start()

            # Start livereload server and auto open site in browser
            try:
                logger.Info(f"Started server at http://localhost:{port}/")
                if open:
                    logger.Info("Opening server in browser")
                server.serve(
                    port=port,
                    host="localhost",
                    root="site/",  # TODO: Allow user to specify
                    open_url_delay=open_delay if open else None,
                    live_css=False,
                    default_filename=entry_file,
                )
                logger.Custom("Cleaning up threads", clr=FColor.MAGENTA, label="SHUTDOWN")
            finally:
                # If the server is shutdown also stop watchdog
                watch_files.stop()
                if tailwind_thread is not None:
                    tailwind_thread.kill()

                if sass_thread is not None:
                    sass_thread.kill()
