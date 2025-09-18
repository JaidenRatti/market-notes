# Testing & Archive Files

This folder contains development and testing files that were used during the creation and testing of the tweet-to-market pipeline. These files are not needed for normal usage of the module.

## Test Files

- **`test_sentiment.py`** - Tests for the sentiment analysis component
- **`test_polymarket_full.py`** - Tests for Polymarket API integration  
- **`test_multiple_tweets.py`** - Batch testing with multiple tweets
- **`verify_api.py`** - API verification and validation tests

## Legacy Pipeline Files

- **`complete_pipeline.py`** - Earlier version of the complete pipeline (superseded by `enhanced_pipeline.py`)

## Test Results & Output Files

- **`tweet_analysis_*.json`** - Sample output files from test runs
- **`pipeline_results.json`** - Large test results file with multiple tweet analyses
- **`enhanced_pipeline_results.json`** - Results from enhanced pipeline tests

## Usage

These files are kept for reference and debugging purposes. If you want to run the tests:

```bash
# Make sure you're in the main pipeline directory
cd ..

# Activate virtual environment
source venv/bin/activate

# Run individual tests (from testing folder)
python testing/test_sentiment.py
python testing/test_polymarket_full.py
python testing/verify_api.py
```

## Note

For normal usage of the tweet-to-market pipeline, you don't need any files from this folder. Use the main module files in the parent directory instead.