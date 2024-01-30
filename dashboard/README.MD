# 🏠🔍 Rent Comparison Dashboard

A Python script that scrapes the utilized

## 🔨 Usage

Run and install virtual environment:

```
pip install pipenv
pipenv install
pipenv shell
```

Run the Dashboard

```
streamlit run dashboard//streamlit_app.py
```

The output renders in the OS's default webbrowser.
You can share the outcome in the local or network URL

## 🪓 Configuration

Simply modify the config file: `dashboard\config.py`.
More important arguments are:

```
DATA:
    "user_data_path": ...,
    "market_data_path": ...,

MODEL:
    "model_path": ...,
    "model_metadata_path": ...,

```

## 🤖 Testing

There is no automated tests

## 📜 License

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
