import unittest
from unittest.mock import MagicMock, patch

from crewai_tools.tools.brightdata_tool.brightdata_dataset import (
    BrightDataDatasetTool,
    BrightDataDatasetToolException,
)


class TestBrightDataDatasetTool(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    def setUp(self):
        self.tool = BrightDataDatasetTool()

    def test_filter_dataset_by_id_success(self):
        result = self.tool.filter_dataset_by_id("amazon_product")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "amazon_product")
        self.assertEqual(result[0]["dataset_id"], "gd_l7q7dkf244hwjntr0")

    def test_filter_dataset_by_id_not_found(self):
        result = self.tool.filter_dataset_by_id("nonexistent_dataset")
        self.assertEqual(len(result), 0)

    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    @patch("crewai_tools.tools.brightdata_tool.brightdata_dataset.asyncio.run")
    def test_run_successful_dataset_retrieval(self, mock_asyncio_run):
        mock_asyncio_run.return_value = {"data": [{"product": "test"}]}
        
        tool = BrightDataDatasetTool()
        result = tool._run(
            dataset_type="amazon_product",
            url="https://amazon.com/dp/test123",
            format="json"
        )
        
        self.assertEqual(result, {"data": [{"product": "test"}]})
        mock_asyncio_run.assert_called_once()

    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    def test_run_missing_required_params(self):
        tool = BrightDataDatasetTool()
        with self.assertRaises(ValueError) as context:
            tool._run(dataset_type="amazon_product")
        
        self.assertIn("url is required", str(context.exception))

    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    def test_run_invalid_dataset_type(self):
        tool = BrightDataDatasetTool()
        with self.assertRaises(ValueError) as context:
            tool._run(
                dataset_type="invalid_type",
                url="https://example.com"
            )
        
        self.assertIn("Unable to find the dataset", str(context.exception))

    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    @patch("crewai_tools.tools.brightdata_tool.brightdata_dataset.asyncio.run")
    def test_run_with_additional_params(self, mock_asyncio_run):
        mock_asyncio_run.return_value = {"data": [{"product": "test"}]}
        
        tool = BrightDataDatasetTool()
        result = tool._run(
            dataset_type="amazon_product",
            url="https://amazon.com/dp/test123",
            format="json",
            zipcode="12345",
            additional_params={"pages_to_search": "2"}
        )
        
        self.assertEqual(result, {"data": [{"product": "test"}]})
        mock_asyncio_run.assert_called_once()

    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key"},
    )
    @patch("crewai_tools.tools.brightdata_tool.brightdata_dataset.asyncio.run")
    def test_run_with_exception(self, mock_asyncio_run):
        mock_asyncio_run.side_effect = BrightDataDatasetToolException("API Error", 500)
        
        tool = BrightDataDatasetTool()
        with self.assertRaises(BrightDataDatasetToolException) as context:
            tool._run(
                dataset_type="amazon_product",
                url="https://amazon.com/dp/test123"
            )
        
        self.assertEqual(context.exception.error_code, 500)
        self.assertIn("API Error", str(context.exception))

    def test_missing_api_key_error_message(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(ValueError) as context:
                tool = BrightDataDatasetTool()
                tool._run(
                    dataset_type="amazon_product",
                    url="https://amazon.com/dp/test123"
                )
            
            error_message = str(context.exception)
            self.assertIn("BRIGHT_DATA_API_KEY environment variable is required", error_message)
            self.assertIn("Get your API key from https://brightdata.com/", error_message)


if __name__ == "__main__":
    unittest.main()
