"Biotoptypen (Flächen)"
from selenium import webdriver

from selenium.webdriver.common import keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver import ActionChains


fire = webdriver.Firefox()

fire.get('http://map1.naturschutz.rlp.de/kartendienste_naturschutz/index.php')

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/span").click()

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/div/ul/li[8]/span").click()

#####

fire.find_element_by_xpath(".//*[@id='menu']/li[3]/div/ul/li[8]/div/ul/li/span").click()

element = fire.find_element_by_xpath(".//*[@id='mod_export_layer']")

element.send_keys(unicode("Biotoptypen (Flächen)".decode("iso-8859-4")))

element = fire.find_element_by_xpath(".//*[@id='mod_export_format']")

element.send_keys("ESRI Shapefile")

element = fire.find_element_by_xpath(".//*[@id='coord_bbox_result']")

element.send_keys("1111, 2222, 3333, 4444")

fire.find_element_by_xpath(".//*[@id='exportWindow']/table/tbody/tr[5]/td/a").click()

fire.find_element_by_xpath(".//*[@id='mod_export_output']/strong/a").click()














