"""
Git repository management for pushing consolidated data.
"""
import subprocess
from pathlib import Path
from loguru import logger
from tradestat_ingestor.config.settings import settings


def initialize_git_repo(repo_path: str = None) -> bool:
    """
    Initialize or verify git repository exists.
    """
    if repo_path is None:
        repo_path = Path.cwd()
    else:
        repo_path = Path(repo_path)
    
    try:
        # Check if .git exists
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            logger.info("Initializing git repository...")
            subprocess.run(
                ["git", "init"],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
        
        logger.success("Git repository ready")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize git repo: {str(e)}")
        return False


def add_remote_origin(remote_url: str = None, repo_path: str = None) -> bool:
    """
    Add remote origin if not already added.
    """
    if remote_url is None:
        remote_url = getattr(settings, 'git_repo_url', None)
    
    if not remote_url:
        logger.warning("No git_repo_url configured in settings")
        return False
    
    if repo_path is None:
        repo_path = Path.cwd()
    else:
        repo_path = Path(repo_path)
    
    try:
        # Check if origin exists
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Origin doesn't exist, add it
            subprocess.run(
                ["git", "remote", "add", "origin", remote_url],
                cwd=repo_path,
                capture_output=True,
                check=True
            )
            logger.info(f"Added remote origin: {remote_url}")
        else:
            logger.info(f"Remote origin already exists: {result.stdout.strip()}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to add remote origin: {str(e)}")
        return False


def push_file_to_git(file_path: str, trade_type: str = "export", hsn: str = None) -> bool:
    """
    Add, commit, and push a single file to git.
    Called after each HSN processing completes.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return False
    
    try:
        repo_path = Path.cwd()
        
        # Add file
        subprocess.run(
            ["git", "add", str(file_path)],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        
        # Commit with meaningful message
        commit_msg = f"[{trade_type.upper()}] Add consolidated export for HSN {hsn}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=repo_path,
            capture_output=True,
            check=False  # Allow failure if nothing to commit
        )
        
        # Push to remote
        branch = getattr(settings, 'git_branch', 'main')
        subprocess.run(
            ["git", "push", "origin", branch],
            cwd=repo_path,
            capture_output=True,
            check=True
        )
        
        logger.success(f"Pushed to git: {file_path.name}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Git operation failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to push file to git: {str(e)}")
        return False


def batch_push_to_git(trade_type: str = "export", batch_size: int = 100) -> dict:
    """
    Batch push all consolidated exports from a trade type.
    Useful for pushing all completed HSNs at once.
    """
    from tradestat_ingestor.utils.constants import EXPORT_PATH
    
    export_dir = Path(EXPORT_PATH) / trade_type
    
    if not export_dir.exists():
        logger.warning(f"Export directory not found: {export_dir}")
        return {"pushed": 0, "failed": 0}
    
    pushed = 0
    failed = 0
    
    try:
        # Find all consolidated export files
        export_files = list(export_dir.glob(f"*/*_{trade_type}.json"))
        logger.info(f"Found {len(export_files)} consolidated exports to push")
        
        # Push in batches
        for i, export_file in enumerate(export_files):
            hsn = export_file.parent.name
            if push_file_to_git(str(export_file), trade_type, hsn):
                pushed += 1
            else:
                failed += 1
            
            # Log progress every batch_size
            if (i + 1) % batch_size == 0:
                logger.info(f"Pushed {i + 1}/{len(export_files)} files")
        
        logger.success(f"Batch push complete: {pushed} pushed, {failed} failed")
        return {"pushed": pushed, "failed": failed}
        
    except Exception as e:
        logger.error(f"Batch push failed: {str(e)}")
        return {"pushed": pushed, "failed": failed}
