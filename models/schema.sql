PRAGMA foreign_keys = ON;

----------------------------------------------------------------------
-- 0. COUNTRIES
----------------------------------------------------------------------
CREATE TABLE countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,							-- Unique ID
    iso_code TEXT NOT NULL UNIQUE,									-- Standard ISO 3166-1 alpha-3 code (e.g., 'USA', 'FRA', 'JPN')
    name TEXT NOT NULL UNIQUE										-- Full country name (e.g., 'United States', 'France')
);

---------------------------------------------------------------------
-- 1. AGENCIES
---------------------------------------------------------------------
CREATE TABLE agencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,							-- Unique ID
    name TEXT NOT NULL,												-- Agency name (e.g., 'NASA', 'ESA')
    country_id INTEGER,												-- Foreign Key to 'countries'			
    founding_year INTEGER,											-- Year of creation
    details TEXT,													-- Description
    FOREIGN KEY(country_id) REFERENCES countries(id) ON DELETE SET NULL
);

----------------------------------------------------------------------
-- 2. CREW
----------------------------------------------------------------------
CREATE TABLE crew (
    id INTEGER PRIMARY KEY AUTOINCREMENT,               			-- Unique ID
    agency_id INTEGER NOT NULL,                 					-- Foreign Key to 'agencies'
    name TEXT NOT NULL,                      						-- Full name of the crew member
    status TEXT CHECK (status IN ('active','retired','unknown')),	-- Operational status
    date_of_birth TEXT,                      						-- Date of birth (ISO 8601 format)
    nationality TEXT,                        						-- Nationality of the crew member
    gender TEXT CHECK (gender IN ('male','female','other',			-- Gender
    'unknown')),
    rank TEXT,                              						-- Rank or position within the agency (e.g., Commander, Pilot, Specialist)
    missions INTEGER,                      			 				-- Number of space missions completed
    total_time_in_space REAL,               		 				-- Total time spent in space (days)
    image TEXT,                             						-- URL of the crew member's image
    detail TEXT,                          							-- Short biography or career notes
    FOREIGN KEY(agency_id) REFERENCES agencies(id) ON DELETE CASCADE
);

----------------------------------------------------------------------
-- 3. ROCKETS
----------------------------------------------------------------------
CREATE TABLE rockets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,							-- Unique ID
    agency_id INTEGER NOT NULL,          							-- Foreign Key to 'agencies'
    name TEXT NOT NULL,                  							-- Rocket name 
    type TEXT,                           							-- Rocket type 
    active INTEGER CHECK (active IN (0,1)),							-- Boolean: Is the rocket currently in use (1=True, 0=False)
    stages INTEGER,                      							-- Number of stages
    boosters INTEGER,                    							-- Number of side boosters
    cost_per_launch REAL,                							-- Cost per launch in USD
    success_rate_pct REAL,              							-- Percentage of successful launches
    first_flight TEXT,                   							-- Date of the first flight (ISO 8601)
    description TEXT,                    							-- Short description of the rocket
    image TEXT,                          							-- URL of a single representative image
    height_meters REAL,                  							-- Height in meters
    diameter_meters REAL,                							-- Diameter in meters
    mass_kg REAL,                        							-- Mass in kilograms
    engine_type TEXT,                    							-- Engine type
    engine_version TEXT,				 							-- Engine version
    engine_layout TEXT,												-- Engine layout
    engine_loss_max INTEGER,       				      				-- Max number of engines that can fail
    propellant_1 TEXT,            				       				-- Primary propellant
    propellant_2 TEXT,             				      				-- Secondary propellant
    thrust_sea_level_kN REAL,      				      				-- Thrust at sea level in kilonewtons
    thrust_vacuum_kN REAL,          				    			-- Thrust in vacuum in kilonewtons
    landing_legs_number INTEGER,									-- Number of landing legs
    landing_legs_material TEXT,										-- Material of landing legs
    details TEXT,													-- Description
    FOREIGN KEY(agency_id) REFERENCES agencies(id) ON DELETE CASCADE
);

