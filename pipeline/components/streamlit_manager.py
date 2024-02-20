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
import sys
import threading

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
    timer = threading.Timer(
        timeout_interval, handle_timeout, [streamlit_process, timeout_interval]
    )
    timer.start()

    print("Type 'stop' and press Enter to terminate the Dashboard and its server:")
    while True:
        try:
            user_input = input().strip().lower()
            if user_input in [
                "stop",
                "exit",
                "quit",
            ]:  # We do not need to be strict here
                terminate_streamlit(streamlit_process)
                timer.cancel()
                break

            print(
                "Unrecognized command. Type 'stop' and press Enter to terminate the Dashboard:"
            )
        except KeyboardInterrupt:
            handle_ctrl_c(streamlit_process)
            timer.cancel()


def handle_timeout(streamlit_process: subprocess.Popen, interval: int):
    """
    Handler for the timeout that checks if the process is still running and terminates it.

    Args:
        streamlit_process (subprocess.Popen): The Streamlit process to check and possibly terminate.
        interval (int): The timeout interval in seconds.
    """
    if streamlit_process.poll() is None:  # Check if process is still running
        log_and_print(
            f"Terminating the Dashboard due to timeout after {interval // 3600} hours."
        )
        terminate_streamlit(streamlit_process)


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
