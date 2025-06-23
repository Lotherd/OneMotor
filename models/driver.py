from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Driver:
    """Modelo de datos para un piloto"""
    driver_id: str
    permanent_number: Optional[str]
    code: Optional[str]
    given_name: str
    family_name: str
    date_of_birth: Optional[str]
    nationality: str
    url: Optional[str]
    
    @property
    def full_name(self) -> str:
        """Nombre completo del piloto"""
        return f"{self.given_name} {self.family_name}"
    
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'Driver':
        """Crear instancia desde datos de Ergast API"""
        return cls(
            driver_id=data.get('driverId', ''),
            permanent_number=data.get('permanentNumber'),
            code=data.get('code'),
            given_name=data.get('givenName', ''),
            family_name=data.get('familyName', ''),
            date_of_birth=data.get('dateOfBirth'),
            nationality=data.get('nationality', ''),
            url=data.get('url')
        )

@dataclass
class Constructor:
    """Modelo de datos para un constructor/equipo"""
    constructor_id: str
    name: str
    nationality: str
    url: Optional[str]
    
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'Constructor':
        """Crear instancia desde datos de Ergast API"""
        return cls(
            constructor_id=data.get('constructorId', ''),
            name=data.get('name', ''),
            nationality=data.get('nationality', ''),
            url=data.get('url')
        )

@dataclass
class DriverStanding:
    """Modelo de datos para la posición de un piloto en el campeonato"""
    position: int
    position_text: str
    points: float
    wins: int
    driver: Driver
    constructors: List[Constructor]
    
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'DriverStanding':
        """Crear instancia desde datos de Ergast API"""
        driver = Driver.from_ergast_data(data['Driver'])
        constructors = [Constructor.from_ergast_data(c) for c in data['Constructors']]
        
        return cls(
            position=int(data.get('position', 0)),
            position_text=data.get('positionText', ''),
            points=float(data.get('points', 0)),
            wins=int(data.get('wins', 0)),
            driver=driver,
            constructors=constructors
        )