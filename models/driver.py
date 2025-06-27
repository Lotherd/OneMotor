# models/driver.py
"""
Data models for drivers, constructors, and championship standings

This module contains the data model classes that represent F1 drivers,
constructor teams, and driver championship standings. These models
handle data parsing from the Ergast API format.

**Classes:**
    Driver - Individual driver information and details
    Constructor - Team/constructor information and details  
    DriverStanding - Driver's position and points in championship

**Author:** Lotherd
**Version:** 1.0.0
"""

from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Driver:
    """Data model representing an individual F1 driver with all personal details"""
    
    driver_id: str
    permanent_number: Optional[str]
    code: Optional[str]
    given_name: str
    family_name: str
    date_of_birth: Optional[str]
    nationality: str
    url: Optional[str]
    
    
    """
    * Constructs and returns the driver's complete full name
    *
    * This property combines the driver's given name and family name
    * to create a readable full name for display purposes.
    *
    * **@return** String containing the driver's full name
    """
    @property
    def full_name(self) -> str:
        return f"{self.given_name} {self.family_name}"
    
    
    """
    * Creates a Driver instance from Ergast API response data
    *
    * This class method parses the JSON data structure returned by the
    * Ergast API and creates a properly structured Driver object with
    * all the available driver information.
    *
    * **@param** data Dictionary containing driver data from Ergast API
    * **@return** Driver instance populated with the provided data
    """
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'Driver':
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
    """Data model representing an F1 constructor/team with basic information"""
    
    constructor_id: str
    name: str
    nationality: str
    url: Optional[str]
    
    
    """
    * Creates a Constructor instance from Ergast API response data
    *
    * This class method parses the JSON data structure returned by the
    * Ergast API and creates a properly structured Constructor object
    * with all the available team information.
    *
    * **@param** data Dictionary containing constructor data from Ergast API
    * **@return** Constructor instance populated with the provided data
    """
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'Constructor':
        return cls(
            constructor_id=data.get('constructorId', ''),
            name=data.get('name', ''),
            nationality=data.get('nationality', ''),
            url=data.get('url')
        )

@dataclass
class DriverStanding:
    """Data model representing a driver's championship position and statistics"""
    
    position: int
    position_text: str
    points: float
    wins: int
    driver: Driver
    constructors: List[Constructor]
    
    
    """
    * Creates a DriverStanding instance from Ergast API response data
    *
    * This class method parses the complex JSON data structure returned by
    * the Ergast API standings endpoint and creates a complete DriverStanding
    * object including embedded Driver and Constructor objects.
    *
    * **@param** data Dictionary containing standing data from Ergast API
    * **@return** DriverStanding instance with all related objects populated
    """
    @classmethod
    def from_ergast_data(cls, data: dict) -> 'DriverStanding':
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