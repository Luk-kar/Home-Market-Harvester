"""
This module provides mechanisms for integrating Streamlit applications into data processing
pipelines, specifically focusing on the execution and lifecycle management of Streamlit processes.
It facilitates the seamless operation of Streamlit apps as part of broader data engineering and
analysis workflows, offering utilities to start, monitor, and gracefully terminate Streamlit
applications.
"""

# Standard library imports
import os
import subprocess
import time

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
    Terminates the Streamlit process when the user types 'stop' and presses Enter.
    Or when the timeout interval is reached.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to manage.
    """

    hour = 3600
    timeout_interval = 3 * hour
    start_time = time.time()

    print("Type 'stop' and press Enter to terminate the Dashboard and its server:")
    while True:
        current_time = time.time()
        if current_time - start_time > timeout_interval:
            log_and_print("Timeout reached. Terminating the Streamlit process.")
            terminate_streamlit(streamlit_process)
            break
        try:
            user_input = input().strip().lower()
            if user_input in [
                "stop",
                "exit",
                "quit",
            ]:  # We do not need to be strict here
                terminate_streamlit(streamlit_process)
                break

            else:
                print(
                    "Unrecognized command. Type 'stop' and press Enter to terminate the Dashboard:"
                )
                time.sleep(1)

        except KeyboardInterrupt:
            handle_ctrl_c(streamlit_process)
            break


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
