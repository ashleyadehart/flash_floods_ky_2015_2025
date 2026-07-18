# ERD Diagram Generation Script
## This code was generated via Claude Code. 
## The purpose of this code is to create a database schema based on the provided Mermaid ERD diagram. 

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from eralchemy2 import render_er

Base = declarative_base()


class EventInfo(Base):
    __tablename__ = 'event_info'

    event_id = Column(String, primary_key=True)
    county_name = Column(String)
    begin_date = Column(DateTime)
    end_date = Column(DateTime)
    begin_time = Column(DateTime)
    end_time = Column(DateTime)
    begin_location = Column(String)
    end_location = Column(String)
    begin_range = Column(Float)
    end_range = Column(Float)
    begin_lat = Column(Float)
    begin_lon = Column(Float)
    end_lat = Column(Float)
    end_lon = Column(Float)
    year = Column(Integer)
    duration_minutes = Column(Float)
    duration_hours = Column(Float)

    impact_data = relationship(
        "ImpactData", back_populates="event", uselist=False,
        cascade="all, delete-orphan"
    )
    weather_conditions = relationship(
        "WeatherConditions", back_populates="event", uselist=False,
        cascade="all, delete-orphan"
    )
    moon_sun_data = relationship(
        "MoonData", back_populates="event", uselist=False,
        cascade="all, delete-orphan"
    )
    oni_data = relationship(
        "OniData", back_populates="event", uselist=False,
        cascade="all, delete-orphan"
    )
    nlcd_data = relationship(
        "NlcdData", back_populates="event", uselist=False,
        cascade="all, delete-orphan"
    )


class ImpactData(Base):
    __tablename__ = 'impact_data'

    event_id = Column(String, ForeignKey('event_info.event_id', ondelete="CASCADE"), primary_key=True)
    deaths_direct = Column(Integer)
    deaths_indirect = Column(Integer)
    injuries_direct = Column(Integer)
    injuries_indirect = Column(Integer)
    damage_property_num = Column(Integer)
    damage_number_crops = Column(Integer)

    event = relationship("EventInfo", back_populates="impact_data")


class WeatherConditions(Base):
    __tablename__ = 'weather_conditions'

    event_id = Column(String, ForeignKey('event_info.event_id', ondelete="CASCADE"), primary_key=True)
    maxtemp_f = Column(Float)
    mintemp_f = Column(Float)
    avgtemp_f = Column(Float)
    maxwind_mph = Column(Float)
    totalprecip_in = Column(Float)
    avgvis_miles = Column(Float)
    avghumidity = Column(Float)
    condition_text = Column(String)
    condition_code = Column(Integer)
    uv = Column(Float)
    daily_will_it_rain = Column(Integer)
    daily_chance_of_rain = Column(Integer)

    event = relationship("EventInfo", back_populates="weather_conditions")


class MoonData(Base):
    __tablename__ = 'moon_sun_data'

    event_id = Column(String, ForeignKey('event_info.event_id', ondelete="CASCADE"), primary_key=True)
    sun_altitude_deg = Column(Float)
    sun_azimuth_deg = Column(Float)
    sunrise_utc = Column(String)
    sunset_utc = Column(String)
    moon_altitude_deg = Column(Float)
    moon_azimuth_deg = Column(Float)
    moon_phase_name = Column(String)
    moon_illumination_pct = Column(Float)

    event = relationship("EventInfo", back_populates="moon_sun_data")


class OniData(Base):
    __tablename__ = 'oni_data'

    event_id = Column(String, ForeignKey('event_info.event_id', ondelete="CASCADE"), primary_key=True)
    oni_season = Column(String)
    year = Column(Integer)
    oni_anomaly = Column(Float)
    enso_phase = Column(String)

    event = relationship("EventInfo", back_populates="oni_data")


class NlcdData(Base):
    __tablename__ = 'nlcd_data'

    event_id = Column(String, ForeignKey('event_info.event_id', ondelete="CASCADE"), primary_key=True)
    nlcd_code = Column(Integer)
    nlcd_class = Column(String)
    elevation_m = Column(Float)
    impervious_surface_pct = Column(Float)

    event = relationship("EventInfo", back_populates="nlcd_data")


def main():
    """Renders the ERD diagram directly from the schema metadata into the plots folder."""
    output_dir = 'plots'
    output_path = os.path.join(output_dir, 'erd_diagram.png')

    os.makedirs(output_dir, exist_ok=True)

    try:
        render_er(Base.metadata, output_path)
        print(f"Success! ERD image file saved to: {output_path}")
    except Exception as e:
        print(f"Error generating ERD image. Please verify eralchemy2 and pygraphviz are installed. Details: {e}")


if __name__ == "__main__":
    main()