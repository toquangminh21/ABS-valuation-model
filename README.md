# ABS-valuation-model
Small project to build a valuation model for an Asset-Backed Securities (ABS) using Python. 

The model is a bit slow because:
1) Python
2) I'm using dictionaries to keep track of the cash flows and waterfalls for each period - this may not be the optimal data structure to accomplish this
3) There are 1,500 Auto loans with the longest tenor being 71 months, and we're running 2,000 simulations: so there are 1500*71*2000 = 213,000,000 periods that we must process
4) No multiprocessing... yet (as of 3:38PM 6/21/20)

Also, the program can use a simple GUI as well. Feel free to open a pull requests (either via writing a new branch or forking the repository) if you feel you can help out with any of these aspects. Thank you!
