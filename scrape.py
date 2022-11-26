from selenium import webdriver
from selenium.webdriver.common.by import By

from datetime import datetime
from time import perf_counter
import os
import asyncio

from link import LINK, EXEC_PATH, ELEM_CLASS

driver = webdriver.Chrome(executable_path=EXEC_PATH)


async def get_occupancy(link: str) -> str:
    """Returns the occupancy number on the site"""
    t1 = perf_counter()
    driver.get(link)
    await asyncio.sleep(0.9-(perf_counter()-t1)) # makes sure that the driver.get + sleep is constant
    t1 = perf_counter()
    element = driver.find_element(By.CLASS_NAME, value=ELEM_CLASS)
    text = element.text
    t2 = perf_counter()
    if t2 - t1 < 0.1:
        await asyncio.sleep(0.1 - t2 + t1) # same for getting text from the element
    return text

async def main_loop() -> None:
    file_exists = os.path.exists("occupancy_2.csv")

    with open("occupancy_2.csv", mode="a+") as f:
        if not file_exists:
            f.write(f"occupancy_max,occupancy,datetime\n")

        request_stamp = datetime.now()
        get_occupancy_task = asyncio.create_task(get_occupancy(LINK))
        occupancy_data = await get_occupancy_task

        while True:

            get_occupancy_task = asyncio.create_task(get_occupancy(LINK)) # loads next link while appending the previous one

            try: # i dont know, what happens on the site after midnight :D 
                occupancy_data = occupancy_data.split()
            except (IndexError, TypeError): # this is raised, if the text is different from "occupancy / occupancy_max"
                occupancy_data = "None"

            occupancy_max, occupancy = occupancy_data[0], occupancy_data[2]
            f.write(f"{occupancy_max},{occupancy},{request_stamp}\n")

            occupancy_data = await get_occupancy_task
            request_stamp = datetime.now()
            
if __name__ == "__main__":
    asyncio.run(main_loop())


