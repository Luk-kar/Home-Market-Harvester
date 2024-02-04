# Standard imports
from dotenv import load_dotenv
from pathlib import Path
import os
import re
import subprocess
import sys


def set_sys_path_to_project_root(__file__):
    root_dir = Path(__file__).resolve().parent
    sys.path.append(str(root_dir))


set_sys_path_to_project_root(__file__)


def initialize_environment_settings():
    """
    Creates or verifies an .env file with predefined (dummy) environment variables for project configuration.

    Raises:
        ValueError: If the .env file is not found or is empty.
    """

    env_path = ".env"  # Assuming the root of the project is the project directory

    env_content = (
        "USER_OFFERS_PATH=data\test\your_offers.csv\n"  # A structure example
        "MARKET_OFFERS_TIMEPLACE=\n"  # To be created after the scraping stage
        "MODEL_PATH=model.pkl\n"  # To be created after model training
        "LOCATION_QUERY=Warszawa\n"  # Be sure that location fits the query
        "AREA_RADIUS=25\n"  # 0, 5, 10, 15, 25, 50, 75
        "SCRAPED_OFFERS_CAP=5\n"  # Sky is the limit
        "CHROME_DRIVER_PATH=\n"  # path to the ChromeDriver
        "CHROME_BROWSER_PATH=\n"  # path to the Chrome browser
    )

    if not env_path.exists():
        with open(env_path, "w") as f:
            f.write(env_content)

    if env_path.read_text() == env_content:
        raise ValueError(
            "Please fill in the .env file with your data.\n"
            f"The file {env_path} is located at the root of the project.\n"
            "Reload the environment settings."
        )


initialize_environment_settings()


def run_command(command, env_vars=None):
    """
    Run a command as a subprocess with optional environment variables.

    Args:
        command (list): The command to run as a list of strings.
        env_vars (dict, optional): Additional environment variables to set.

    Returns:
        int: The return code of the subprocess.
    """
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
    result = subprocess.run(command, env=env)
    return result.returncode


def run_python(script, env_vars=None):
    """
    Run a Python script as a subprocess.
    """
    return run_command(["python", script], env_vars)


def run_ipynb(script, env_vars=None):
    """
    Run a Jupyter notebook as a subprocess by converting it to a script first.
    """
    return run_command(
        ["jupyter", "nbconvert", "--to", "script", script, "--execute"], env_vars
    )


def run_streamlit(script, env_vars=None):
    """
    Run a Streamlit app as a subprocess.
    """
    return run_command(["streamlit", "run", script], env_vars)


class PipelineError(Exception):
    """Exception raised for errors in the pipeline."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def run_stage(stage):
    """
    Run a stage of the pipeline.

    Args:
        stage (str): The path to the stage to run.

    Returns:
        int: The return code of the stage.
    """
    if not os.path.exists(stage):
        raise PipelineError(f"Stage not found: {stage}")

    if stage.endswith(".py") or re.match(r".*\.([a-z]|\_)+$", stage):  # TODO check
        return run_python(stage)
    elif stage.endswith(".ipynb"):
        return run_ipynb(stage)
    elif stage.endswith(".py"):
        return run_streamlit(stage)
    else:
        raise ValueError(f"Unsupported file type: {stage}")


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env

    scraping = [os.path.join("pipeline", "src", "a_scraping")]
    cleaning_stage = os.path.join("pipeline", "src", "b_cleaning")
    cleaning_sub_stageg = [
        os.path.join(cleaning_stage, "a_cleaning_OLX.ipynb"),
        os.path.join(cleaning_stage, "b_cleaning_OtoDom.ipynb"),
        os.path.join(cleaning_stage, "c_combining_data.ipynb"),
        os.path.join(cleaning_stage, "d_creating_map_data.ipynb"),
    ]
    model_developing = [
        os.path.join("pipeline", "src", "c_model_developing", "model_training.ipynb")
    ]
    data_visualizing = [
        os.path.join(
            "pipeline", "src", "d_data_visualizing", "dashboard", "streamlit_app.py"
        )
    ]

    stages = scraping + cleaning_sub_stageg + model_developing + data_visualizing

    for stage in stages:
        print(f"Running {stage}...")
        return_code = run_stage(stage)
        if return_code != 0:
            raise PipelineError(f"Error in {stage}. Exiting pipeline.")
    print("Pipeline execution completed.")
