# models/race.py
"""
Data model for F1 race information and results

This module contains the Race data model class that represents individual
F1 races including basic information and podium results when available.

**Classes:**
    Race - Individual race information with podium results

**Author:** Lotherd
**Version:** 1.0.0
"""

from dataclasses import dataclass, field
from typing import List

@dataclass
class Race:
    """Data model representing an individual F1 race with details and results"""
    
    season: str
    round: str
    race_name: str
    circuit: str
    date: str
    podium: List[str] = field(default_factory=list)

    
    """
    * Creates a Race instance from Ergast API response data with optional results
    *
    * This class method parses race data from the Ergast API and optionally
    * includes podium results if results data is provided. It extracts the
    * top 3 finishers for the podium display.
    *
    * **@param** season String representing the F1 season year
    * **@param** race_data Dictionary containing race information from Ergast API
    * **@param** results_data Optional dictionary containing race results data
    * **@return** Race instance populated with race and podium information
    """
    @classmethod
    def from_ergast_data(cls, season: str, race_data: dict, results_data: dict | None = None) -> 'Race':
        podium = []
        if results_data:
            try:
                results = results_data['MRData']['RaceTable']['Races'][0]['Results']
                podium = [
                    f"{r['Driver']['givenName']} {r['Driver']['familyName']}" for r in results[:3]
                ]
            except Exception:
                podium = []
        return cls(
            season=season,
            round=race_data.get('round', ''),
            race_name=race_data.get('raceName', ''),
            circuit=race_data.get('Circuit', {}).get('circuitName', ''),
            date=race_data.get('date', ''),
            podium=podium
        )