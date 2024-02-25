# 🏠📊 Rent Comparison Dashboard

The Rent Comparison Dashboard is a Streamlit-based web application designed for comparing rental properties.
It provides users with insights into the real estate market,
allowing them to evaluate and compare their own rental offers with the current market trends.
Ultimately, the dashboard accepts arguments from environment variables:
`USER_OFFERS_PATH`, `MODEL_PATH`
and the `run_pipeline.conf`
`MARKET_OFFERS_TIMEPLACE`, `DESTINATION_COORDINATES`

## 🔨 Usage

**Run and install virtual environment:**

```
pip install pipenv
pipenv install
pipenv shell
```

**Run the Dashboard**:

```
streamlit run pipeline//stages//d_data_visualizing//streamlit_app.py
```

The output renders in the OS's default web browser.
You can share the outcome via the local or network URL.

## ⚙️ Configuration

Simply modify the config file: `pipeline//config//d_data_visualizing.py`.
Important arguments include:

```
DATA:
    "user_data_path": ...,
    "market_data_datetime": ...,

MODEL:
    "model_path": ...,

```

To upload the selected data to the dashboard, change the time-place value of:
`MARKET_OFFERS_TIMEPLACE`
in the file:
`pipeline//config//run_pipeline.conf`

`DESTINATION_COORDINATES` is responsible for setting point of interest on the map (red dot).

By the date of writing this `README` there is no known method to put arguments by the command line to the `streamlit` framework.

## ✅ Testing

Currently, there are no automated tests for the application.

## 🩹 Troubleshoots

- When the module `config.py` is loaded, the warnings are invoked each time, instead of just once in the runtime.
- Ensure the `USER_OFFERS_PATH` environment variable is set correctly to avoid FileNotFoundError during data loading.
- The `DESTINATION_COORDINATES` should

## 📜 License

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
