#!/usr/bin/env python3
"""
Build ANZSCO -> SOC crosswalk via ISCO-08 triangulation.

Pipeline:
1. Load ANZSCO -> ISCO-08 (from ABS)
2. Load ISCO-08 -> SOC (we'll build this from Anthropic's SOC codes)
3. Triangulate: ANZSCO -> ISCO-08 -> SOC
"""

import pandas as pd
import json
from pathlib import Path

def load_anzsco_isco():
    """Load ABS ANZSCO to ISCO-08 concordance."""
    df = pd.read_csv('anzsco_to_isco08.csv')
    
    # Clean up - only keep 6-digit ANZSCO codes (unit level)
    df = df[df['anzsco_code'].str.len() == 6]
    df['isco08_code'] = df['isco08_code'].astype(str).str.replace('.0', '', regex=False)
    
    # Pad ISCO codes to 4 digits
    df['isco08_code'] = df['isco08_code'].str.zfill(4)
    
    print(f"ANZSCO->ISCO mappings: {len(df)}")
    print(f"Unique ANZSCO: {df['anzsco_code'].nunique()}")
    print(f"Unique ISCO: {df['isco08_code'].nunique()}")
    
    return df

def build_isco_soc_from_anthropic():
    """
    Build ISCO-08 to SOC mapping from Anthropic Economic Index data.
    
    Anthropic uses O*NET SOC codes. We'll reverse-engineer the mapping
    by looking at occupation titles and manually matching to ISCO-08.
    """
    # Known SOC -> ISCO-08 mappings (partial, for common occupations)
    # Source: BLS crosswalk documentation + manual review
    soc_to_isco = {
        # Management
        '11-1011': '1120',  # Chief Executives
        '11-1021': '1120',  # General and Operations Managers
        '11-2021': '1221',  # Marketing Managers
        '11-2022': '1221',  # Sales Managers
        '11-3011': '1211',  # Administrative Services Managers
        '11-3021': '1213',  # Computer and Information Systems Managers
        '11-3031': '1211',  # Financial Managers
        '11-3051': '1321',  # Industrial Production Managers
        '11-3061': '1324',  # Purchasing Managers
        '11-3071': '1330',  # Transportation, Storage Managers
        '11-3111': '1342',  # Compensation and Benefits Managers
        '11-3121': '1212',  # Human Resources Managers
        '11-9021': '1323',  # Construction Managers
        '11-9031': '1431',  # Education Administrators
        '11-9041': '1342',  # Architectural and Engineering Managers
        '11-9051': '1321',  # Food Service Managers
        '11-9111': '1343',  # Medical and Health Services Managers
        '11-9121': '1349',  # Natural Sciences Managers
        
        # Business & Financial
        '13-1111': '2423',  # Management Analysts
        '13-2011': '2411',  # Accountants and Auditors
        '13-2021': '2141',  # Property Appraisers
        '13-2031': '2413',  # Budget Analysts
        '13-2041': '2413',  # Credit Analysts
        '13-2051': '2413',  # Financial Analysts
        '13-2061': '2413',  # Financial Examiners
        '13-2071': '3312',  # Credit Counselors
        '13-2072': '3312',  # Loan Officers
        
        # Computer & Mathematical
        '15-1211': '2511',  # Computer Systems Analysts
        '15-1212': '2529',  # Information Security Analysts
        '15-1221': '2512',  # Computer and Information Research Scientists
        '15-1231': '2511',  # Computer Network Support Specialists
        '15-1232': '2523',  # Computer Network Architects
        '15-1241': '3511',  # Computer Network Administrators
        '15-1244': '3512',  # Network Technicians
        '15-1251': '2512',  # Computer Programmers
        '15-1252': '2512',  # Software Developers
        '15-1253': '2514',  # Software Quality Assurance
        '15-1254': '2513',  # Web Developers
        '15-1255': '2513',  # Web and Digital Interface Designers
        '15-1299': '2519',  # Computer Occupations, All Other
        '15-2011': '2120',  # Actuaries
        '15-2021': '2120',  # Mathematicians
        '15-2031': '2120',  # Operations Research Analysts
        '15-2041': '2111',  # Statisticians
        '15-2051': '2521',  # Data Scientists
        
        # Healthcare
        '29-1141': '2221',  # Registered Nurses
        '29-1171': '2212',  # Nurse Practitioners
        '29-1211': '2261',  # Anesthesiologists
        '29-1212': '2212',  # Cardiologists
        '29-1213': '2212',  # Dermatologists
        '29-1214': '2212',  # Emergency Medicine Physicians
        '29-1215': '2211',  # Family Medicine Physicians
        '29-1216': '2212',  # General Internal Medicine Physicians
        '29-1218': '2212',  # Obstetricians and Gynecologists
        '29-1221': '2211',  # Pediatricians, General
        '29-1222': '2212',  # Physicians, Pathologists
        '29-1223': '2212',  # Psychiatrists
        '29-1224': '2212',  # Radiologists
        '29-1229': '2212',  # Physicians, All Other
        '29-1241': '2212',  # Ophthalmologists
        '29-1031': '2261',  # Dietitians and Nutritionists
        '29-1051': '2262',  # Pharmacists
        '29-1122': '2267',  # Occupational Therapists
        '29-1123': '2264',  # Physical Therapists
        '29-1127': '2266',  # Speech-Language Pathologists
        
        # Education
        '25-1011': '2310',  # Business Teachers, Postsecondary
        '25-1021': '2310',  # Computer Science Teachers, Postsecondary
        '25-1022': '2310',  # Mathematical Science Teachers, Postsecondary
        '25-1031': '2310',  # Architecture Teachers, Postsecondary
        '25-1032': '2310',  # Engineering Teachers, Postsecondary
        '25-2011': '2341',  # Preschool Teachers
        '25-2012': '2341',  # Kindergarten Teachers
        '25-2021': '2341',  # Elementary School Teachers
        '25-2022': '2330',  # Middle School Teachers
        '25-2031': '2330',  # Secondary School Teachers
        '25-2052': '2359',  # Special Education Teachers
        '25-3011': '2352',  # Adult Education Teachers
        '25-3021': '2353',  # Self-Enrichment Teachers
        '25-3031': '2353',  # Substitute Teachers
        '25-9031': '2351',  # Instructional Coordinators
        
        # Legal
        '23-1011': '2611',  # Lawyers
        '23-1012': '2611',  # Judicial Law Clerks
        '23-1021': '2612',  # Administrative Law Judges
        '23-1022': '2612',  # Arbitrators, Mediators
        '23-1023': '2612',  # Judges, Magistrate Judges
        '23-2011': '2619',  # Paralegals and Legal Assistants
        
        # Architecture & Engineering
        '17-1011': '2161',  # Architects
        '17-2011': '2161',  # Aerospace Engineers
        '17-2021': '2143',  # Agricultural Engineers
        '17-2031': '2142',  # Bioengineers and Biomedical Engineers
        '17-2041': '2145',  # Chemical Engineers
        '17-2051': '2142',  # Civil Engineers
        '17-2061': '2144',  # Computer Hardware Engineers
        '17-2071': '2151',  # Electrical Engineers
        '17-2072': '2152',  # Electronics Engineers
        '17-2081': '2143',  # Environmental Engineers
        '17-2111': '2143',  # Health and Safety Engineers
        '17-2112': '2141',  # Industrial Engineers
        '17-2121': '2146',  # Marine Engineers
        '17-2131': '2149',  # Materials Engineers
        '17-2141': '2144',  # Mechanical Engineers
        '17-2151': '2146',  # Mining Engineers
        '17-2161': '2143',  # Nuclear Engineers
        '17-2171': '2146',  # Petroleum Engineers
        
        # Sales
        '41-1011': '5222',  # First-Line Supervisors of Retail Sales Workers
        '41-1012': '5222',  # First-Line Supervisors of Non-Retail Sales
        '41-2011': '5230',  # Cashiers
        '41-2021': '5223',  # Counter and Rental Clerks
        '41-2031': '5211',  # Retail Salespersons
        '41-3011': '3322',  # Advertising Sales Agents
        '41-3021': '3321',  # Insurance Sales Agents
        '41-3031': '3324',  # Securities Agents
        '41-4011': '3322',  # Sales Representatives, Technical
        '41-4012': '3322',  # Sales Representatives, Wholesale
        '41-9021': '3334',  # Real Estate Brokers
        '41-9022': '3334',  # Real Estate Sales Agents
        
        # Office & Administrative
        '43-1011': '3341',  # First-Line Supervisors, Office Workers
        '43-3011': '4311',  # Bill and Account Collectors
        '43-3021': '4311',  # Billing and Posting Clerks
        '43-3031': '4311',  # Bookkeeping, Accounting Clerks
        '43-3051': '4312',  # Payroll and Timekeeping Clerks
        '43-3061': '4312',  # Procurement Clerks
        '43-4011': '4226',  # Brokerage Clerks
        '43-4031': '4419',  # Court, Municipal, License Clerks
        '43-4041': '4131',  # Credit Authorizers
        '43-4051': '4225',  # Customer Service Representatives
        '43-4071': '4323',  # File Clerks
        '43-4081': '4323',  # Hotel, Motel Desk Clerks
        '43-4111': '4120',  # Interviewers
        '43-4121': '3354',  # Library Assistants
        '43-4131': '3312',  # Loan Interviewers
        '43-4141': '4312',  # New Accounts Clerks
        '43-4151': '4321',  # Order Clerks
        '43-4161': '4222',  # Human Resources Assistants
        '43-4171': '4222',  # Receptionists
        '43-4181': '4224',  # Reservation Agents
        '43-5011': '4412',  # Cargo and Freight Agents
        '43-5021': '4412',  # Couriers and Messengers
        '43-5031': '3431',  # Police, Fire Dispatchers
        '43-5032': '4223',  # Dispatchers (not police, fire)
        '43-5041': '4415',  # Meter Readers
        '43-5051': '4412',  # Postal Service Clerks
        '43-5052': '9621',  # Postal Service Mail Carriers
        '43-5053': '4412',  # Postal Service Mail Sorters
        '43-5061': '4321',  # Production Planning Clerks
        '43-5071': '4321',  # Shipping, Receiving Clerks
        '43-5111': '4321',  # Weighers, Measurers
        '43-6011': '4120',  # Executive Secretaries
        '43-6012': '3344',  # Legal Secretaries
        '43-6013': '3344',  # Medical Secretaries
        '43-6014': '4120',  # Secretaries
        '43-9011': '2423',  # Computer Operators
        '43-9021': '4132',  # Data Entry Keyers
        '43-9022': '4131',  # Word Processors
        '43-9031': '4110',  # Desktop Publishers
        '43-9041': '3321',  # Insurance Claims Clerks
        '43-9051': '4110',  # Mail Clerks
        '43-9061': '4110',  # Office Clerks, General
        '43-9071': '4110',  # Office Machine Operators
        '43-9081': '4415',  # Proofreaders
        '43-9111': '4312',  # Statistical Assistants
        
        # Food Preparation & Serving
        '35-1011': '5120',  # Chefs and Head Cooks
        '35-1012': '5120',  # First-Line Supervisors, Food Prep
        '35-2011': '5120',  # Cooks, Fast Food
        '35-2012': '5120',  # Cooks, Institution
        '35-2013': '5120',  # Cooks, Private Household
        '35-2014': '5120',  # Cooks, Restaurant
        '35-2015': '5120',  # Cooks, Short Order
        '35-2019': '5120',  # Cooks, All Other
        '35-2021': '9412',  # Food Preparation Workers
        '35-3011': '5132',  # Bartenders
        '35-3021': '5131',  # Combined Food Prep and Serving
        '35-3022': '5246',  # Counter Attendants
        '35-3031': '5131',  # Waiters and Waitresses
        '35-3041': '5131',  # Food Servers, Nonrestaurant
        '35-9011': '9412',  # Dining Room Attendants
        '35-9021': '9412',  # Dishwashers
        '35-9031': '5246',  # Hosts and Hostesses
        
        # Construction & Extraction
        '47-1011': '3123',  # First-Line Supervisors, Construction
        '47-2011': '7111',  # Boilermakers
        '47-2021': '7112',  # Brickmasons
        '47-2022': '7113',  # Stonemasons
        '47-2031': '7115',  # Carpenters
        '47-2041': '7124',  # Carpet Installers
        '47-2042': '7122',  # Floor Layers
        '47-2043': '7122',  # Floor Sanders
        '47-2044': '7123',  # Tile and Marble Setters
        '47-2051': '9313',  # Cement Masons
        '47-2053': '7114',  # Terrazzo Workers
        '47-2061': '7119',  # Construction Laborers
        '47-2071': '9312',  # Paving Equipment Operators
        '47-2072': '9312',  # Pile Driver Operators
        '47-2073': '8342',  # Operating Engineers
        '47-2081': '7126',  # Drywall Installers
        '47-2082': '7123',  # Tapers
        '47-2111': '7411',  # Electricians
        '47-2121': '7125',  # Glaziers
        '47-2131': '7127',  # Insulation Workers, Floor
        '47-2132': '7127',  # Insulation Workers, Mechanical
        '47-2141': '7131',  # Painters, Construction
        '47-2142': '7132',  # Paperhangers
        '47-2151': '7126',  # Pipelayers
        '47-2152': '7126',  # Plumbers
        '47-2161': '7133',  # Plasterers
        '47-2171': '7212',  # Reinforcing Iron and Rebar Workers
        '47-2181': '7214',  # Roofers
        '47-2211': '7213',  # Sheet Metal Workers
        '47-2221': '7214',  # Structural Iron Workers
        
        # Installation, Maintenance, Repair
        '49-1011': '3122',  # First-Line Supervisors, Mechanics
        '49-2011': '7421',  # Computer, ATM Repairers
        '49-2021': '7421',  # Radio, Cellular Equipment Installers
        '49-2022': '7421',  # Telecommunications Equipment Installers
        '49-2091': '7421',  # Avionics Technicians
        '49-2092': '7421',  # Electric Motor Repairers
        '49-2093': '7412',  # Electrical Equipment Repairers
        '49-2094': '7412',  # Electrical Repairers, Commercial
        '49-2095': '7412',  # Electrical Repairers, Powerhouse
        '49-2096': '7421',  # Electronic Equipment Installers
        '49-2097': '7421',  # Electronic Home Entertainment
        '49-2098': '7422',  # Security System Installers
        '49-3011': '7231',  # Aircraft Mechanics
        '49-3021': '7233',  # Automotive Body Repairers
        '49-3022': '7231',  # Automotive Glass Installers
        '49-3023': '7231',  # Automotive Service Technicians
        '49-3031': '7233',  # Bus and Truck Mechanics
        '49-3041': '7234',  # Farm Equipment Mechanics
        '49-3042': '7233',  # Mobile Heavy Equipment Mechanics
        '49-3043': '7234',  # Rail Car Repairers
        '49-3051': '7234',  # Motorboat Mechanics
        '49-3052': '7234',  # Motorcycle Mechanics
        '49-3053': '7234',  # Outdoor Power Equipment Mechanics
        '49-3091': '7234',  # Bicycle Repairers
        '49-3092': '7231',  # Recreational Vehicle Technicians
        '49-3093': '7233',  # Tire Repairers
        '49-9011': '7412',  # Mechanical Door Repairers
        '49-9012': '7412',  # Control and Valve Installers
        '49-9021': '7127',  # Heating, AC Mechanics
        '49-9031': '7233',  # Home Appliance Repairers
        '49-9041': '7233',  # Industrial Machinery Mechanics
        '49-9043': '7233',  # Maintenance Workers, Machinery
        '49-9044': '7233',  # Millwrights
        '49-9045': '8189',  # Refractory Repairers
        '49-9051': '7421',  # Electrical Line Installers
        '49-9052': '7421',  # Telecommunications Line Installers
        '49-9061': '7421',  # Camera Repairers
        '49-9062': '7311',  # Medical Equipment Repairers
        '49-9063': '7311',  # Musical Instrument Repairers
        '49-9064': '7311',  # Watch Repairers
        '49-9071': '7233',  # Maintenance Workers, General
        '49-9091': '7233',  # Coin Machine Servicers
        '49-9092': '7233',  # Commercial Divers
        '49-9094': '7311',  # Locksmiths
        '49-9095': '7421',  # Manufactured Building Installers
        '49-9096': '7233',  # Riggers
        '49-9097': '7421',  # Signal and Track Switch Repairers
        
        # Production
        '51-1011': '3122',  # First-Line Supervisors, Production
        '51-2011': '8211',  # Aircraft Structure Assemblers
        '51-2021': '7543',  # Coil Winders
        '51-2022': '7412',  # Electrical Equipment Assemblers
        '51-2023': '8219',  # Electromechanical Assemblers
        '51-2031': '8219',  # Engine Assemblers
        '51-2041': '8219',  # Structural Metal Fabricators
        '51-2051': '8219',  # Fiberglass Laminators
        '51-2091': '8219',  # Assemblers, Fabricators, All Other
        '51-2092': '8219',  # Team Assemblers
        '51-3011': '7512',  # Bakers
        '51-3021': '7513',  # Butchers
        '51-3022': '7513',  # Meat, Poultry Cutters
        '51-3023': '7513',  # Slaughterers and Meat Packers
        '51-3091': '7514',  # Food and Tobacco Roasting
        '51-3092': '7512',  # Food Batchmakers
        '51-3093': '8160',  # Food Cooking Machine Operators
        '51-4011': '7223',  # Computer Numerically Controlled Tool Operators
        '51-4012': '7223',  # CNC Tool Programmers
        '51-4021': '8121',  # Extruding Machine Operators
        '51-4022': '8122',  # Forging Machine Operators
        '51-4023': '8122',  # Rolling Machine Operators
        '51-4031': '7224',  # Cutting, Punching Machine Operators
        '51-4032': '8122',  # Drilling Machine Operators
        '51-4033': '7223',  # Grinding Machine Operators
        '51-4034': '7223',  # Lathe Operators
        '51-4035': '7223',  # Milling Machine Operators
        '51-4041': '7221',  # Machinists
        '51-4051': '8122',  # Metal-Refining Furnace Operators
        '51-4052': '8121',  # Pourers and Casters
        '51-4061': '7214',  # Model Makers, Metal
        '51-4062': '7222',  # Patternmakers, Metal
        '51-4071': '7214',  # Foundry Mold Makers
        '51-4072': '8121',  # Molding Machine Operators
        '51-4081': '8121',  # Multiple Machine Tool Operators
        '51-4111': '7222',  # Tool and Die Makers
        '51-4121': '7214',  # Welders
        '51-4122': '7212',  # Solderers and Brazers
        '51-4191': '8122',  # Heat Treating Equipment Operators
        '51-4192': '7222',  # Layout Workers
        '51-4193': '7224',  # Plating Machine Operators
        '51-4194': '7224',  # Tool Grinders
        
        # Transportation
        '53-1031': '8331',  # First-Line Supervisors, Transportation
        '53-1041': '3151',  # Aircraft Cargo Handling Supervisors
        '53-1042': '3152',  # First-Line Supervisors, Helpers
        '53-1043': '3153',  # First-Line Supervisors, Vehicle Operators
        '53-1044': '3154',  # First-Line Supervisors, Water Transportation
        '53-2011': '3153',  # Airline Pilots
        '53-2012': '3153',  # Commercial Pilots
        '53-2021': '3155',  # Air Traffic Controllers
        '53-2022': '3155',  # Airfield Operations Specialists
        '53-2031': '3155',  # Flight Attendants
        '53-3011': '8331',  # Ambulance Drivers
        '53-3021': '8331',  # Bus Drivers, Transit
        '53-3022': '8331',  # Bus Drivers, School
        '53-3031': '8322',  # Driver/Sales Workers
        '53-3032': '8332',  # Heavy and Tractor-Trailer Drivers
        '53-3033': '8332',  # Light Truck Drivers
        '53-3041': '8322',  # Taxi Drivers
        '53-3051': '8331',  # Motor Vehicle Operators, All Other
        '53-3052': '8331',  # Shuttle Drivers
        '53-3053': '8332',  # Shuttle Drivers
        '53-4011': '8311',  # Locomotive Engineers
        '53-4012': '8311',  # Locomotive Firers
        '53-4013': '8312',  # Rail Yard Engineers
        '53-4021': '8312',  # Railroad Brake Operators
        '53-4022': '8312',  # Railroad Conductors
        '53-4031': '8312',  # Railroad Signal Operators
        '53-4041': '8350',  # Subway and Streetcar Operators
        '53-4099': '8312',  # Rail Transportation Workers, All Other
        '53-5011': '3152',  # Sailors
        '53-5021': '3152',  # Captains
        '53-5022': '3152',  # Motorboat Operators
        '53-5031': '3152',  # Ship Engineers
        '53-6011': '8341',  # Bridge and Lock Tenders
        '53-6021': '8343',  # Parking Attendants
        '53-6031': '4323',  # Automotive Service Attendants
        '53-6041': '4323',  # Traffic Technicians
        '53-6051': '9621',  # Transportation Inspectors
        '53-6061': '9621',  # Transportation Attendants
        '53-7011': '8343',  # Conveyor Operators
        '53-7021': '8343',  # Crane Operators
        '53-7031': '8343',  # Dredge Operators
        '53-7032': '8342',  # Excavating Machine Operators
        '53-7033': '8342',  # Loading Machine Operators
        '53-7041': '9333',  # Hoist and Winch Operators
        '53-7051': '8344',  # Industrial Truck Operators
        '53-7061': '9621',  # Cleaners of Vehicles
        '53-7062': '9622',  # Laborers, Freight
        '53-7063': '9621',  # Machine Feeders
        '53-7064': '9621',  # Packers and Packagers
        '53-7065': '9623',  # Stockers and Order Fillers
        '53-7072': '9621',  # Pump Operators
        '53-7073': '9621',  # Wellhead Pumpers
        '53-7081': '9621',  # Refuse Collectors
        '53-7111': '9611',  # Mine Shuttle Car Operators
        '53-7121': '9621',  # Tank Car Loaders
        
        # Personal Care & Service
        '39-1011': '5151',  # Gaming Supervisors
        '39-1012': '5153',  # Slot Supervisors
        '39-1021': '5151',  # First-Line Supervisors, Personal Service
        '39-1022': '5151',  # First-Line Supervisors, Gaming
        '39-2011': '5113',  # Animal Trainers
        '39-2021': '5164',  # Animal Caretakers
        '39-3011': '5151',  # Gaming Dealers
        '39-3012': '5151',  # Gaming and Sports Book Writers
        '39-3019': '5151',  # Gaming Service Workers, All Other
        '39-3021': '3423',  # Motion Picture Projectionists
        '39-3031': '5163',  # Ushers, Lobby Attendants
        '39-3091': '5161',  # Amusement Attendants
        '39-3092': '5169',  # Costume Attendants
        '39-3093': '5169',  # Locker Room Attendants
        '39-4011': '5142',  # Embalmers
        '39-4012': '5142',  # Funeral Attendants
        '39-4021': '5142',  # Funeral Service Managers
        '39-4031': '5142',  # Morticians
        '39-5011': '5141',  # Barbers
        '39-5012': '5141',  # Hairdressers
        '39-5091': '5142',  # Makeup Artists
        '39-5092': '5142',  # Manicurists
        '39-5093': '5142',  # Shampooers
        '39-5094': '5142',  # Skincare Specialists
        '39-6011': '5311',  # Baggage Porters
        '39-6012': '5311',  # Concierges
        '39-7011': '5153',  # Tour Guides
        '39-7012': '5153',  # Travel Guides
        '39-9011': '5311',  # Childcare Workers
        '39-9021': '5322',  # Personal Care Aides
        '39-9031': '3423',  # Fitness Trainers
        '39-9032': '5169',  # Recreation Workers
        '39-9041': '5169',  # Residential Advisors
        
        # Cleaning & Building Services
        '37-1011': '5153',  # First-Line Supervisors, Housekeeping
        '37-1012': '5153',  # First-Line Supervisors, Landscaping
        '37-2011': '9412',  # Janitors and Cleaners
        '37-2012': '9112',  # Maids and Housekeeping Cleaners
        '37-2019': '9129',  # Building Cleaning Workers, All Other
        '37-2021': '9613',  # Pest Control Workers
        '37-3011': '9214',  # Landscaping and Groundskeeping Workers
        '37-3012': '9214',  # Pesticide Handlers
        '37-3013': '9214',  # Tree Trimmers
        
        # Protective Service
        '33-1011': '3355',  # First-Line Supervisors, Correctional Officers
        '33-1012': '3355',  # First-Line Supervisors, Police
        '33-1021': '3355',  # First-Line Supervisors, Fire Fighting
        '33-2011': '5411',  # Firefighters
        '33-2021': '5411',  # Fire Inspectors
        '33-2022': '5411',  # Forest Fire Inspectors
        '33-3011': '3351',  # Bailiffs
        '33-3012': '3351',  # Correctional Officers
        '33-3021': '3355',  # Detectives
        '33-3031': '5412',  # Fish and Game Wardens
        '33-3041': '5412',  # Parking Enforcement Workers
        '33-3051': '5412',  # Police and Sheriff's Patrol Officers
        '33-3052': '5413',  # Transit Police
        '33-9011': '5414',  # Animal Control Workers
        '33-9021': '5414',  # Private Detectives
        '33-9031': '5414',  # Gaming Surveillance Officers
        '33-9032': '5414',  # Security Guards
        '33-9091': '5419',  # Crossing Guards
        '33-9092': '5419',  # Lifeguards
        '33-9093': '5419',  # Transportation Security Screeners
        
        # Arts, Design, Entertainment, Sports, Media
        '27-1011': '2161',  # Art Directors
        '27-1012': '2651',  # Craft Artists
        '27-1013': '2651',  # Fine Artists
        '27-1014': '2651',  # Special Effects Artists
        '27-1019': '2659',  # Artists, All Other
        '27-1021': '2163',  # Commercial and Industrial Designers
        '27-1022': '2166',  # Fashion Designers
        '27-1023': '2163',  # Floral Designers
        '27-1024': '2166',  # Graphic Designers
        '27-1025': '2162',  # Interior Designers
        '27-1026': '2163',  # Merchandise Displayers
        '27-1027': '2163',  # Set and Exhibit Designers
        '27-1029': '2163',  # Designers, All Other
        '27-2011': '2652',  # Actors
        '27-2012': '2652',  # Producers and Directors
        '27-2021': '2652',  # Athletes and Sports Competitors
        '27-2022': '3421',  # Coaches and Scouts
        '27-2023': '3421',  # Umpires, Referees
        '27-2031': '2653',  # Dancers
        '27-2032': '2653',  # Choreographers
        '27-2041': '2652',  # Music Directors
        '27-2042': '2652',  # Musicians and Singers
        '27-3011': '2641',  # Broadcast Announcers
        '27-3012': '2656',  # Disc Jockeys
        '27-3021': '2642',  # Broadcast Technicians
        '27-3022': '2642',  # Reporters and Correspondents
        '27-3023': '2641',  # News Analysts
        '27-3031': '2643',  # Public Relations Specialists
        '27-3041': '2641',  # Editors
        '27-3042': '2641',  # Technical Writers
        '27-3043': '2641',  # Writers and Authors
        '27-3091': '2642',  # Interpreters and Translators
        '27-4011': '3521',  # Audio and Video Technicians
        '27-4012': '3521',  # Broadcast Technicians
        '27-4013': '3521',  # Radio Operators
        '27-4014': '3521',  # Sound Engineering Technicians
        '27-4021': '3431',  # Photographers
        '27-4031': '3521',  # Camera Operators, Television
        '27-4032': '3521',  # Film and Video Editors
    }
    
    # Build reverse mapping: ISCO-08 -> SOC
    isco_to_soc = {}
    for soc, isco in soc_to_isco.items():
        if isco not in isco_to_soc:
            isco_to_soc[isco] = []
        isco_to_soc[isco].append(soc)
    
    print(f"SOC->ISCO mappings: {len(soc_to_isco)}")
    print(f"Unique ISCO codes: {len(isco_to_soc)}")
    
    # Save as CSV
    rows = []
    for soc, isco in soc_to_isco.items():
        rows.append({'soc_code': soc, 'isco08_code': isco})
    
    df = pd.DataFrame(rows)
    df.to_csv('soc_to_isco08.csv', index=False)
    print("Saved soc_to_isco08.csv")
    
    return soc_to_isco, isco_to_soc

