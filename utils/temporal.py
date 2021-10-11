# Nicholas Eterovic 2021Q4
####################################################################################################

# Open-source packages.
import typing as tp

####################################################################################################

def is_leap_year(YYYY:int) -> bool:
    if YYYY % 100 == 0:
        if YYYY % 400 == 0:
            return True
        return False
    if YYYY % 4 == 0:
        return True
    return False

def get_num_days_in_month(YYYY:int, MM:int) -> int:
    if MM==2:
        if is_leap_year(YYYY):
            return 29
        return 28
    if MM in [4, 6, 9, 11]:
        return 30
    return 31

def parse_date(YYYYMMDD:int) -> tp.Tuple[int, int, int]:
    DD = YYYYMMDD % 100
    MM = ((YYYYMMDD-DD) % 10000) // 100
    YYYY = (YYYYMMDD-100*MM-DD) // 10000
    return (YYYY, MM, DD)
    
def get_dates_between(sYYYYMMDD:int, eYYYYMMDD:int) -> tp.List[int]:
    sYYYY, sMM, sDD = parse_date(YYYYMMDD=sYYYYMMDD)
    eYYYY, eMM, eDD = parse_date(YYYYMMDD=eYYYYMMDD)
    return [
        10000*YYYY+100*MM+DD
        for YYYY in range(
            sYYYY,
            eYYYY+1,
        )
        for MM in range(
            sMM if YYYY==sYYYY else 1,
            (eMM if YYYY==eYYYY else 12)+1,
        )
        for DD in range(
            sDD if YYYY==sYYYY and MM==sMM else 1,
            (eDD if YYYY==eYYYY and MM==eMM else get_num_days_in_month(YYYY, MM))+1,
        )
    ]