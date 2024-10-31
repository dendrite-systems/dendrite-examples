from dendrite import Dendrite
from dotenv import load_dotenv

load_dotenv()

browser = Dendrite()

# Open multiple URLs in new tabs
tab1 = browser.new_tab("https://www.example.com")
tab2 = browser.new_tab("https://www.example.com")

tab1.click("the more information link")
md = tab1.markdown()
print(md)

text = tab2.extract("the header text")
print(text)