def triangulate_anzsco_to_soc(anzsco_isco_df, isco_to_soc):
    """
    Triangulate: ANZSCO -> ISCO-08 -> SOC
    """
    results = []
    
    for _, row in anzsco_isco_df.iterrows():
        anzsco = row['anzsco_code']
        isco = row['isco08_code']
        
        # Find matching SOC codes
        if isco in isco_to_soc:
            for soc in isco_to_soc[isco]:
                results.append({
                    'anzsco_code': anzsco,
                    'anzsco_title': row['anzsco_title'],
                    'isco08_code': isco,
                    'soc_code': soc,
                    'match_method': 'isco_triangulation'
                })
    
    df = pd.DataFrame(results)
    print(f"\nTriangulated mappings: {len(df)}")
    print(f"Unique ANZSCO with SOC match: {df['anzsco_code'].nunique()}")
    
    return df

def main():
    print("=== Building ISCO Crosswalk ===\n")
    
    # Step 1: Load ANZSCO->ISCO
    anzsco_isco = load_anzsco_isco()
    
    # Step 2: Build SOC->ISCO (manual mapping)
    soc_to_isco, isco_to_soc = build_isco_soc_from_anthropic()
    
    # Step 3: Triangulate
    triangulated = triangulate_anzsco_to_soc(anzsco_isco, isco_to_soc)
    
    # Save results
    triangulated.to_csv('anzsco_to_soc_via_isco.csv', index=False)
    print(f"\nSaved anzsco_to_soc_via_isco.csv")
    
    # Compare with existing fuzzy match
    existing = pd.read_csv('../pipeline/output/anzsco_onet_mapping.csv')
    print(f"\nComparison:")
    print(f"  Existing fuzzy match: {len(existing)} ANZSCO codes")
    print(f"  ISCO triangulation:   {triangulated['anzsco_code'].nunique()} ANZSCO codes")
    
    # Show sample improvements
    print("\nSample triangulated mappings:")
    print(triangulated[['anzsco_code', 'anzsco_title', 'soc_code']].head(20).to_string(index=False))

if __name__ == '__main__':
    main()
