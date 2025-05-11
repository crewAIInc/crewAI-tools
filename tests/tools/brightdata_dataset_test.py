import unittest
from unittest.mock import MagicMock, patch

from crewai_tools.tools.brightdata_tool.brightdata_dataset import (
    BrightDataDatasetTool,
    BrightDataWebScraperAPIWrapper,
)


class TestBrightDataDatasetTool(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {"BRIGHT_DATA_API_KEY": "test_api_key", "BRIGHT_DATA_ZONE": "test_zone"},
    )
    def setUp(self):
        self.tool = BrightDataDatasetTool()
        self.params = {
            "dataset_id": "ds123",
            "url": "https://example.com/data",
            "zipcode": "12345",
            "additional_params": {"param": "value"},
        }

    @patch("crewai_tools.tools.brightdata_tool.brightdata_dataset.requests.post")
    def test_get_dataset_data_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        mock_post.return_value = mock_response

        wrapper = BrightDataWebScraperAPIWrapper()
        result = wrapper.get_dataset_data(**self.params)
        self.assertEqual(result, {"data": "success"})

    @patch("crewai_tools.tools.brightdata_tool.brightdata_dataset.requests.post")
    def test_get_dataset_data_failure(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        wrapper = BrightDataWebScraperAPIWrapper()
        with self.assertRaises(ValueError) as context:
            wrapper.get_dataset_data(**self.params)
        self.assertIn("Error 400", str(context.exception))

    @patch(
        "crewai_tools.tools.brightdata_tool.brightdata_dataset.BrightDataWebScraperAPIWrapper.get_dataset_data"
    )
    def test_tool_run_sync(self, mock_sync_call):
        mock_sync_call.return_value = {"data": "sync_ok"}
        result = self.tool._run(**self.params)
        self.assertEqual(result, {"data": "sync_ok"})

    @patch(
        "crewai_tools.tools.brightdata_tool.brightdata_dataset.BrightDataWebScraperAPIWrapper.get_dataset_data_async"
    )
    def test_tool_run_async(self, mock_async_call):
        mock_async_call.return_value = {"data": "async_ok"}
        self.params["async_mode"] = True
        result = self.tool._run(**self.params)
        self.assertEqual(result, {"data": "async_ok"})


if __name__ == "__main__":
    unittest.main()
