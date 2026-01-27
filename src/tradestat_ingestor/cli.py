import typer

from tradestat_ingestor.config.settings import settings
from tradestat_ingestor.core.session import TradeStatSession
from tradestat_ingestor.core.scraper import scrape_export
from tradestat_ingestor.core.parser import parse_commodity_from_html
from tradestat_ingestor.storage.parsed import save_parsed_json
from tradestat_ingestor.storage.export import merge_years_to_export, save_consolidated_export
from tradestat_ingestor.storage.git import initialize_git_repo, add_remote_origin, batch_push_to_git
from tradestat_ingestor.utils.constants import EXPORT_PATH
from tradestat_ingestor.tasks.batch_scraper import scrape_all_years
from tradestat_ingestor.tasks.batch_manager import (
    load_hsn_codes_from_file,
    submit_batch_jobs,
    get_queue_status,
    get_batch_results,
)

app = typer.Typer(help="TradeStat data ingestion CLI")


@app.command()
def scrape(
    hsn: str = typer.Option(..., help="HSN code (e.g. 09011112)"),
    year: str = typer.Option(..., help="Financial year (e.g. 2024)"),
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Perform a single scrape, parse data, and save as JSON.
    """
    if trade.lower() != "export":
        raise typer.BadParameter("Only EXPORT supported for now")

    session = TradeStatSession(
        base_url=settings.base_url,
        user_agent=settings.user_agent,
    )

    state = session.bootstrap(EXPORT_PATH)
    html = scrape_export(session.session, settings.base_url, hsn, year, state)

    # Parse HTML to structured data
    parsed_data = parse_commodity_from_html(html, hsn=hsn, year=year)
    
    # Save only JSON (no HTML)
    save_parsed_json(trade, hsn, year, parsed_data)

    typer.echo("Single scrape completed successfully")


@app.command()
def scrape_years(
    hsn: str = typer.Option(..., help="HSN code (e.g. 09011112)"),
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Scrape data for all available years.
    Shows success/failure status for each year.
    """
    if trade.lower() != "export":
        raise typer.BadParameter("Only EXPORT supported for now")

    typer.echo(f"Starting batch scrape for HSN={hsn}")
    results = scrape_all_years(hsn, trade)
    
    typer.echo("\n" + "="*60)
    typer.echo(f"Batch scrape completed for HSN={hsn}")
    typer.echo("="*60)
    
    if results["successful"]:
        typer.echo("\nSuccessfully scraped:")
        for item in results["successful"]:
            typer.echo(f"  Y Year {item['year']}: {item['countries_count']} countries")
    
    if results["failed"]:
        typer.echo("\nFailed to scrape:")
        for item in results["failed"]:
            typer.echo(f"  N Year {item['year']}: {item['reason']}")
    
    typer.echo(f"\nTotal: {len(results['successful'])} successful, {len(results['failed'])} failed")


@app.command()
def export_data(
    hsn: str = typer.Option(..., help="HSN code (e.g. 09011112)"),
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Merge all year data into a single consolidated JSON export file.
    """
    typer.echo(f"Consolidating data for HSN={hsn}")
    
    consolidated = merge_years_to_export(trade, hsn)
    
    if not consolidated:
        typer.echo("Error: No data to consolidate")
        raise typer.Exit(1)
    
    export_file = save_consolidated_export(trade, hsn, consolidated)
    
    typer.echo("\n" + "="*60)
    typer.echo("Data consolidated successfully!")
    typer.echo("="*60)
    typer.echo(f"Export file: {export_file}")
    typer.echo(f"Commodity: {consolidated['commodity'].get('description', 'N/A')}")
    typer.echo(f"Years consolidated: {consolidated['metadata']['years_count']}")
    typer.echo(f"Total countries: {sum(len(y.get('countries', [])) for y in consolidated['years'].values())}")


@app.command(name="batch-submit")
def batch_submit(
    file: str = typer.Option(..., help="Path to CSV/TXT file with HSN codes (one per line or 'hsn_code' column)"),
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Submit batch jobs from a file for scraping.
    File format: CSV with 'hsn_code' column or TXT with one HSN per line.
    """
    hsn_codes = load_hsn_codes_from_file(file)
    
    if not hsn_codes:
        typer.echo("Error: No HSN codes loaded from file")
        raise typer.Exit(1)
    
    typer.echo(f"Loaded {len(hsn_codes)} HSN codes")
    typer.echo(f"Submitting to Redis Queue...")
    
    results = submit_batch_jobs(hsn_codes, trade)
    
    typer.echo("\n" + "="*60)
    typer.echo("Batch submission completed")
    typer.echo("="*60)
    typer.echo(f"Submitted: {len(results['submitted'])}")
    typer.echo(f"Failed: {len(results['failed'])}")
    
    if results["submitted"]:
        typer.echo(f"\nFirst 5 jobs:")
        for job in results["submitted"][:5]:
            typer.echo(f"  HSN={job['hsn']}, Job ID={job['job_id']}")


@app.command(name="queue-status")
def queue_status():
    """
    Check status of queued jobs.
    """
    status = get_queue_status()
    
    typer.echo("\n" + "="*60)
    typer.echo("Queue Status")
    typer.echo("="*60)
    typer.echo(f"Jobs queued: {status['queued']}")
    
    if status["jobs"]:
        typer.echo("\nQueued jobs:")
        for job_id, job_info in list(status["jobs"].items())[:10]:
            typer.echo(f"  {job_info['hsn']}: {job_info['status']} (ID: {job_id[:8]}...)")


@app.command(name="batch-results")
def batch_results(
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Show batch processing results and statistics.
    """
    results = get_batch_results(trade)
    
    typer.echo("\n" + "="*60)
    typer.echo("Batch Processing Results")
    typer.echo("="*60)
    typer.echo(f"Total HSN codes: {results['total_hsn']}")
    typer.echo(f"Completed: {len(results['completed'])}")
    typer.echo(f"Pending: {len(results['pending'])}")
    
    if results["completed"]:
        total_countries = sum(r["countries"] for r in results["completed"])
        avg_countries = total_countries / len(results["completed"]) if results["completed"] else 0
        typer.echo(f"\nCompletion Statistics:")
        typer.echo(f"  Total countries scraped: {total_countries}")
        typer.echo(f"  Avg countries per HSN: {avg_countries:.1f}")
        
        typer.echo(f"\nFirst 10 completed HSNs:")
        for item in results["completed"][:10]:
            typer.echo(f"  {item['hsn']}: {item['years']} years, {item['countries']} countries")


@app.command(name="git-init")
def git_init():
    """
    Initialize and configure git repository for remote data storage.
    """
    typer.echo("Initializing Git repository...")
    
    if not initialize_git_repo():
        typer.echo("Error: Failed to initialize git repo")
        raise typer.Exit(1)
    
    if not settings.git_repo_url:
        typer.echo("Error: GIT_REPO_URL not configured in .env")
        raise typer.Exit(1)
    
    if not add_remote_origin():
        typer.echo("Error: Failed to add remote origin")
        raise typer.Exit(1)
    
    typer.echo("\n" + "="*60)
    typer.echo("Git repository configured successfully!")
    typer.echo("="*60)
    typer.echo(f"Repository: {settings.git_repo_url}")
    typer.echo(f"Branch: {settings.git_branch}")
    typer.echo("\nData will be pushed automatically during batch processing")


@app.command(name="git-push-all")
def git_push_all(
    trade: str = typer.Option("export", help="Trade type (export/import)"),
):
    """
    Push all completed consolidated exports to git repository.
    Useful for manual batch push or recovery.
    """
    if not settings.git_repo_url:
        typer.echo("Error: GIT_REPO_URL not configured in .env")
        raise typer.Exit(1)
    
    typer.echo(f"Pushing all {trade} data to Git...")
    results = batch_push_to_git(trade)
    
    typer.echo("\n" + "="*60)
    typer.echo("Git batch push completed")
    typer.echo("="*60)
    typer.echo(f"Pushed: {results['pushed']}")
    typer.echo(f"Failed: {results['failed']}")


def main():
    app()


if __name__ == "__main__":
    app()
