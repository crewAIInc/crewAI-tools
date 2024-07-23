
The ApifyTool class provides the following methods:

- `run_actor`: Run an Apify actor with the given input.
- `wait_for_actor_run`: Wait for an Apify actor run to complete.
- `get_dataset`: Get the dataset associated with the given actor run.
- `get_dataset_items`: Get all items from the given dataset.
- `get_key_value_store`: Get the key-value store associated with the given actor run.
- `download_file`: Download a file from the key-value store of the given actor run.
- `store_dataset`: Store data in an Apify dataset.

You can use these methods to interact with various Apify services, such as running actors, waiting for actor runs to complete, fetching datasets, accessing the key-value store, downloading files, and storing data in datasets.

Make sure to replace `"your_apify_token"` and `"your_actor_id"` with your actual Apify token and the ID of the actor you want to run, respectively.