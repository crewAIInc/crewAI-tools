import typing as t
from crewai_tools.tools.base_tool import BaseTool
from apify_client import ApifyClient, ActorRun, Dataset

class ApifyTool(BaseTool):
    def __init__(self, apify_token: str):
        self.client = ApifyClient(apify_token)

    def _run(self, query: str) -> str:
        """
        Run the Apify tool with the given query.
        """
        # Parse the query and determine the appropriate Apify action
        # For example, you could use natural language processing to extract the intent
        # and map it to an Apify action

        # Execute the Apify action using the client
        # For example, to run an actor:
        actor_run = self.run_actor(actor_id="your_actor_id", run_input={"query": query})

        # Wait for the actor to complete
        actor_run = self.wait_for_actor_run(actor_run)

        # Return the result
        return actor_run.output

    def run_actor(self, actor_id: str, run_input: dict) -> ActorRun:
        """
        Run an Apify actor with the given input.
        """
        return self.client.actor.call_run(actor_id=actor_id, run_input=run_input)

    def wait_for_actor_run(self, actor_run: ActorRun) -> ActorRun:
        """
        Wait for an Apify actor run to complete.
        """
        while not actor_run.is_finished():
            actor_run = self.client.actor.get_run(actor_run.id)

        return actor_run

    def get_dataset(self, actor_run: ActorRun, dataset_id: str = None) -> Dataset:
        """
        Get the dataset associated with the given actor run.
        """
        if dataset_id:
            return self.client.dataset.get(dataset_id)
        else:
            return actor_run.dataset

    def get_dataset_items(self, dataset: Dataset) -> List[Dict[str, Any]]:
        """
        Get all items from the given dataset.
        """
        return list(dataset.iterate_items())

    def get_key_value_store(self, actor_run: ActorRun) -> Dict[str, Any]:
        """
        Get the key-value store associated with the given actor run.
        """
        return actor_run.key_value_store

    def download_file(self, actor_run: ActorRun, key: str, file_path: str):
        """
        Download a file from the key-value store of the given actor run.
        """
        with open(file_path, "wb") as file:
            file.write(actor_run.key_value_store.get_file(key).read())

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("This tool does not support async mode.")