----------------------------------------------------------------------
-- 4. PAYLOADS
----------------------------------------------------------------------
CREATE TABLE payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,							-- Unique ID
    name TEXT,                          							-- Name of the payload
    type TEXT CHECK (type IN ('Satellite','Capsule',				-- Payload type or category
    'Crewed spacecraft','Cargo spacecraft','Telescope',
    'Probe','Rover','Space station module','Other')),               				
    reused INTEGER CHECK (reused IN (0,1)),  						-- Reuse indicator (1 = reused, 0 = not reused)
    mass_kg REAL,                        							-- Total mass of the payload in kilograms
    manufacturer TEXT,                   							-- Manufacturer or organization responsible for the payload
    orbit TEXT CHECK (orbit IN ('LEO','MEO','GEO','HEO',			-- Orbit type
    'SSO','Polar','TLI','Mars Transfer','Other')),              				
    reference_system TEXT CHECK (reference_system IN 				-- Orbital reference system
    ('Geocentric','Heliocentric','Selenocentric',
    'Barycentric','Other')),  				
    regime TEXT CHECK (regime IN ('low-earth',						-- Specific orbital regime
    'sun-synchronous','geostationary','other')),
    longitude REAL,                   				   				-- Orbital longitude in degrees
    semi_major_axis_km REAL,        				    			-- Semi-major axis of the orbit in kilometers
    eccentricity REAL,              				    			-- Orbital eccentricity (0 = circular, close to 1 = highly elliptical)
    periapsis_km REAL,             				      				-- Closest point to Earth in kilometers
    apoapsis_km REAL,              					    			-- Farthest point from Earth in kilometers
    inclination_deg REAL,         				       				-- Orbital inclination in degrees relative to the equator
    period_min REAL,                 				    			-- Orbital period in minutes
    lifespan_years REAL,              				   				-- Expected operational lifespan in years
    epoch TEXT,                     				    			-- Reference time of the orbital elements (ISO 8601 format)
    mean_motion REAL,                				    			-- Mean motion (orbits per day)
    raan REAL,                       				    			-- Right Ascension of the Ascending Node (°)
    arg_of_pericenter REAL,          				    			-- Argument of pericenter (°)
    mean_anomaly REAL,                				    			-- Mean anomaly at epoch (°)
    details TEXT,													-- Description
);

----------------------------------------------------------------------
-- 5. LAUNCHPADS
----------------------------------------------------------------------
CREATE TABLE launchpads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,							-- Unique ID
    agency_id INTEGER NOT NULL,             						-- Foreign Key to 'agencies' (owner/operator)
    name TEXT,                           							-- Name of the launchpads
    status TEXT CHECK (status IN ('active','inactive','retired',	-- Operational status
    'under construction','planned','unknown')),     				
    locality TEXT,                       							-- City/Locality
    region TEXT,                         							-- State/Region
    timezone TEXT,                       							-- Timezone
    latitude REAL,                       							-- Geographic latitude
    longitude REAL,                      							-- Geographic longitude
    launch_attempts INTEGER,             							-- Total launch attempts from this pad
    launch_successes INTEGER,            							-- Total launch successes from this pad
    details TEXT,                        							-- Detailed description of the pad
    FOREIGN KEY(agency_id) REFERENCES agencies(id) ON DELETE CASCADE
);

----------------------------------------------------------------------
-- 5. LANDPADS
----------------------------------------------------------------------
CREATE TABLE landpads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  							-- Unique ID
    name TEXT,            											-- Name of the landpad
    status TEXT NOT NULL CHECK (status IN ('active','inactive',		-- Operational status
    'unknown','retired','lost','under construction')),
    type TEXT CHECK (type IN ('ASDS','RTLS','Ocean','Autonomous',	-- Type of landing pad 
    'Other')),
    locality TEXT,        											-- Nearby city or locality
    region TEXT,          											-- Region or state
    latitude REAL,        											-- Latitude coordinate
    longitude REAL,       											-- Longitude coordinate
    landing_attempts INTEGER DEFAULT 0,   							-- Number of landing attempts
    landing_successes INTEGER DEFAULT 0,  							-- Number of successful landings
    details TEXT          											-- Additional descriptive details
);

----------------------------------------------------------------------
-- 7. LAUNCHES
----------------------------------------------------------------------
CREATE TABLE launches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,              				-- Unique ID
    landpad_id INTEGER,                                           	-- Foreign Key to 'landpads'
    launchpad_id INTEGER,                                			-- Foreign Key to 'launchpads' 
    flight_number INTEGER,               							-- Sequential flight number
    name TEXT,                           							-- Launch name
    date_utc TEXT,                       							-- Launch date and time (ISO 8601 UTC)
    date_unix INTEGER,                   							-- Launch date and time (Unix timestamp)             
	tdb INTEGER CHECK (tdb IN (0,1)),                 				-- Boolean: To Be Determined (0 = No, 1 = Yes)
	net INTEGER CHECK (net IN (0,1)),                 				-- Boolean: No Earlier Than (0 = No, 1 = Yes)
	window INTEGER,                                   				-- Launch window duration in seconds
	rocket_id INTEGER,                                   			-- Foreign Key to 'rockets.id' (TEXT)
	success INTEGER CHECK (success IN (0,1)),        				-- Boolean: Was the launch successful (0 = No, 1 = Yes)
	upcoming INTEGER CHECK (upcoming IN (0,1)),      				-- Boolean: Is the launch upcoming (0 = No, 1 = Yes)

	fairing_status TEXT CHECK (fairing_status IN ('None'			-- Status of the payload fairing
	,'Expended','Reused','Attempted Recovery')), 
 	landing_attempt INTEGER CHECK (landing_attempt IN (0,1)),   	-- Boolean: Was a landing attempt made
    landing_success INTEGER CHECK (landing_success IN (0,1)),   	-- Boolean: Was the landing successful
    landing_type TEXT CHECK (landing_type IN ('ASDS','RTLS','Ocean',-- Landing method
    'Other')),
    details TEXT,                                    				-- Launch details/summary
    FOREIGN KEY(rocket_id) REFERENCES rockets(id) ON DELETE CASCADE,
    FOREIGN KEY(launchpad_id) REFERENCES launchpads(id) ON DELETE CASCADE,
    FOREIGN KEY(landpad_id) REFERENCES landpads(id) ON DELETE SET NULL
);

