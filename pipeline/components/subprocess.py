# Standard library imports
from pathlib import Path
from typing import Optional
import logging
import os
import re
import subprocess
import time

# Local imports
from pipeline.components.logging import log_and_print
from pipeline.components.exceptions import PipelineError


def run_stage(_stage: str, env_vars: dict, args: Optional[list] = None):
    """
    Run a stage of the pipeline.

    Args:
        _stage (str): The path to the stage to run.
        env_vars (dict): The environment variables to set.
        args (list, optional): Additional arguments to pass to the stage.

    Returns:
        subprocess.Popen: The process object for the Streamlit app, if applicable.

    Raises:
        PipelineError: If the stage is not found or fails.
    """
    if not Path(_stage).exists():
        raise PipelineError(f"Stage not found: {_stage}")

    # https://regex101.com/r/nY3BlO/1/r/JFd40X/1
    pattern = r"^(?!.*[/\\][^/\\]*\.[^/\\]*$).*[/\\]([^/\\]+)$"
    match_dir_path_only = re.match(pattern, _stage)

    args_valid_type = None
    if args:
        args_valid_type = [str(arg) for arg in args] if args else None

    process = None
    exit_code = None

    try:
        if (
            _stage.endswith(".py") and not _stage.endswith("streamlit_app.py")
        ) or match_dir_path_only:
            exit_code = run_python(_stage, env_vars, args_valid_type)
        elif _stage.endswith(".ipynb"):
            exit_code = run_ipynb(_stage, env_vars)
        elif _stage.endswith("streamlit_app.py"):
            process = run_streamlit(_stage, env_vars)
        else:
            raise ValueError(f"Unsupported file type: {_stage}")

        if exit_code is not None and exit_code != 0:
            log_and_print(
                f"Stage {_stage} completed with exit code {exit_code}.", logging.WARNING
            )

    except subprocess.CalledProcessError as error:
        log_and_print(
            f"Error in {_stage} with exit code {error.returncode}.", logging.ERROR
        )
        raise PipelineError(f"Error in {_stage}. Exiting pipeline.") from error

    return process


def run_command(command: list[str], env_vars: Optional[dict] = None) -> int:
    """
    Run a command as a subprocess with optional environment variables
    and an option to ignore non-zero exit codes.

    Args:
        command (list[str]): The command to run as a list of strings.
        env_vars (dict, optional): Additional environment variables to set.

    Returns:
        int: The exit code of the subprocess.

    Raises:
        subprocess.CalledProcessError: If the subprocess call fails.
    """

    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)

    result = subprocess.run(
        command, env=env, check=False
    )  # Use check=False to manually handle exit codes
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    return result.returncode


def run_python(script: str, env_vars: dict, args: Optional[list] = None) -> int:
    """
    Run a Python script as a subprocess with optional command-line arguments.

    Args:
        script (str): The path to the Python script to run.
        env_vars (dict): Additional environment variables to set for the script.
        args (list, optional): A list of command-line arguments to pass to the script.

    Returns:
        int: The exit code of the subprocess.
    """
    command = ["python", script]
    if args:
        command.extend(args)

    exit_code = run_command(command, env_vars)

    return exit_code


def run_ipynb(_stage: str, env_vars: dict):
    """
    Run a Jupyter notebook as a subprocess by converting it to a script first.
    The execution uses the `pipenv` environment.

    Args:
        _stage (str): The path to the Jupyter notebook to run.
        env_vars (dict): Additional environment variables to set for the notebook.

    Returns:
        int: The exit code of the subprocess.
    """

    notebook_path = Path(_stage).resolve()

    # Command to convert and execute the notebook using nbconvert within pipenv
    command = [
        "pipenv",
        "run",
        "jupyter",
        "nbconvert",
        "--to",
        "script",
        "--execute",
        "--output-dir",
        str(notebook_path.parent),
        str(notebook_path),
    ]

    # Run the command
    exit_code = run_command(command, env_vars)

    return exit_code


def run_streamlit(script: list[str], env_vars: dict):
    """
    Run a Streamlit app as a subprocess and monitor
    its output to log when it's successfully initialized.

    Args:
        script (str): The path to the Streamlit script.
        env_vars (dict): Environment variables to set for the subprocess.

    WARNING:
        This function starts the Streamlit server as
        a non-blocking concurrent process.
        It is important to manage this process by monitoring
        its output for successful initialization
        and ensuring it is properly terminated when no longer needed.
        Failure to terminate the Streamlit process can result in resource leaks
        and unintended operation of the application.
        It is recommended to track the process ID and implement
        a mechanism to terminate the process based on the application's lifecycle or user action.
    """
    env = os.environ.copy()
    env.update(env_vars)

    # Start Streamlit as a subprocess and capture its output
    process = subprocess.Popen(
        ["streamlit", "run", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    # Monitor the subprocess output for a success message
    while True:
        output = process.stdout.readline()
        print(output, end="")  # Optional: print Streamlit's output to console
        if "You can now view your Streamlit app in your browser." in output:
            log_and_print("Streamlit app initialized successfully.")
            # WARNING about concurrent process management
            log_and_print(
                "WARNING: Streamlit app is running as a concurrent process. "
                "Ensure it is terminated appropriately when no longer needed.",
                logging.WARNING,
            )
            break
        if process.poll() is not None:
            log_and_print("Streamlit app failed to start.", logging.ERROR)
            break
        time.sleep(0.1)  # Avoid busy waiting

    return process
