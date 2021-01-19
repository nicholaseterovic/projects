# Nicholas Eterovic 2020Q3
####################################################################################################

# Open-source miscellanous packages.
import sys as sy
import typing as tp
import pandas as pd
import logging as lg

# Open-source selenium packages.
import selenium.webdriver as wd
import selenium.webdriver.common.by as by
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as ec

####################################################################################################

def reserve_rcta_court(
    chrome:wd.Chrome,
    dtidx:pd.DatetimeIndex,
    url:str,
    fname:str,
    lname:str,
    email:str,
    logger:lg.Logger,
) -> bool:
    
    wait = ui.WebDriverWait(chrome, .5)
    
    try:
        logger.info(f'Attempting to connect to {url}')
        chrome.get(url)
        logger.info(f'Successfully connected to {url}')
    except Exception as exception:
        logger.error(f'Failed to connect to {url} with exception:{exception}')
        return False
    
    try:
        day = dtidx[0].strftime('%d')
        logger.info(f'Attempting to find and click on day {day}')
        wait.until(ec.element_to_be_clickable((by.By.PARTIAL_LINK_TEXT, day))).click()
        logger.info(f'Successfully clicked on day {day}')
    except Exception as exception:
        logger.error(f'Failed to click on date {day} with exception:\n{exception}')
        return False
    
    for dt in dtidx:
        try:
            time = dt.strftime('%I:%M %p')
            logger.info(f'Attempting to find and click on time {time}')
            wait.until(ec.element_to_be_clickable((by.By.PARTIAL_LINK_TEXT, time))).click()
            logger.info(f'Successfully clicked on time {time}')
        except Exception as exception:
            logger.warning(f'Failed to click on time {time} with exception:\n{exception}')
            continue
        
        try:
            logger.info(f'Attempting to find and click on court')
            wait.until(ec.invisibility_of_element_located((by.By.ID, 'primary-modal')))
            wait.until(ec.element_to_be_clickable((by.By.PARTIAL_LINK_TEXT, 'Court'))).click()
            logger.info(f'Successfully clicked on court')
        except Exception as exception:
            logger.error(f'Failed to click on court with exception:\n{exception}')
            return False
        
        try:
            logger.info(f'Attempting to complete court booking')
            wait.until(ec.presence_of_element_located((by.By.ID, 'first_name'))).send_keys(fname)
            wait.until(ec.presence_of_element_located((by.By.ID, 'last_name'))).send_keys(lname)
            wait.until(ec.presence_of_element_located((by.By.ID, 'email'))).send_keys(email)
            wait.until(ec.presence_of_element_located((by.By.XPATH, '//button[text()="Submit"]'))).click()
            logger.info(f'Successfully completed court booking')
            return True
        except Exception as exception:
            logger.error(f'Failed to complete court booking with exception:\n{exception}')
            return False
        
    return False

####################################################################################################

def main(**kwargs:dict) -> None:
    
    date = pd.Timestamp(kwargs.get('date', pd.Timestamp.now().normalize()+pd.Timedelta(days=1)))
    times = pd.TimedeltaIndex(str(kwargs['times']).split(sep=','))
    dtidx = date+times
    
    fname = str(kwargs['fname'])
    lname = str(kwargs['lname'])
    email = str(kwargs['email'])
    url = str(kwargs['url'])
    
    lg.basicConfig(stream=sy.stdout, level=lg.INFO)
    logger = lg.Logger(__name__)
    
    chrome = wd.Chrome(str(kwargs['driver_fpath']))
    chrome.maximize_window()
    
    reserved = False
    while not reserved:
        reserved = reserve_rcta_court(
            chrome=chrome,
            dtidx=dtidx,
            url=url,
            fname=fname,
            lname=lname,
            email=email,
            logger=logger,
        )
    chrome.quit()

####################################################################################################

if __name__=='__main__':
    kwargs = dict(a.lstrip('-').split(sep='=', maxsplit=1) for a in sy.argv if a.startswith('-') and '=' in a)
    main(**kwargs)