CREATE TABLE launch_failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,    						-- Unique ID
    launch_id INTEGER NOT NULL,       								-- Foreign Key to 'launches'
    time INTEGER,                            						-- Time of failure in seconds since liftoff
    altitude INTEGER,                        						-- Altitude at failure in meters
    reason TEXT,                             						-- Reason or description of the failure
    FOREIGN KEY(launch_id) REFERENCES launches(id) ON DELETE CASCADE
);

-----------------------------------------------------------------------
-- 8. JUNCTION TABLES
-----------------------------------------------------------------------

-- Association Table: Payload <-> Customers
CREATE TABLE payload_customers (
	payload_id INTEGER NOT NULL,     								-- Foreign Key to 'payloads'
    customer_name TEXT NOT NULL,         							-- Customer name
    FOREIGN KEY(payload_id) REFERENCES payloads(id) ON DELETE CASCADE,
    PRIMARY KEY (payload_id, customer_name)
);

-- Association Table: Payload <-> NORAD id
CREATE TABLE payload_norad (
    payload_id INTEGER NOT NULL,     								-- Foreign Key to 'payloads'
    norad_id INTEGER NOT NULL,           							-- NORAD ID number
    PRIMARY KEY (payload_id, norad_id),			
    FOREIGN KEY(payload_id) REFERENCES payloads(id) ON DELETE CASCADE
);

-- Association Table: Launches <-> Payloads 
CREATE TABLE launch_payloads (
    launch_id INTEGER NOT NULL,   									-- Foreign Key to 'launches' 
    payload_id INTEGER NOT NULL,   									-- Foreign Key to 'payloads'
    PRIMARY KEY (launch_id, payload_id),
    FOREIGN KEY(launch_id) REFERENCES launches(id) ON DELETE CASCADE,
    FOREIGN KEY(payload_id) REFERENCES payloads(id) ON DELETE CASCADE
);

-- Association Table: Launches <-> crew 
CREATE TABLE launch_crew (
    launch_id INTEGER NOT NULL,   									-- Foreign Key to 'launches'
    crew_id INTEGER NOT NULL,         								-- Foreign Key to 'crew'
    role TEXT,                           							-- Crew member's role (e.g., 'Commander', 'Flight Engineer')
    PRIMARY KEY (launch_id, crew_id),
    FOREIGN KEY(launch_id) REFERENCES launches(id) ON DELETE CASCADE,
    FOREIGN KEY(crew_id) REFERENCES crew(id) ON DELETE CASCADE
);

-----------------------------------------------------------------------
-- 9. INDEXES
-----------------------------------------------------------------------
-- 1. AGENCIES
CREATE INDEX idx_agencies_country_id ON agencies (country_id);

-- 2. CREW
CREATE INDEX idx_crew_agency_id ON crew (agency_id);

-- 3. ROCKETS
CREATE INDEX idx_rockets_agency_id ON rockets (agency_id);

-- 5. LAUNCHPADS
CREATE INDEX idx_launchpads_agency_id ON launchpads (agency_id);

-- 7. LAUNCHES
CREATE INDEX idx_launches_rocket_id ON launches (rocket_id);
CREATE INDEX idx_launches_launchpad_id ON launches (launchpad_id);
CREATE INDEX idx_launches_landpad_id ON launches (landpad_id);
CREATE INDEX idx_launches_date_unix ON launches (date_unix);
CREATE INDEX idx_launches_upcoming ON launches (upcoming);

CREATE INDEX idx_launch_failures_launch_id ON launch_failures (launch_id);

-- PAYLOAD_CUSTOMERS
CREATE INDEX idx_payload_customers_customer_name ON payload_customers (customer_name);

-- PAYLOAD_NORAD
CREATE INDEX idx_payload_norad_norad_id ON payload_norad (norad_id);

-- LAUNCH_PAYLOADS
CREATE INDEX idx_launch_payloads_payload_id ON launch_payloads (payload_id);

-- LAUNCH_CREW
CREATE INDEX idx_launch_crew_crew_id ON launch_crew (crew_id);