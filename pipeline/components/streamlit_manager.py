# Standard library imports
import os
import subprocess
import sys

# Local imports
from pipeline.components.logging import log_and_print
from pipeline.components.pipeline_flow import run_stage


def handle_streamlit_app(stage: str):
    """
    Handles the execution of a Streamlit app stage within the pipeline.

    Args:
        stage (str): The name of the stage, expected to be a Streamlit app.
    """

    streamlit_process = run_stage(stage, os.environ)
    manage_streamlit_process(streamlit_process)


def manage_streamlit_process(streamlit_process: subprocess.Popen):
    """
    Provides an interface for managing the lifecycle of a Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to manage.
    """

    print("Type 'stop' and press Enter to terminate the Dashboard and its server:")
    while True:
        try:
            user_input = input().strip().lower()
            if user_input == "stop":
                terminate_streamlit(streamlit_process)
                break

            print(
                "Unrecognized command. Type 'stop' and press Enter to terminate the Dashboard:"
            )
        except KeyboardInterrupt:
            handle_ctrl_c(streamlit_process)


def terminate_streamlit(
    streamlit_process: subprocess.Popen, message: str = "Dashboard has been terminated."
):
    """
    Terminates the Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to terminate.
    """

    streamlit_process.terminate()
    streamlit_process.wait()
    log_and_print(message)


def handle_ctrl_c(streamlit_process: subprocess.Popen):
    """
    Handles a KeyboardInterrupt event by terminating the Streamlit process.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to terminate.
    """

    print("\nCtrl+C detected. Terminating the Dashboard...")

    terminate_streamlit(
        streamlit_process, "Dashboard has been terminated due to Ctrl+C."
    )
    sys.exit(1)
