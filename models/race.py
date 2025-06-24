from dataclasses import dataclass, field
from typing import List

@dataclass
class Race:
    season: str
    round: str
    race_name: str
    circuit: str
    date: str
    podium: List[str] = field(default_factory=list)

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