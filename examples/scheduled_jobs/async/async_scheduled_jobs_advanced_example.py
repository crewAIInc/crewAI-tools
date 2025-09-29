import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

from dotenv import load_dotenv

from scrapegraph_py import AsyncClient
from scrapegraph_py.logger import sgai_logger

# Load environment variables from .env file
load_dotenv()

sgai_logger.set_logging(level="INFO")


class ScheduledJobManager:
    """Advanced scheduled job manager with monitoring and automation"""
    
    def __init__(self, client: AsyncClient):
        self.client = client
        self.active_jobs: Dict[str, Dict[str, Any]] = {}
    
    async def create_monitoring_job(self, website_url: str, job_name: str, cron_expression: str) -> str:
        """Create a job that monitors website changes"""
        print(f"📅 Creating monitoring job for {website_url}...")
        
        job_config = {
            "website_url": website_url,
            "user_prompt": "Monitor for any changes in content, new articles, or updates. Extract the latest information.",
            "render_heavy_js": True,
            "headers": {
                "User-Agent": "Mozilla/5.0 (compatible; MonitoringBot/1.0)"
            }
        }
        
        result = await self.client.create_scheduled_job(
            job_name=job_name,
            service_type="smartscraper",
            cron_expression=cron_expression,
            job_config=job_config,
            is_active=True
        )
        
        job_id = result["id"]
        self.active_jobs[job_id] = {
            "name": job_name,
            "url": website_url,
            "type": "monitoring",
            "created_at": datetime.now()
        }
        
        print(f"✅ Created monitoring job with ID: {job_id}")
        return job_id
    
    async def create_data_collection_job(self, search_prompt: str, job_name: str, cron_expression: str) -> str:
        """Create a job that collects data from multiple sources"""
        print(f"📅 Creating data collection job: {search_prompt}...")
        
        job_config = {
            "user_prompt": search_prompt,
            "num_results": 10,
            "headers": {
                "User-Agent": "Mozilla/5.0 (compatible; DataCollector/1.0)"
            }
        }
        
        result = await self.client.create_scheduled_job(
            job_name=job_name,
            service_type="searchscraper",
            cron_expression=cron_expression,
            job_config=job_config,
            is_active=True
        )
        
        job_id = result["id"]
        self.active_jobs[job_id] = {
            "name": job_name,
            "prompt": search_prompt,
            "type": "data_collection",
            "created_at": datetime.now()
        }
        
        print(f"✅ Created data collection job with ID: {job_id}")
        return job_id
    
    async def create_crawl_job(self, base_url: str, job_name: str, cron_expression: str) -> str:
        """Create a job that crawls websites for comprehensive data"""
        print(f"📅 Creating crawl job for {base_url}...")
        
        job_config = {
            "url": base_url,
            "prompt": "Extract all relevant information including titles, descriptions, links, and metadata",
            "extraction_mode": True,
            "depth": 3,
            "max_pages": 50,
            "same_domain_only": True,
            "cache_website": True,
            "sitemap": True
        }
        
        result = await self.client.create_scheduled_job(
            job_name=job_name,
            service_type="crawl",
            cron_expression=cron_expression,
            job_config=job_config,
            is_active=True
        )
        
        job_id = result["id"]
        self.active_jobs[job_id] = {
            "name": job_name,
            "url": base_url,
            "type": "crawl",
            "created_at": datetime.now()
        }
        
        print(f"✅ Created crawl job with ID: {job_id}")
        return job_id
    
    async def monitor_job_executions(self, job_id: str, duration_minutes: int = 5):
        """Monitor job executions for a specified duration"""
        print(f"📊 Monitoring executions for job {job_id} for {duration_minutes} minutes...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                executions = await self.client.get_job_executions(job_id, page=1, page_size=10)
                
                if executions["executions"]:
                    latest_execution = executions["executions"][0]
                    print(f"  Latest execution: {latest_execution['status']} at {latest_execution['started_at']}")
                    
                    if latest_execution.get('completed_at'):
                        print(f"  Completed at: {latest_execution['completed_at']}")
                        if latest_execution.get('credits_used'):
                            print(f"  Credits used: {latest_execution['credits_used']}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"  Error monitoring job {job_id}: {e}")
                await asyncio.sleep(30)
    
    async def batch_trigger_jobs(self, job_ids: List[str]):
        """Trigger multiple jobs concurrently"""
        print(f"🚀 Triggering {len(job_ids)} jobs concurrently...")
        
        tasks = [self.client.trigger_scheduled_job(job_id) for job_id in job_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"  ❌ Failed to trigger job {job_ids[i]}: {result}")
            else:
                print(f"  ✅ Triggered job {job_ids[i]}: {result['execution_id']}")
    
    async def get_job_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about all jobs"""
        print("📈 Collecting job statistics...")
        
        all_jobs = await self.client.get_scheduled_jobs(page=1, page_size=100)
        
        stats = {
            "total_jobs": all_jobs["total"],
            "active_jobs": 0,
            "inactive_jobs": 0,
            "service_types": {},
            "recent_executions": 0,
            "total_credits_used": 0
        }
        
        for job in all_jobs["jobs"]:
            if job["is_active"]:
                stats["active_jobs"] += 1
            else:
                stats["inactive_jobs"] += 1
            
            service_type = job["service_type"]
            stats["service_types"][service_type] = stats["service_types"].get(service_type, 0) + 1
            
            # Get execution history for each job
            try:
                executions = await self.client.get_job_executions(job["id"], page=1, page_size=5)
                stats["recent_executions"] += len(executions["executions"])
                
                for execution in executions["executions"]:
                    if execution.get("credits_used"):
                        stats["total_credits_used"] += execution["credits_used"]
                        
            except Exception as e:
                print(f"  ⚠️ Could not get executions for job {job['id']}: {e}")
        
        return stats
    
    async def cleanup_old_jobs(self, days_old: int = 7):
        """Clean up jobs older than specified days"""
        print(f"🧹 Cleaning up jobs older than {days_old} days...")
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        jobs_to_delete = []
        
        all_jobs = await self.client.get_scheduled_jobs(page=1, page_size=100)
        
        for job in all_jobs["jobs"]:
            created_at = datetime.fromisoformat(job["created_at"].replace('Z', '+00:00'))
            if created_at < cutoff_date:
                jobs_to_delete.append(job["id"])
        
        if jobs_to_delete:
            print(f"  Found {len(jobs_to_delete)} jobs to delete")
            
            for job_id in jobs_to_delete:
                try:
                    await self.client.delete_scheduled_job(job_id)
                    print(f"  ✅ Deleted job {job_id}")
                except Exception as e:
                    print(f"  ❌ Failed to delete job {job_id}: {e}")
        else:
            print("  No old jobs found to delete")
    
    async def export_job_configurations(self) -> List[Dict[str, Any]]:
        """Export all job configurations for backup"""
        print("💾 Exporting job configurations...")
        
        all_jobs = await self.client.get_scheduled_jobs(page=1, page_size=100)
        configurations = []
        
        for job in all_jobs["jobs"]:
            config = {
                "job_name": job["job_name"],
                "service_type": job["service_type"],
                "cron_expression": job["cron_expression"],
                "job_config": job["job_config"],
                "is_active": job["is_active"],
                "created_at": job["created_at"]
            }
            configurations.append(config)
        
        print(f"  Exported {len(configurations)} job configurations")
        return configurations


async def main():
    """Main function demonstrating advanced scheduled jobs management"""
    # Initialize async client with API key from environment variable
    api_key = os.getenv("SGAI_API_KEY")
    if not api_key:
        print("❌ Error: SGAI_API_KEY environment variable not set")
        print("Please either:")
        print("  1. Set environment variable: export SGAI_API_KEY='your-api-key-here'")
        print("  2. Create a .env file with: SGAI_API_KEY=your-api-key-here")
        return

    async with AsyncClient(api_key=api_key) as client:
        print("🚀 Starting Advanced Scheduled Jobs Demo")
        print("=" * 60)
        
        manager = ScheduledJobManager(client)
        job_ids = []
        
        try:
            # Create different types of advanced jobs
            print("\n📅 Creating Advanced Scheduled Jobs:")
            print("-" * 40)
            
            # News monitoring job
            news_job_id = await manager.create_monitoring_job(
                website_url="https://techcrunch.com",
                job_name="TechCrunch News Monitor",
                cron_expression="0 */2 * * *"  # Every 2 hours
            )
            job_ids.append(news_job_id)
            
            # AI research job
            ai_job_id = await manager.create_data_collection_job(
                search_prompt="Latest developments in artificial intelligence and machine learning",
                job_name="AI Research Collector",
                cron_expression="0 8 * * 1"  # Every Monday at 8 AM
            )
            job_ids.append(ai_job_id)
            
            # E-commerce crawl job
            ecommerce_job_id = await manager.create_crawl_job(
                base_url="https://example-store.com",
                job_name="E-commerce Product Crawler",
                cron_expression="0 3 * * *"  # Daily at 3 AM
            )
            job_ids.append(ecommerce_job_id)
            
            # Get comprehensive statistics
            print("\n📈 Job Statistics:")
            print("-" * 40)
            stats = await manager.get_job_statistics()
            print(f"Total jobs: {stats['total_jobs']}")
            print(f"Active jobs: {stats['active_jobs']}")
            print(f"Inactive jobs: {stats['inactive_jobs']}")
            print(f"Service types: {stats['service_types']}")
            print(f"Recent executions: {stats['recent_executions']}")
            print(f"Total credits used: {stats['total_credits_used']}")
            
            # Trigger jobs concurrently
            print("\n🚀 Concurrent Job Triggering:")
            print("-" * 40)
            await manager.batch_trigger_jobs(job_ids)
            
            # Monitor executions
            print("\n📊 Monitoring Job Executions:")
            print("-" * 40)
            if job_ids:
                await manager.monitor_job_executions(job_ids[0], duration_minutes=2)
            
            # Export configurations
            print("\n💾 Exporting Job Configurations:")
            print("-" * 40)
            configurations = await manager.export_job_configurations()
            print(f"Exported {len(configurations)} configurations")
            
            # Demonstrate job management
            print("\n🔧 Advanced Job Management:")
            print("-" * 40)
            
            # Update job configurations
            if job_ids:
                print(f"Updating job {job_ids[0]}:")
                await client.update_scheduled_job(
                    job_ids[0],
                    job_name="Updated TechCrunch Monitor",
                    cron_expression="0 */1 * * *"  # Every hour
                )
                print("  ✅ Job updated successfully")
                
                # Pause and resume
                print(f"Pausing job {job_ids[0]}:")
                await client.pause_scheduled_job(job_ids[0])
                print("  ✅ Job paused")
                
                await asyncio.sleep(1)
                
                print(f"Resuming job {job_ids[0]}:")
                await client.resume_scheduled_job(job_ids[0])
                print("  ✅ Job resumed")
            
            # Cleanup demonstration (commented out to avoid deleting real jobs)
            # print("\n🧹 Cleanup Demonstration:")
            # print("-" * 40)
            # await manager.cleanup_old_jobs(days_old=1)
            
        except Exception as e:
            print(f"❌ Error during execution: {e}")
        
        finally:
            # Clean up created jobs
            print("\n🧹 Cleaning up created jobs:")
            print("-" * 40)
            for job_id in job_ids:
                try:
                    await client.delete_scheduled_job(job_id)
                    print(f"  ✅ Deleted job {job_id}")
                except Exception as e:
                    print(f"  ❌ Failed to delete job {job_id}: {e}")
        
        print("\n✅ Advanced Scheduled Jobs Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
