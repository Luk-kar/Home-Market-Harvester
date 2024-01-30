# 🏠🔍 Rent Comparison Dashboard

The Rent Comparison Dashboard is a Streamlit-based web application designed for comparing rental properties.
It provides users with insights into the real estate market,
allowing them to evaluate and compare their own rental offers with the current market trends.

## 🔨 Usage

**Run and install virtual environment:**

```
pip install pipenv
pipenv install
pipenv shell
```

**Run the Dashboard**:

```
streamlit run dashboard//streamlit_app.py
```

The output renders in the OS's default web browser.
You can share the outcome via the local or network URL.

## 🪓 Configuration

Simply modify the config file: `dashboard\config.py`.
Important arguments include:

```
DATA:
    "user_data_path": ...,
    "market_data_datetime": ...,

MODEL:
    "model_path": ...,

```

## 🤖 Testing

Currently, there are no automated tests for the application.

## Troubleshoots

- When the module `config.py` is loaded, the warnings are invoked each time, instead of just once in the runtime.
- Ensure the `YOUR_OFFERS_PATH` environment variable is set correctly to avoid FileNotFoundError during data loading.

## 📜 License

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
