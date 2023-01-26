# rtsp-api

API for DVRPC's Regional Transit Screening Platform. The frontend repo is at <https://github.com/dvrpc/rtps>.

## Development

To run the API locally, create and activate a Python virtual environment from the project root directory with the dependencies installed:

```bash
python3 -m venv ve
source ve/bin/activate
pip install -r requirements_dev.txt
```

Then run `uvicorn --reload main:app`. It will be available at <http://127.0.0.1:8000/api/rtsp/v2/docs>.

### Tests

The development virtual environment includes two dependencies for testing, `pytest` and `pytest-watch`. Pytest is the de facto standard for testing in Python, while `pytest-watch` will run the tests anytime a change is made to them. Just run `ptw` from the "tests" directory. Or you can run `python -m pytest` from the project root directory to run them manually.

Note: Using `pytest-watch` is an improvement over having to manually run tests, though in order for this to work on the tests in the "tests" directory, the following block had to be added before `from main import api` in the `pytest` configuration file, "conftest.py":

```python
import sys
sys.path.append("..")
```
