import asyncio
import os
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


async def create_smartscraper_job(client: AsyncClient) -> str:
    """Create a scheduled job for smartscraper"""
    print("📅 Creating SmartScraper scheduled job...")
    
    job_config = {
        "website_url": "https://news.ycombinator.com",
        "user_prompt": "Extract the top 5 news titles and their URLs",
        "render_heavy_js": False,
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; ScheduledJob/1.0)"
        }
    }
    
    result = await client.create_scheduled_job(
        job_name="HN Top News Scraper",
        service_type="smartscraper",
        cron_expression="0 */6 * * *",  # Every 6 hours
        job_config=job_config,
        is_active=True
    )
    
    job_id = result["id"]
    print(f"✅ Created SmartScraper job with ID: {job_id}")
    return job_id


async def create_searchscraper_job(client: AsyncClient) -> str:
    """Create a scheduled job for searchscraper"""
    print("📅 Creating SearchScraper scheduled job...")
    
    job_config = {
        "user_prompt": "Find the latest AI and machine learning news",
        "num_results": 5,
        "headers": {
            "User-Agent": "Mozilla/5.0 (compatible; ScheduledJob/1.0)"
        }
    }
    
    result = await client.create_scheduled_job(
        job_name="AI News Search",
        service_type="searchscraper",
        cron_expression="0 9 * * 1",  # Every Monday at 9 AM
        job_config=job_config,
        is_active=True
    )
    
    job_id = result["id"]
    print(f"✅ Created SearchScraper job with ID: {job_id}")
    return job_id


async def create_crawl_job(client: AsyncClient) -> str:
    """Create a scheduled job for crawl"""
    print("📅 Creating Crawl scheduled job...")
    
    job_config = {
        "url": "https://example.com",
        "prompt": "Extract all product information",
        "extraction_mode": True,
        "depth": 2,
        "max_pages": 10,
        "same_domain_only": True,
        "cache_website": True
    }
    
    result = await client.create_scheduled_job(
        job_name="Product Catalog Crawler",
        service_type="crawl",
        cron_expression="0 2 * * *",  # Daily at 2 AM
        job_config=job_config,
        is_active=True
    )
    
    job_id = result["id"]
    print(f"✅ Created Crawl job with ID: {job_id}")
    return job_id


async def manage_jobs(client: AsyncClient, job_ids: list[str]):
    """Demonstrate job management operations"""
    print("\n🔧 Managing scheduled jobs...")
    
    # List all jobs
    print("\n📋 Listing all scheduled jobs:")
    jobs_result = await client.get_scheduled_jobs(page=1, page_size=10)
    print(f"Total jobs: {jobs_result['total']}")
    
    for job in jobs_result["jobs"]:
        print(f"  - {job['job_name']} ({job['service_type']}) - Active: {job['is_active']}")
    
    # Get details of first job
    if job_ids:
        print(f"\n🔍 Getting details for job {job_ids[0]}:")
        job_details = await client.get_scheduled_job(job_ids[0])
        print(f"  Name: {job_details['job_name']}")
        print(f"  Cron: {job_details['cron_expression']}")
        print(f"  Next run: {job_details.get('next_run_at', 'N/A')}")
        
        # Pause the first job
        print(f"\n⏸️ Pausing job {job_ids[0]}:")
        pause_result = await client.pause_scheduled_job(job_ids[0])
        print(f"  Status: {pause_result['message']}")
        
        # Resume the job
        print(f"\n▶️ Resuming job {job_ids[0]}:")
        resume_result = await client.resume_scheduled_job(job_ids[0])
        print(f"  Status: {resume_result['message']}")
        
        # Update job configuration
        print(f"\n📝 Updating job {job_ids[0]}:")
        update_result = await client.update_scheduled_job(
            job_ids[0],
            job_name="Updated HN News Scraper",
            cron_expression="0 */4 * * *"  # Every 4 hours instead of 6
        )
        print(f"  Updated job name: {update_result['job_name']}")
        print(f"  Updated cron: {update_result['cron_expression']}")


async def trigger_and_monitor_jobs(client: AsyncClient, job_ids: list[str]):
    """Demonstrate manual job triggering and execution monitoring"""
    print("\n🚀 Triggering and monitoring jobs...")
    
    for job_id in job_ids:
        print(f"\n🎯 Manually triggering job {job_id}:")
        trigger_result = await client.trigger_scheduled_job(job_id)
        execution_id = trigger_result["execution_id"]
        print(f"  Execution ID: {execution_id}")
        print(f"  Message: {trigger_result['message']}")
        
        # Wait a bit for execution to start
        await asyncio.sleep(2)
        
        # Get execution history
        print(f"\n📊 Getting execution history for job {job_id}:")
        executions = await client.get_job_executions(job_id, page=1, page_size=5)
        print(f"  Total executions: {executions['total']}")
        
        for execution in executions["executions"][:3]:  # Show last 3 executions
            print(f"    - Execution {execution['id']}: {execution['status']}")
            print(f"      Started: {execution['started_at']}")
            if execution.get('completed_at'):
                print(f"      Completed: {execution['completed_at']}")
            if execution.get('credits_used'):
                print(f"      Credits used: {execution['credits_used']}")


async def cleanup_jobs(client: AsyncClient, job_ids: list[str]):
    """Clean up created jobs"""
    print("\n🧹 Cleaning up created jobs...")
    
    for job_id in job_ids:
        print(f"🗑️ Deleting job {job_id}:")
        delete_result = await client.delete_scheduled_job(job_id)
        print(f"  Status: {delete_result['message']}")


async def main():
    """Main function demonstrating async scheduled jobs"""
    # Initialize async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return

    async with AsyncClient(api_key=api_key) as client:
        print("🚀 Starting Async Scheduled Jobs Demo")
        print("=" * 50)
        
        job_ids = []
        
        try:
            # Create different types of scheduled jobs
            smartscraper_job_id = await create_smartscraper_job(client)
            job_ids.append(smartscraper_job_id)
            
            searchscraper_job_id = await create_searchscraper_job(client)
            job_ids.append(searchscraper_job_id)
            
            crawl_job_id = await create_crawl_job(client)
            job_ids.append(crawl_job_id)
            
            # Manage jobs
            await manage_jobs(client, job_ids)
            
            # Trigger and monitor jobs
            await trigger_and_monitor_jobs(client, job_ids)
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
        
        finally:
            # Clean up
            await cleanup_jobs(client, job_ids)
        
        print("\n✅ Async Scheduled Jobs Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
