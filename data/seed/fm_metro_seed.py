"""Seed data for the Fargo-Moorhead metro area.

This seeds real, publicly available data for:
  - Moorhead, MN: City Council, School Board (ISD 152)
  - Fargo, ND: City Commission, School Board (Fargo Public Schools)
  - Clay County, MN: Board of Commissioners, Sheriff, Attorney, Auditor
  - Cass County, ND: Board of Commissioners, Sheriff, State's Attorney, Recorder
  - MN 7th Judicial District (Clay County judges)
  - ND East Central Judicial District (Cass County judges)
  - Clay County SWCD (Soil & Water Conservation District)
  - Cass County SCD (Soil Conservation District)
  - Fargo Park District
  - West Fargo Park District

All information sourced from official government websites and public records.
"""

import sys
from datetime import date
from pathlib import Path

# Allow running as a script from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from politibase.db.database import SessionLocal, init_db
from politibase.models.schema import (
    Candidate,
    Candidacy,
    DataSource,
    Election,
    Jurisdiction,
    Office,
)


def seed():
    init_db()
    session = SessionLocal()

    # ------------------------------------------------------------------
    # Jurisdictions
    # ------------------------------------------------------------------
    mn = Jurisdiction(name="Minnesota", jurisdiction_type="state", state="MN")
    nd = Jurisdiction(name="North Dakota", jurisdiction_type="state", state="ND")
    session.add_all([mn, nd])
    session.flush()

    moorhead = Jurisdiction(
        name="City of Moorhead", jurisdiction_type="city", state="MN", parent_id=mn.id
    )
    fargo = Jurisdiction(
        name="City of Fargo", jurisdiction_type="city", state="ND", parent_id=nd.id
    )
    clay_county = Jurisdiction(
        name="Clay County", jurisdiction_type="county", state="MN", parent_id=mn.id
    )
    cass_county = Jurisdiction(
        name="Cass County", jurisdiction_type="county", state="ND", parent_id=nd.id
    )
    moorhead_schools = Jurisdiction(
        name="Moorhead Area Public Schools (ISD 152)",
        jurisdiction_type="school_district",
        state="MN",
        parent_id=mn.id,
    )
    fargo_schools = Jurisdiction(
        name="Fargo Public Schools",
        jurisdiction_type="school_district",
        state="ND",
        parent_id=nd.id,
    )
    # Judicial districts
    mn_7th_judicial = Jurisdiction(
        name="Minnesota 7th Judicial District",
        jurisdiction_type="judicial_district",
        state="MN",
        parent_id=mn.id,
    )
    nd_ec_judicial = Jurisdiction(
        name="North Dakota East Central Judicial District",
        jurisdiction_type="judicial_district",
        state="ND",
        parent_id=nd.id,
    )
    # Soil & Water Conservation Districts
    clay_swcd = Jurisdiction(
        name="Clay County Soil & Water Conservation District",
        jurisdiction_type="conservation_district",
        state="MN",
        parent_id=mn.id,
    )
    cass_scd = Jurisdiction(
        name="Cass County Soil Conservation District",
        jurisdiction_type="conservation_district",
        state="ND",
        parent_id=nd.id,
    )
    # Park Districts
    fargo_parks = Jurisdiction(
        name="Fargo Park District",
        jurisdiction_type="park_district",
        state="ND",
        parent_id=nd.id,
    )
    wf_parks = Jurisdiction(
        name="West Fargo Park District",
        jurisdiction_type="park_district",
        state="ND",
        parent_id=nd.id,
    )
    session.add_all([
        moorhead, fargo, clay_county, cass_county, moorhead_schools, fargo_schools,
        mn_7th_judicial, nd_ec_judicial, clay_swcd, cass_scd, fargo_parks, wf_parks,
    ])
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Moorhead City Council
    # ------------------------------------------------------------------
    mhd_mayor = Office(
        jurisdiction_id=moorhead.id,
        title="Mayor",
        office_level="city",
        seats=1,
        term_length_years=4,
        is_partisan=False,
        description="Chief elected official of the City of Moorhead. Presides over City Council meetings.",
    )
    mhd_wards = []
    for ward in range(1, 5):
        for seat in ["A", "B"]:
            office = Office(
                jurisdiction_id=moorhead.id,
                title=f"Council Member Ward {ward} Seat {seat}",
                office_level="city",
                district=f"Ward {ward}",
                seats=1,
                term_length_years=4,
                is_partisan=False,
            )
            mhd_wards.append(office)
    session.add(mhd_mayor)
    session.add_all(mhd_wards)
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Fargo City Commission
    # ------------------------------------------------------------------
    fgo_mayor = Office(
        jurisdiction_id=fargo.id,
        title="Mayor",
        office_level="city",
        seats=1,
        term_length_years=4,
        is_partisan=False,
        description="Mayor of the City of Fargo. The Mayor and four Commissioners are elected at-large.",
    )
    fgo_commissioners = []
    for i in range(1, 5):
        office = Office(
            jurisdiction_id=fargo.id,
            title=f"City Commissioner Seat {i}",
            office_level="city",
            seats=1,
            term_length_years=4,
            is_partisan=False,
            description="Fargo commissioners are elected at-large and limited to three consecutive terms.",
        )
        fgo_commissioners.append(office)
    session.add(fgo_mayor)
    session.add_all(fgo_commissioners)
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Clay County Commission (5 districts)
    # ------------------------------------------------------------------
    clay_offices = []
    for d in range(1, 6):
        office = Office(
            jurisdiction_id=clay_county.id,
            title=f"County Commissioner District {d}",
            office_level="county",
            district=f"District {d}",
            seats=1,
            term_length_years=4,
            is_partisan=False,
        )
        clay_offices.append(office)
    session.add_all(clay_offices)
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Cass County Commission (5 districts)
    # ------------------------------------------------------------------
    cass_offices = []
    for d in range(1, 6):
        office = Office(
            jurisdiction_id=cass_county.id,
            title=f"County Commissioner District {d}",
            office_level="county",
            district=f"District {d}",
            seats=1,
            term_length_years=4,
            is_partisan=False,
        )
        cass_offices.append(office)
    session.add_all(cass_offices)
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Moorhead School Board (7 at-large seats)
    # ------------------------------------------------------------------
    mhd_school_seats = []
    for i in range(1, 8):
        office = Office(
            jurisdiction_id=moorhead_schools.id,
            title=f"School Board Member Seat {i}",
            office_level="school_board",
            seats=1,
            term_length_years=4,
            is_partisan=False,
        )
        mhd_school_seats.append(office)
    session.add_all(mhd_school_seats)
    session.flush()

    # ------------------------------------------------------------------
    # Offices — Fargo School Board (9 at-large seats)
    # ------------------------------------------------------------------
    fgo_school_seats = []
    for i in range(1, 10):
        office = Office(
            jurisdiction_id=fargo_schools.id,
            title=f"Board of Education Member Seat {i}",
            office_level="school_board",
            seats=1,
            term_length_years=4,
            is_partisan=False,
        )
        fgo_school_seats.append(office)
    session.add_all(fgo_school_seats)
    session.flush()

    # ------------------------------------------------------------------
    # Helper to create candidate + candidacy in one go
    # ------------------------------------------------------------------
    def add_incumbent(office, election, first, last, **kwargs):
        c = Candidate(
            first_name=first,
            last_name=last,
            residence_state=office.jurisdiction.state if office.jurisdiction else None,
            **kwargs,
        )
        session.add(c)
        session.flush()
        cy = Candidacy(
            candidate_id=c.id,
            election_id=election.id,
            status="winner",
            is_incumbent=True,
        )
        session.add(cy)
        return c

    # ------------------------------------------------------------------
    # Elections — create "current term" election placeholders
    # ------------------------------------------------------------------
    # Moorhead city elections (even years)
    mhd_2024 = Election(
        office_id=mhd_mayor.id,
        election_date=date(2024, 11, 5),
        election_type="general",
        description="Moorhead 2024 General Election",
    )
    mhd_2022 = Election(
        office_id=mhd_mayor.id,
        election_date=date(2022, 11, 8),
        election_type="general",
        description="Moorhead 2022 General Election",
    )
    session.add_all([mhd_2024, mhd_2022])
    session.flush()

    # Fargo city elections
    fgo_2024 = Election(
        office_id=fgo_mayor.id,
        election_date=date(2024, 6, 11),
        election_type="general",
        description="Fargo 2024 General Election",
    )
    fgo_2022 = Election(
        office_id=fgo_mayor.id,
        election_date=date(2022, 6, 14),
        election_type="general",
        description="Fargo 2022 General Election",
    )
    session.add_all([fgo_2024, fgo_2022])
    session.flush()

    # Clay County elections (even years, Nov)
    clay_2024 = Election(
        office_id=clay_offices[0].id,
        election_date=date(2024, 11, 5),
        election_type="general",
        description="Clay County 2024 General Election",
    )
    clay_2022 = Election(
        office_id=clay_offices[0].id,
        election_date=date(2022, 11, 8),
        election_type="general",
        description="Clay County 2022 General Election",
    )
    session.add_all([clay_2024, clay_2022])
    session.flush()

    # Cass County elections
    cass_2024 = Election(
        office_id=cass_offices[0].id,
        election_date=date(2024, 11, 5),
        election_type="general",
        description="Cass County 2024 General Election",
    )
    cass_2022 = Election(
        office_id=cass_offices[0].id,
        election_date=date(2022, 11, 8),
        election_type="general",
        description="Cass County 2022 General Election",
    )
    session.add_all([cass_2024, cass_2022])
    session.flush()

    # Moorhead school board elections (Nov, even years)
    mhd_school_2024 = Election(
        office_id=mhd_school_seats[0].id,
        election_date=date(2024, 11, 5),
        election_type="general",
        description="Moorhead School Board 2024 Election",
    )
    mhd_school_2022 = Election(
        office_id=mhd_school_seats[0].id,
        election_date=date(2022, 11, 8),
        election_type="general",
        description="Moorhead School Board 2022 Election",
    )
    session.add_all([mhd_school_2024, mhd_school_2022])
    session.flush()

    # Fargo school board elections (June, even years)
    fgo_school_2024 = Election(
        office_id=fgo_school_seats[0].id,
        election_date=date(2024, 6, 11),
        election_type="general",
        description="Fargo School Board 2024 Election",
    )
    fgo_school_2026 = Election(
        office_id=fgo_school_seats[0].id,
        election_date=date(2026, 6, 9),
        election_type="general",
        description="Fargo School Board 2026 Election — 5 seats up",
        filing_deadline=date(2026, 4, 6),
    )
    session.add_all([fgo_school_2024, fgo_school_2026])
    session.flush()

    # ------------------------------------------------------------------
    # Candidates — Moorhead City Council (current incumbents)
    # ------------------------------------------------------------------
    add_incumbent(
        mhd_mayor, mhd_2024,
        "Shelly", "Carlson",
        bio="Born and raised in Minot, ND. Came to Moorhead in 1990 to attend Moorhead State University. "
            "30-year career advocating on behalf of crime victims, specifically victims of domestic violence "
            "and sexual assault.",
        occupation="Nonprofit / Government Advocacy",
        education="Moorhead State University",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[0], mhd_2024,
        "Deb", "White",
        bio="Professor of Sociology at Minnesota State University Moorhead since 2000. "
            "Member of the Moorhead Planning Commission (2011-2015).",
        occupation="Professor of Sociology, MSUM",
        education="AAS Business Administration; BA Economics; PhD Sociology, University at Albany",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[1], mhd_2024,
        "Lisa", "Borgen",
        bio="Lifelong Moorhead resident. Clay County Attorney (1999-2006), District Court Judge (2006-2013), "
            "VP at American Crystal Sugar Company (2014-2024).",
        occupation="Attorney",
        education="Moorhead High School; MSU-Moorhead; UND School of Law",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[2], mhd_2024,
        "Chuck", "Hendrickson",
        bio="Employed at Koerber. Attends Trinity Lutheran Church in Moorhead.",
        occupation="Koerber",
        education="BA Political Science and English Writing, Concordia College; MBA, University of Mary",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[3], mhd_2024,
        "Sebastian", "McDougall",
        bio="Small business owner and consultant. Served on the City of Moorhead Park Advisory Board "
            "and the Public Service Commission.",
        occupation="Consultant / Small Business Owner",
        education="BS Exercise Science, NDSU",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[4], mhd_2024,
        "Nicole", "Mattson",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_wards[5], mhd_2024,
        "Ryan", "Nelson",
        residence_city="Moorhead",
    )

    # ------------------------------------------------------------------
    # Candidates — Fargo City Commission (current incumbents)
    # ------------------------------------------------------------------
    add_incumbent(
        fgo_mayor, fgo_2024,
        "Tim", "Mahoney",
        suffix="Dr.",
        bio="Mayor of Fargo. Presides over the five-member City Commission.",
        occupation="Mayor",
        residence_city="Fargo",
    )
    add_incumbent(
        fgo_commissioners[0], fgo_2024,
        "Denise", "Kolpack",
        bio="Deputy Mayor. Serves as the City Commission's liaison to the Water Utility.",
        occupation="Commissioner",
        residence_city="Fargo",
    )
    add_incumbent(
        fgo_commissioners[1], fgo_2022,
        "Dave", "Piepkorn",
        residence_city="Fargo",
    )
    add_incumbent(
        fgo_commissioners[2], fgo_2022,
        "John", "Strand",
        bio="Reappointed to the National League of Cities Human Development Federal Advocacy Committee "
            "for 2026, after serving as Vice Chair in 2025.",
        residence_city="Fargo",
    )
    add_incumbent(
        fgo_commissioners[3], fgo_2024,
        "Arlette", "Preston",
        residence_city="Fargo",
    )

    # ------------------------------------------------------------------
    # Candidates — Clay County Commissioners (current)
    # ------------------------------------------------------------------
    add_incumbent(
        clay_offices[0], clay_2024,
        "Paul", "Krabbenhoft",
        bio="Serving since 2021. Term expires January 2029.",
        residence_city="Moorhead",
    )
    add_incumbent(
        clay_offices[1], clay_2024,
        "Ezra", "Baer",
        bio="Serving since 2025. Ran for the open District 2 seat replacing retiring commissioner Frank Gross. "
            "District includes Dilworth, Felton, Georgetown, Glyndon, Hawley, Hitterdal, Ulen and 16 townships.",
        residence_city="Hawley",
    )
    add_incumbent(
        clay_offices[2], clay_2022,
        "Jenny", "Mongeau",
        bio="Serving since 2015. Term expires January 2027.",
    )
    add_incumbent(
        clay_offices[3], clay_2022,
        "Kevin", "Campbell",
        bio="Serving since 2003 — the longest-serving current Clay County commissioner. Term expires January 2027.",
    )
    add_incumbent(
        clay_offices[4], clay_2024,
        "David", "Ebinger",
        bio="Serving since 2025. Term expires January 2029.",
    )

    # ------------------------------------------------------------------
    # Candidates — Cass County Commissioners (current)
    # ------------------------------------------------------------------
    add_incumbent(
        cass_offices[0], cass_2024,
        "Tim", "Flakoll",
        bio="Former state senator. Ran unopposed for the District 1 seat. Sworn in December 3, 2024.",
        residence_city="Fargo",
    )
    add_incumbent(
        cass_offices[1], cass_2022,
        "Tony", "Grindberg",
        bio="Commission Chair (District 2). Succeeded Chad Peterson as chair.",
        residence_city="Fargo",
    )
    add_incumbent(
        cass_offices[2], cass_2022,
        "Jim", "Kapitan",
        bio="District 3 commissioner. Won reelection running unopposed.",
        residence_city="Fargo",
    )
    add_incumbent(
        cass_offices[3], cass_2022,
        "Duane", "Breitling",
        bio="District 4 commissioner.",
        residence_city="West Fargo",
    )
    add_incumbent(
        cass_offices[4], cass_2024,
        "Joel", "Vettel",
        bio="District 5 commissioner. Defeated challenger Keith Gohdes. 19-year Fargo police veteran, "
            "now with Sanford Health Foundation.",
        occupation="Sanford Health Foundation",
        residence_city="Fargo",
    )

    # ------------------------------------------------------------------
    # Candidates — Moorhead School Board (current)
    # ------------------------------------------------------------------
    add_incumbent(
        mhd_school_seats[0], mhd_school_2024,
        "Cassidy", "Bjorklund",
        bio="Served on the Moorhead school board since 2017. Lifelong Moorhead resident, parent of three.",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_school_seats[1], mhd_school_2024,
        "Scott", "Steffes",
        bio="Board Chair. Served since 2013. 30-year district resident. "
            "Retired deputy with the Clay County Sheriff's Office.",
        occupation="Retired Law Enforcement",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_school_seats[2], mhd_school_2024,
        "Melissa", "Burgard",
        bio="Served since 2017. Has served as treasurer and chair during her terms.",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_school_seats[3], mhd_school_2024,
        "Matt", "Valan",
        bio="Board member since 2013. Lives on a family farm south of Sabin. "
            "Lifelong district resident. Lutheran pastor at churches in Felton and Borup.",
        occupation="Lutheran Pastor",
        residence_city="Sabin",
    )
    add_incumbent(
        mhd_school_seats[4], mhd_school_2022,
        "Keith", "Vogt",
        bio="Re-elected in 2022.",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_school_seats[5], mhd_school_2022,
        "Lorilee", "Bergin",
        bio="Elected 2022. Elementary teacher in Fargo Public Schools for 12 years.",
        occupation="Elementary Teacher, Fargo Public Schools",
        residence_city="Moorhead",
    )
    add_incumbent(
        mhd_school_seats[6], mhd_school_2022,
        "David", "Marquardt",
        bio="Elected 2022. Taught in Fargo Public Schools for 21 years. "
            "Former Fargo Education Association president (5 years). Now with North Dakota United.",
        occupation="North Dakota United (Educators Union)",
        residence_city="Moorhead",
    )

    # ------------------------------------------------------------------
    # Candidates — Fargo School Board (current)
    # ------------------------------------------------------------------
    fgo_school_members = [
        ("Katie", "Christensen Mineer", "Board President"),
        ("Robin", "Nelson", "Vice President"),
        ("Melissa", "Burkland", None),
        ("Greg", "Clark", None),
        ("Nyamal", "Dei", None),
        ("Nikkie", "Gullickson", None),
        ("Jason", "Nelson", None),
        ("Kristin", "Nelson", None),
        ("Allie", "Ollenburger", None),
    ]
    for i, (first, last, role) in enumerate(fgo_school_members):
        # First 5 have terms expiring 2026 (elected 2022), last 4 expire 2028 (elected 2024)
        election = fgo_school_2024 if i >= 5 else fgo_school_2024
        bio = f"Fargo Public Schools Board of Education member."
        if role:
            bio = f"{role}. {bio}"
        add_incumbent(
            fgo_school_seats[i], election,
            first, last,
            bio=bio,
            residence_city="Fargo",
        )

    # ------------------------------------------------------------------
    # Upcoming Election — Fargo School Board 2026 (5 seats up)
    # ------------------------------------------------------------------
    # The five members whose terms expire in 2026:
    # Melissa Burkland, Katie Christensen Mineer, Greg Clark, Nyamal Dei, Robin Nelson
    # Filing deadline: April 6, 2026 at 4:00 PM
    # Election date: June 9, 2026
    # (The fgo_school_2026 election was already created above)

    # ==================================================================
    # NEW: County Elected Officials (non-commissioner)
    # ==================================================================

    # -- Clay County elected officials --
    clay_sheriff_office = Office(
        jurisdiction_id=clay_county.id, title="Sheriff", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Chief law enforcement officer of Clay County.",
    )
    clay_attorney_office = Office(
        jurisdiction_id=clay_county.id, title="County Attorney", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Chief prosecutor for Clay County. Prosecutes criminal cases and advises county agencies.",
    )
    clay_auditor_office = Office(
        jurisdiction_id=clay_county.id, title="County Auditor-Treasurer", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Manages county finances, elections, and tax collection.",
    )
    clay_recorder_office = Office(
        jurisdiction_id=clay_county.id, title="County Recorder", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Custodian of real estate records, vital records, and marriage licenses.",
    )
    session.add_all([clay_sheriff_office, clay_attorney_office, clay_auditor_office, clay_recorder_office])
    session.flush()

    clay_county_officials_2022 = Election(
        office_id=clay_sheriff_office.id, election_date=date(2022, 11, 8),
        election_type="general", description="Clay County 2022 General — County Officials",
    )
    session.add(clay_county_officials_2022)
    session.flush()

    add_incumbent(clay_sheriff_office, clay_county_officials_2022,
        "Mark", "Empting",
        bio="Elected Sheriff in 2018. Started with the Sheriff's Office in 2001 as a part-time deputy. "
            "Assignments include Field Training Officer, Emergency Vehicle Operations Instructor, "
            "Sergeant in Patrol Division, and Patrol Division Commander.",
        occupation="Sheriff",
        residence_city="Moorhead",
    )
    add_incumbent(clay_attorney_office, clay_county_officials_2022,
        "Brian", "Melton",
        bio="Clay County Attorney. Prosecutes adult criminal and juvenile cases.",
        occupation="County Attorney",
        residence_city="Moorhead",
    )
    add_incumbent(clay_auditor_office, clay_county_officials_2022,
        "Lori", "Johnson",
        suffix="J.",
        bio="With the Auditor's Office since 1987. Graduated from Concordia College (BA, 1983), "
            "CPA. Worked for the State Auditor's Office before joining Clay County as Financial Manager "
            "in 1987. Became County Auditor in 1997. Also serves as the county election official.",
        occupation="County Auditor-Treasurer",
        education="BA, Concordia College; CPA",
        residence_city="Moorhead",
    )

    # -- Cass County elected officials --
    cass_sheriff_office = Office(
        jurisdiction_id=cass_county.id, title="Sheriff", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Chief law enforcement officer of Cass County.",
    )
    cass_sa_office = Office(
        jurisdiction_id=cass_county.id, title="State's Attorney", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
        description="Prosecutes felonies, misdemeanors, and traffic offenses committed in Cass County.",
    )
    cass_recorder_office = Office(
        jurisdiction_id=cass_county.id, title="County Recorder", office_level="county",
        seats=1, term_length_years=4, is_partisan=False,
    )
    session.add_all([cass_sheriff_office, cass_sa_office, cass_recorder_office])
    session.flush()

    cass_county_officials_2022 = Election(
        office_id=cass_sheriff_office.id, election_date=date(2022, 11, 8),
        election_type="general", description="Cass County 2022 General — County Officials",
    )
    session.add(cass_county_officials_2022)
    session.flush()

    add_incumbent(cass_sheriff_office, cass_county_officials_2022,
        "Jesse", "Jahner",
        bio="Cass County Sheriff. Office located at the Cass County Law Enforcement Center, "
            "1612 23rd Ave N, Fargo.",
        occupation="Sheriff",
        residence_city="Fargo",
    )
    add_incumbent(cass_sa_office, cass_county_officials_2022,
        "Birch", "Burdick",
        bio="Cass County State's Attorney. Responsible for prosecuting felonies, misdemeanors, "
            "and traffic offenses not handled by Fargo/West Fargo city prosecutors.",
        occupation="State's Attorney",
        residence_city="Fargo",
    )
    add_incumbent(cass_recorder_office, cass_county_officials_2022,
        "Deb", "Moeller",
        occupation="County Recorder",
        residence_city="Fargo",
    )

    # ==================================================================
    # NEW: Judicial Elections
    # ==================================================================

    # -- Minnesota 7th Judicial District (Clay County judges, chambered in Moorhead) --
    mn_judge_offices = []
    mn_judge_names = [
        ("Steven", "Cahill", "Appointed 2006, elected 2008. Long-serving Clay County district judge."),
        ("Michelle", "Winkis Lawson", "Appointed by Governor Dayton in October 2012."),
        ("Leah", "duCharme", "Appointed by Governor Walz. Replaced Judge Amber B. Gustafson. Chambered in Moorhead."),
        ("Michael", "Leeser", "Appointed by Governor Walz in 2024. Former Clay County assistant county attorney. "
                              "Replaced Judge Greta M. Smolnisky. Chambered in Moorhead, Clay County Courthouse."),
    ]
    for i, (first, last, bio) in enumerate(mn_judge_names):
        office = Office(
            jurisdiction_id=mn_7th_judicial.id,
            title=f"District Court Judge Seat {i + 1} (Clay County)",
            office_level="judicial",
            seats=1, term_length_years=6, is_partisan=False,
            description="Minnesota district court judges serve 6-year terms and run in nonpartisan elections.",
        )
        mn_judge_offices.append(office)
    session.add_all(mn_judge_offices)
    session.flush()

    mn_judicial_2024 = Election(
        office_id=mn_judge_offices[0].id, election_date=date(2024, 11, 5),
        election_type="general",
        description="Minnesota 2024 General — 7th Judicial District",
    )
    session.add(mn_judicial_2024)
    session.flush()

    for i, (first, last, bio) in enumerate(mn_judge_names):
        add_incumbent(mn_judge_offices[i], mn_judicial_2024, first, last,
            bio=bio, occupation="District Court Judge", residence_city="Moorhead",
        )

    # -- North Dakota East Central Judicial District (Cass County judges) --
    nd_judge_offices = []
    nd_judge_data = [
        {"first": "Steven", "last": "McCullough", "suffix": "E.",
         "bio": "Presiding Judge, East Central Judicial District."},
        {"first": "Susan", "last": "Bailey",
         "bio": "Elected as District Court Judge in 2014 for judgeship #1. Chambered in Fargo."},
        {"first": "Reid", "last": "Brady", "suffix": "A.",
         "bio": "East Central Judicial District judge."},
        {"first": "Cherie", "last": "Clark", "suffix": "L.",
         "bio": "Appointed by Governor Burgum to a newly created judgeship (HB 1002)."},
        {"first": "Constance", "last": "Cleveland", "suffix": "L.",
         "bio": "East Central Judicial District judge."},
        {"first": "Stephanie", "last": "Hayden",
         "bio": "Appointed by Governor Burgum. Formerly a Judicial Referee in the district."},
        {"first": "Stephannie", "last": "Stiel", "suffix": "N.",
         "bio": "East Central Judicial District judge."},
        {"first": "Ryan", "last": "Younggren", "suffix": "J.",
         "bio": "Investiture held March 7, 2025 at the Cass County Courthouse in Fargo."},
        {"first": "Scott", "last": "Diamond", "suffix": "O.",
         "bio": "Appointed as District Court Judge in 2026."},
    ]
    for i, j in enumerate(nd_judge_data):
        office = Office(
            jurisdiction_id=nd_ec_judicial.id,
            title=f"District Court Judge Seat {i + 1}",
            office_level="judicial",
            seats=1, term_length_years=6, is_partisan=False,
            description="North Dakota district court judges serve 6-year terms in nonpartisan elections.",
        )
        nd_judge_offices.append(office)
    session.add_all(nd_judge_offices)
    session.flush()

    nd_judicial_2024 = Election(
        office_id=nd_judge_offices[0].id, election_date=date(2024, 11, 5),
        election_type="general",
        description="North Dakota 2024 General — East Central Judicial District",
    )
    session.add(nd_judicial_2024)
    session.flush()

    for i, j in enumerate(nd_judge_data):
        kwargs = {"bio": j["bio"], "occupation": "District Court Judge", "residence_city": "Fargo"}
        if "suffix" in j:
            kwargs["suffix"] = j["suffix"]
        add_incumbent(nd_judge_offices[i], nd_judicial_2024, j["first"], j["last"], **kwargs)

    # ==================================================================
    # NEW: Soil & Water Conservation Districts
    # ==================================================================

    # -- Clay County SWCD (5 elected supervisors, 4-year terms) --
    clay_swcd_offices = []
    for d in range(1, 6):
        office = Office(
            jurisdiction_id=clay_swcd.id,
            title=f"SWCD Supervisor District {d}",
            office_level="conservation_district",
            district=f"District {d}",
            seats=1, term_length_years=4, is_partisan=False,
            description="Elected supervisor for Clay County Soil & Water Conservation District. "
                        "Supervisors establish policy for soil and water conservation programs. "
                        "Compensated per meeting; $20 filing fee.",
        )
        clay_swcd_offices.append(office)
    session.add_all(clay_swcd_offices)
    session.flush()

    clay_swcd_2024 = Election(
        office_id=clay_swcd_offices[0].id, election_date=date(2024, 11, 5),
        election_type="general",
        description="Clay County SWCD 2024 Supervisor Election — Districts 1, 2, and 5",
    )
    session.add(clay_swcd_2024)
    session.flush()

    clay_swcd_members = [
        ("Joel", "Hildebrandt", "Chair of the Clay SWCD Board."),
        ("Robert", "Anderson", "Reporter for the SWCD Board."),
        ("Randy", "Schellack", "Secretary of the SWCD Board."),
        ("Carol", "Schoff", "Treasurer of the SWCD Board."),
    ]
    for i, (first, last, bio) in enumerate(clay_swcd_members):
        add_incumbent(clay_swcd_offices[i], clay_swcd_2024, first, last,
            bio=bio, residence_city="Moorhead",
        )

    # -- Cass County SCD (3 elected + 2 appointed supervisors, 6-year terms for elected) --
    cass_scd_offices = []
    for i in range(1, 4):
        office = Office(
            jurisdiction_id=cass_scd.id,
            title=f"Soil Conservation Supervisor Seat {i} (Elected)",
            office_level="conservation_district",
            seats=1, term_length_years=6, is_partisan=False,
            description="Elected supervisor for Cass County Soil Conservation District. "
                        "Approximate $60 stipend per meeting plus mileage reimbursement.",
        )
        cass_scd_offices.append(office)
    session.add_all(cass_scd_offices)
    session.flush()

    cass_scd_2022 = Election(
        office_id=cass_scd_offices[0].id, election_date=date(2022, 11, 8),
        election_type="general",
        description="Cass County SCD 2022 Supervisor Election",
    )
    session.add(cass_scd_2022)
    session.flush()

    cass_scd_members = [
        ("Terry", "Hoffmann", "Vice Chairman. Runs the family farm near Wheatland."),
        ("Warren", "Solberg", "Filled the remaining term left by retired supervisor Curt Knutson."),
        ("Brad", "Kellerman", "Elected supervisor."),
    ]
    for i, (first, last, bio) in enumerate(cass_scd_members):
        add_incumbent(cass_scd_offices[i], cass_scd_2022, first, last,
            bio=bio, residence_city="Fargo",
        )

    # ==================================================================
    # NEW: Park Districts
    # ==================================================================

    # -- Fargo Park District (5 at-large commissioners, 4-year terms, no term limits) --
    fgo_park_offices = []
    for i in range(1, 6):
        office = Office(
            jurisdiction_id=fargo_parks.id,
            title=f"Park Board Commissioner Seat {i}",
            office_level="park_district",
            seats=1, term_length_years=4, is_partisan=False,
            description="Fargo Park District commissioners are elected at-large with no term limits. "
                        "The board meets the second Tuesday of each month at 5:30 PM.",
        )
        fgo_park_offices.append(office)
    session.add_all(fgo_park_offices)
    session.flush()

    fgo_park_2024 = Election(
        office_id=fgo_park_offices[0].id, election_date=date(2024, 6, 11),
        election_type="general",
        description="Fargo Park District 2024 Election",
    )
    fgo_park_2022 = Election(
        office_id=fgo_park_offices[0].id, election_date=date(2022, 6, 14),
        election_type="general",
        description="Fargo Park District 2022 Election",
    )
    fgo_park_2026 = Election(
        office_id=fgo_park_offices[0].id, election_date=date(2026, 6, 9),
        election_type="general",
        description="Fargo Park District 2026 Election — Dawson and Deutsch running for reelection",
        filing_deadline=date(2026, 4, 6),
    )
    session.add_all([fgo_park_2024, fgo_park_2022, fgo_park_2026])
    session.flush()

    fgo_park_members = [
        ("Joe", "Deutsch", fgo_park_2022,
         "Board President. Reelected for his fifth term in 2022, first joining in 2006. "
         "Professor at NDSU preparing Physical Education Teachers, Coaches, and Recreation Specialists."),
        ("Vicki", "Dawson", fgo_park_2022,
         "Reelected for her second term in 2022, first joining in 2018. "
         "Senior Risk Consultant for Federated Insurance. Former Board President."),
        ("Aaron", "Hill", fgo_park_2022,
         "Board Vice President. Elected to his first term in 2022. "
         "Co-founder of Fargo Brewing Company. Lives in north Fargo."),
        ("Jerry", "Rostad", fgo_park_2024,
         "Re-elected in June 2024, originally joining the Board in 2016. "
         "VP for Strategic Engagement for the North Dakota University System."),
        ("Zoé", "Absey", fgo_park_2024,
         "Elected to her first term in June 2024."),
    ]
    for i, (first, last, election, bio) in enumerate(fgo_park_members):
        add_incumbent(fgo_park_offices[i], election, first, last,
            bio=bio, residence_city="Fargo",
        )

    # -- West Fargo Park District (5 at-large, 4-year terms) --
    wf_park_offices = []
    for i in range(1, 6):
        office = Office(
            jurisdiction_id=wf_parks.id,
            title=f"Park Board Commissioner Seat {i}",
            office_level="park_district",
            seats=1, term_length_years=4, is_partisan=False,
            description="West Fargo Park District commissioners. Board meets the second Wednesday "
                        "of every month at 5:30 PM at Rustad Recreation Center.",
        )
        wf_park_offices.append(office)
    session.add_all(wf_park_offices)
    session.flush()

    wf_park_2024 = Election(
        office_id=wf_park_offices[0].id, election_date=date(2024, 6, 11),
        election_type="general",
        description="West Fargo Park District 2024 Election",
    )
    wf_park_2026 = Election(
        office_id=wf_park_offices[0].id, election_date=date(2026, 6, 9),
        election_type="general",
        description="West Fargo Park District 2026 Election — Lauritsen, McCracken, Heise seats up",
        filing_deadline=date(2026, 4, 6),
    )
    session.add_all([wf_park_2024, wf_park_2026])
    session.flush()

    wf_park_members = [
        ("Jake", "Lauritsen", "Board President. Seat up for reelection in 2026."),
        ("Jeff", "McCracken", "Vice President. Seat up for reelection in 2026."),
        ("Chris", "Heise", "Seat up for reelection in 2026."),
    ]
    for i, (first, last, bio) in enumerate(wf_park_members):
        add_incumbent(wf_park_offices[i], wf_park_2024, first, last,
            bio=bio, residence_city="West Fargo",
        )

    # ------------------------------------------------------------------
    # Data Sources — record provenance
    # ------------------------------------------------------------------
    sources = [
        DataSource(
            source_name="City of Moorhead Official Website",
            source_url="https://www.cityofmoorhead.com/government/mayor-city-council/my-council-members",
            source_type="official",
        ),
        DataSource(
            source_name="City of Fargo Official Website",
            source_url="https://fargond.gov/city-government/departments/city-commission/members",
            source_type="official",
        ),
        DataSource(
            source_name="Clay County Official Website",
            source_url="https://claycountymn.gov/132/Board-of-Commissioners",
            source_type="official",
        ),
        DataSource(
            source_name="Cass County Official Website",
            source_url="https://www.casscountynd.gov/departments/county-commission",
            source_type="official",
        ),
        DataSource(
            source_name="Moorhead Area Public Schools",
            source_url="https://www.moorheadschools.org/apptegy/about/school-board/",
            source_type="official",
        ),
        DataSource(
            source_name="Fargo Public Schools Board of Education",
            source_url="https://www.fargo.k12.nd.us/boardmembers",
            source_type="official",
        ),
        DataSource(
            source_name="Ballotpedia — Moorhead, Minnesota",
            source_url="https://ballotpedia.org/Moorhead,_Minnesota",
            source_type="api",
        ),
        DataSource(
            source_name="Ballotpedia — Fargo, North Dakota",
            source_url="https://ballotpedia.org/Fargo,_North_Dakota",
            source_type="api",
        ),
        DataSource(
            source_name="InForum News",
            source_url="https://www.inforum.com",
            source_type="news",
        ),
        DataSource(
            source_name="MN Courts — 7th Judicial District",
            source_url="https://www.mncourts.gov/About-The-Courts/Overview/JudicialDirectory.aspx?d=7",
            source_type="official",
        ),
        DataSource(
            source_name="ND Courts — East Central Judicial District",
            source_url="https://www.ndcourts.gov/districts/east-central-judicial-district",
            source_type="official",
        ),
        DataSource(
            source_name="Clay County SWCD",
            source_url="https://claycountymn.gov/272/Soil-Water-Conservation-District",
            source_type="official",
        ),
        DataSource(
            source_name="Cass County Soil Conservation District",
            source_url="https://cassscd.org/",
            source_type="official",
        ),
        DataSource(
            source_name="Fargo Park District",
            source_url="https://www.fargoparks.com/park-board",
            source_type="official",
        ),
        DataSource(
            source_name="West Fargo Park District",
            source_url="https://wfparks.org/wf-parks-board/",
            source_type="official",
        ),
        DataSource(
            source_name="Clay County Elected Officials",
            source_url="https://claycountymn.gov/276/Elected-Officials",
            source_type="official",
        ),
        DataSource(
            source_name="Cass County Elected Officials",
            source_url="https://www.casscountynd.gov/our-county/finance-office/elections/elected-officials-in-cass-county",
            source_type="official",
        ),
    ]
    session.add_all(sources)

    session.commit()

    # Print summary
    print("=== Politibase FM Metro Seed Complete ===")
    print(f"  Jurisdictions: {session.query(Jurisdiction).count()}")
    print(f"  Offices:       {session.query(Office).count()}")
    print(f"  Elections:     {session.query(Election).count()}")
    print(f"  Candidates:    {session.query(Candidate).count()}")
    print(f"  Candidacies:   {session.query(Candidacy).count()}")
    print(f"  Data Sources:  {session.query(DataSource).count()}")

    session.close()


if __name__ == "__main__":
    seed()
