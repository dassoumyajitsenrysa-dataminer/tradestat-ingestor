"""
Change Detection & Version Control Module

Tracks data changes between scraping incidents and generates comprehensive
delta reports for data quality monitoring and compliance tracking.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from loguru import logger


class ChangeDetector:
    """Detects and tracks changes in scraped data between versions."""
    
    def __init__(self, data_dir: Path = Path("src/data/raw")):
        """
        Initialize change detector.
        
        Args:
            data_dir: Root directory for storing version history
        """
        self.data_dir = data_dir
        self.versions_dir = data_dir / ".versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def get_version_history_path(self, feature: str, trade_type: str, hsn: str) -> Path:
        """Get path to version history file for a specific HSN."""
        return self.versions_dir / f"{feature}_{trade_type}_{hsn}_history.json"
    
    def get_previous_version(self, feature: str, trade_type: str, hsn: str, year: str) -> Optional[Dict]:
        """Load previous version of data if it exists."""
        history_path = self.get_version_history_path(feature, trade_type, hsn)
        
        if not history_path.exists():
            return None
        
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
                if year in history and 'snapshot' in history[year]:
                    return history[year]['snapshot']
        except Exception as e:
            logger.warning(f"Could not load version history: {e}")
        
        return None
    
    def calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculate MD5 checksum of data for integrity verification."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def detect_changes(
        self,
        current_data: Dict[str, Any],
        previous_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect changes between current and previous data.
        
        Returns comprehensive delta information including:
        - Added countries
        - Removed countries
        - Modified values per country
        - Statistics changes
        """
        if previous_data is None:
            return {
                "status": "NEW_EXTRACTION",
                "change_type": "INITIAL_DATA",
                "has_changes": True,
                "changes_summary": {
                    "countries_added": [],
                    "countries_removed": [],
                    "countries_modified": [],
                    "values_changed": {}
                },
                "change_metrics": {
                    "total_changes": 0,
                    "percent_change": 100.0,
                    "data_drift": "BASELINE"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        current_countries = {c['country']: c for c in current_data.get('countries', [])}
        previous_countries = {c['country']: c for c in previous_data.get('countries', [])}
        
        # Detect added/removed countries
        countries_added = list(set(current_countries.keys()) - set(previous_countries.keys()))
        countries_removed = list(set(previous_countries.keys()) - set(current_countries.keys()))
        
        # Detect modified values
        countries_modified = []
        detailed_changes = {}
        
        for country in set(current_countries.keys()) & set(previous_countries.keys()):
            curr = current_countries[country]
            prev = previous_countries[country]
            
            changes = self._compare_country_data(curr, prev)
            if changes:
                countries_modified.append(country)
                detailed_changes[country] = changes
        
        # Calculate change metrics
        total_changes = len(countries_added) + len(countries_removed) + len(countries_modified)
        total_countries = len(current_countries)
        percent_change = (total_changes / max(total_countries, len(previous_countries))) * 100
        
        # Determine data drift level
        if percent_change == 0:
            data_drift = "NO_CHANGE"
        elif percent_change < 5:
            data_drift = "MINIMAL"
        elif percent_change < 15:
            data_drift = "MODERATE"
        elif percent_change < 30:
            data_drift = "SIGNIFICANT"
        else:
            data_drift = "CRITICAL"
        
        return {
            "status": "COMPARISON_COMPLETE",
            "change_type": "DATA_UPDATE",
            "has_changes": total_changes > 0,
            "changes_summary": {
                "countries_added": countries_added,
                "countries_removed": countries_removed,
                "countries_modified": countries_modified,
                "detailed_changes": detailed_changes
            },
            "change_metrics": {
                "total_changes": total_changes,
                "percent_change": round(percent_change, 2),
                "data_drift": data_drift,
                "countries_added_count": len(countries_added),
                "countries_removed_count": len(countries_removed),
                "countries_modified_count": len(countries_modified)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def _compare_country_data(self, current: Dict, previous: Dict) -> Dict[str, Any]:
        """Compare data for a single country between versions."""
        changes = {}
        
        # Compare USD values
        curr_usd = current.get('values_usd', {})
        prev_usd = previous.get('values_usd', {})
        
        for key in ['y2023_2024', 'y2024_2025', 'pct_growth']:
            curr_val = curr_usd.get(key)
            prev_val = prev_usd.get(key)
            
            if curr_val != prev_val:
                changes[f'usd_{key}'] = {
                    'previous': prev_val,
                    'current': curr_val,
                    'difference': (curr_val - prev_val) if (curr_val and prev_val) else None,
                    'percent_change': self._calc_percent_change(prev_val, curr_val)
                }
        
        # Compare quantity values
        curr_qty = current.get('values_quantity', {})
        prev_qty = previous.get('values_quantity', {})
        
        for key in ['y2023_2024', 'y2024_2025', 'pct_growth']:
            curr_val = curr_qty.get(key)
            prev_val = prev_qty.get(key)
            
            if curr_val != prev_val:
                changes[f'qty_{key}'] = {
                    'previous': prev_val,
                    'current': curr_val,
                    'difference': (curr_val - prev_val) if (curr_val and prev_val) else None,
                    'percent_change': self._calc_percent_change(prev_val, curr_val)
                }
        
        return changes
    
    def _calc_percent_change(self, previous: Optional[float], current: Optional[float]) -> Optional[float]:
        """Calculate percentage change between two values."""
        if not previous or not current:
            return None
        if previous == 0:
            return None
        return round(((current - previous) / abs(previous)) * 100, 2)
    
    def save_version(
        self,
        parsed_data: Dict[str, Any],
        feature: str,
        trade_type: str,
        hsn: str,
        year: str,
        changes: Dict[str, Any]
    ) -> None:
        """Save current version to history."""
        history_path = self.get_version_history_path(feature, trade_type, hsn)
        
        # Load existing history or create new
        if history_path.exists():
            with open(history_path, 'r') as f:
                history = json.load(f)
        else:
            history = {}
        
        # Add new version
        history[year] = {
            "timestamp": datetime.now().isoformat(),
            "checksum": self.calculate_checksum(parsed_data),
            "snapshot": parsed_data,
            "changes": changes,
            "commodity": parsed_data.get('commodity', {}),
            "data_quality": parsed_data.get('data_quality', {})
        }
        
        # Save updated history
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2, default=str)
        
        logger.info(f"Version saved: {feature}/{trade_type}/{hsn}/{year}")
    
    def generate_changelog(
        self,
        feature: str,
        trade_type: str,
        hsn: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Generate comprehensive changelog for all versions of a specific HSN."""
        history_path = self.get_version_history_path(feature, trade_type, hsn)
        
        if not history_path.exists():
            return None
        
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            changelog = []
            years = sorted(history.keys())
            
            for year in years:
                entry = history[year]
                changelog.append({
                    "year": year,
                    "timestamp": entry.get('timestamp'),
                    "checksum": entry.get('checksum'),
                    "data_quality": entry.get('data_quality'),
                    "changes": entry.get('changes'),
                    "commodity": entry.get('commodity')
                })
            
            return changelog
        
        except Exception as e:
            logger.error(f"Error generating changelog: {e}")
            return None
    
    def get_comparison_report(
        self,
        feature: str,
        trade_type: str,
        hsn: str,
        year: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed comparison report between current and previous version."""
        history_path = self.get_version_history_path(feature, trade_type, hsn)
        
        if not history_path.exists():
            return None
        
        try:
            with open(history_path, 'r') as f:
                history = json.load(f)
            
            if year not in history:
                return None
            
            current = history[year]
            
            # Find previous year
            years = sorted([y for y in history.keys() if y < year], reverse=True)
            
            if not years:
                return {
                    "comparison_type": "FIRST_VERSION",
                    "current_year": year,
                    "previous_year": None,
                    "current_data": current,
                    "message": "This is the first recorded version"
                }
            
            previous_year = years[0]
            previous = history[previous_year]
            
            return {
                "comparison_type": "VERSION_COMPARISON",
                "current_year": year,
                "previous_year": previous_year,
                "year_gap": int(year) - int(previous_year),
                "current_data": current,
                "previous_data": previous,
                "changes": current.get('changes'),
                "timestamp_current": current.get('timestamp'),
                "timestamp_previous": previous.get('timestamp')
            }
        
        except Exception as e:
            logger.error(f"Error generating comparison report: {e}")
            return None

